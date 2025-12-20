from __future__ import annotations

import json
import logging
import os
import sys
import glob
import sqlite3
from datetime import datetime, timezone

from flask import g, has_request_context
from apscheduler.schedulers.background import BackgroundScheduler
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_caching import Cache
try:
    from flask_compress import Compress
except ImportError:
    class Compress:
        def __init__(self, *args, **kwargs):
            pass
        def init_app(self, app):
            pass
from sqlalchemy import event, func
from sqlalchemy.engine import Engine

try:
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
except Exception:
    pdfmetrics = None
    TTFont = None

try:
    from colorama import init as colorama_init, Fore, Style
    colorama_init(autoreset=True)
except Exception:
    class _Fore:
        BLUE = ""; GREEN = ""; YELLOW = ""; RED = ""
    class _Style:
        BRIGHT = ""; RESET_ALL = ""
    Fore, Style = _Fore(), _Style()
    def colorama_init(*args, **kwargs):
        return

try:
    import sentry_sdk
    from sentry_sdk.integrations.flask import FlaskIntegration
    from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
except Exception:
    sentry_sdk = None


class RequestIdFilter(logging.Filter):
    def filter(self, record):
        if has_request_context():
            record.request_id = getattr(g, "request_id", "-")
        else:
            record.request_id = "-"
        return True


class GLibWarningFilter(logging.Filter):
    def filter(self, record):
        msg = str(record.getMessage())
        if any(keyword in msg for keyword in ["GLib-GIO", "Clipchamp", "UWP app", "GIO-WARNING"]):
            return False
        return True


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        base = {
            "ts": datetime.now(timezone.utc).isoformat(timespec="milliseconds") + "Z",
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
            "request_id": getattr(record, "request_id", "-"),
        }
        for k, v in record.__dict__.items():
            if k.startswith("_"):
                continue
            if k in (
                "name","msg","args","levelname","levelno","pathname","filename",
                "module","exc_info","exc_text","stack_info","lineno","funcName",
                "created","msecs","relativeCreated","thread","threadName",
                "processName","process","request_id"
            ):
                continue
            try:
                json.dumps({k: v})
                base[k] = v
            except Exception:
                base[k] = str(v)
        if record.exc_info:
            base["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(base, ensure_ascii=False)


class ColorFormatter(logging.Formatter):
    COLORS = {
        "DEBUG":   Fore.BLUE,
        "INFO":    Fore.GREEN,
        "WARNING": Fore.YELLOW,
        "ERROR":   Fore.RED,
        "CRITICAL": Fore.RED + Style.BRIGHT,
    }

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, "")
        reset = Style.RESET_ALL
        req_id = getattr(record, "request_id", "-")
        base = f"[{self.formatTime(record, '%Y-%m-%d %H:%M:%S')}] {color}{record.levelname}{reset} {req_id} {record.name}: {record.getMessage()}"
        if record.exc_info:
            base += "\n" + self.formatException(record.exc_info)
        return base


def setup_logging(app):
    level_name = app.config.get("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    out_handler = logging.StreamHandler(sys.stdout)
    out_handler.setLevel(level)
    out_handler.addFilter(RequestIdFilter())
    out_handler.addFilter(GLibWarningFilter())
    out_handler.setFormatter(JSONFormatter() if app.config.get("JSON_LOGS") else ColorFormatter())

    err_handler = logging.StreamHandler(sys.stderr)
    err_handler.setLevel(logging.ERROR)
    err_handler.addFilter(RequestIdFilter())
    err_handler.addFilter(GLibWarningFilter())
    err_handler.setFormatter(JSONFormatter() if app.config.get("JSON_LOGS") else ColorFormatter())

    for lg in (app.logger, logging.getLogger(), logging.getLogger("sqlalchemy.engine")):
        lg.handlers.clear()
        lg.setLevel(level)
        lg.addHandler(out_handler)
        lg.addHandler(err_handler)
        lg.propagate = False

    if not app.config.get("SQLALCHEMY_ECHO", False):
        for name in (
            "sqlalchemy.engine",
            "sqlalchemy.engine.Engine",
            "sqlalchemy.orm",
            "sqlalchemy.pool",
        ):
            logging.getLogger(name).setLevel(logging.WARNING)
    for name in ("werkzeug", "engineio", "socketio"):
        logging.getLogger(name).setLevel(logging.WARNING)


def setup_sentry(app):
    dsn = (app.config.get("SENTRY_DSN") or "").strip()
    if not dsn or not sentry_sdk:
        app.logger.info("Sentry disabled (no DSN configured).")
        return
    try:
        sentry_sdk.init(
            dsn=dsn,
            integrations=[FlaskIntegration(), SqlalchemyIntegration()],
            traces_sample_rate=app.config.get("SENTRY_TRACES_SAMPLE_RATE", 0.0),
            profiles_sample_rate=app.config.get("SENTRY_PROFILES_SAMPLE_RATE", 0.0),
            environment=app.config.get("APP_ENV", "production"),
            release=app.config.get("APP_VERSION") or None,
            send_default_pii=False,
            max_breadcrumbs=100,
        )
        app.logger.info("Sentry initialized.")
    except Exception as e:
        app.logger.warning("Sentry setup failed: %s", e)


db = SQLAlchemy(session_options={"expire_on_commit": False})


# ═══════════════════════════════════════════════════════════════════════
# 🔄 Checkpoint تلقائي لـ WAL بعد كل commit
# ═══════════════════════════════════════════════════════════════════════

_checkpoint_counter = 0
_CHECKPOINT_INTERVAL = 5


@event.listens_for(db.session.__class__, "after_commit")
def _auto_checkpoint_after_commit(session):
    """تنفيذ checkpoint تلقائي بعد commit لدمج WAL في الملف الرئيسي"""
    global _checkpoint_counter
    try:
        from flask import current_app
        from sqlalchemy import text
        uri = current_app.config.get("SQLALCHEMY_DATABASE_URI", "")
        if not uri.startswith("sqlite:///"):
            return
        
        _checkpoint_counter += 1
        if _checkpoint_counter >= _CHECKPOINT_INTERVAL:
            _checkpoint_counter = 0
            try:
                session.execute(text("PRAGMA wal_checkpoint(PASSIVE)"))
            except Exception:
                try:
                    session.execute(text("PRAGMA wal_checkpoint(TRUNCATE)"))
                except Exception:
                    pass
    except Exception:
        pass
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()
csrf = CSRFProtect()
compress = Compress()
socketio = SocketIO(cors_allowed_origins="*", logger=False, engineio_logger=False)

# نظام الإشعارات الفورية
def send_notification(user_id: int, notification_type: str, title: str, message: str, data: dict = None):
    """
    إرسال إشعار فوري للمستخدم
    
    ⚠️ معطّل: كان يسبب تعليق في النظام
    """
    # ❌ معطّل مؤقتاً - كان يسبب مشاكل أداء
    return
    
    # الكود القديم (معطّل):
    # try:
    #     notification = {
    #         "type": notification_type,
    #         "title": title,
    #         "message": message,
    #         "timestamp": datetime.now(timezone.utc).isoformat(),
    #         "data": data or {}
    #     }
    #     socketio.emit('notification', notification, room=f'user_{user_id}')
    # except Exception as e:
    #     logging.getLogger(__name__).error(f"Failed to send notification: {e}")

def send_broadcast_notification(notification_type: str, title: str, message: str, data: dict = None):
    """
    إرسال إشعار عام لجميع المستخدمين
    
    ⚠️ معطّل: كان يسبب تعليق في النظام
    """
    # ❌ معطّل مؤقتاً - كان يسبب مشاكل أداء
    return
    
    # الكود القديم (معطّل):
    # try:
    #     notification = {
    #         "type": notification_type,
    #         "title": title,
    #         "message": message,
    #         "timestamp": datetime.now(timezone.utc).isoformat(),
    #         "data": data or {}
    #     }
    #     socketio.emit('broadcast_notification', notification)
    # except Exception as e:
    #     logging.getLogger(__name__).error(f"Failed to send broadcast notification: {e}")

def send_system_alert(alert_type: str, message: str, severity: str = "warning"):
    """
    إرسال تنبيه نظام
    
    ⚠️ معطّل: كان يسبب تعليق في النظام
    """
    # ❌ معطّل مؤقتاً - كان يسبب مشاكل أداء
    return
    
    # الكود القديم (معطّل):
    # try:
    #     alert = {
    #         "type": "system_alert",
    #         "alert_type": alert_type,
    #         "message": message,
    #         "severity": severity,
    #         "timestamp": datetime.now(timezone.utc).isoformat()
    #     }
    #     socketio.emit('system_alert', alert)
    # except Exception as e:
    #     logging.getLogger(__name__).error(f"Failed to send system alert: {e}")
cache = Cache()


def _rate_limit_key():
    try:
        from flask_login import current_user
        if getattr(current_user, "is_authenticated", False):
            return f"user:{current_user.get_id()}"
    except Exception:
        pass
    return get_remote_address()


limiter = Limiter(key_func=_rate_limit_key, default_limits=[])
scheduler = BackgroundScheduler()


@event.listens_for(Engine, "connect")
def _configure_db_connection(dbapi_connection, connection_record):
    """Configure database connection based on dialect (SQLite/PostgreSQL)"""
    try:
        if isinstance(dbapi_connection, sqlite3.Connection):
            cur = dbapi_connection.cursor()
            cur.execute("PRAGMA busy_timeout=30000")
            cur.execute("PRAGMA journal_mode=WAL")
            cur.execute("PRAGMA synchronous=FULL")
            cur.execute("PRAGMA foreign_keys=ON")
            cur.execute("PRAGMA cache_size=-128000")
            cur.execute("PRAGMA temp_store=MEMORY")
            cur.execute("PRAGMA mmap_size=268435456")
            cur.execute("PRAGMA page_size=4096")
            cur.execute("PRAGMA auto_vacuum=INCREMENTAL")
            cur.execute("PRAGMA threads=4")
            cur.execute("PRAGMA wal_autocheckpoint=500")
            cur.execute("PRAGMA optimize")
            cur.execute("PRAGMA query_only=0")
            cur.close()
        # PostgreSQL optimization/configuration could be added here if needed
        # e.g., setting application_name or specific session variables
    except Exception:
        pass


def perform_wal_checkpoint(app):
    """تنفيذ Checkpoint دوري لدمج WAL وتقليل حجمه"""
    try:
        uri = app.config.get("SQLALCHEMY_DATABASE_URI", "")
        if not uri.startswith("sqlite:///"):
            return
        
        with app.app_context():
            try:
                from sqlalchemy import text
                result = db.session.execute(text("PRAGMA wal_checkpoint(TRUNCATE)")).fetchone()
                if result and len(result) >= 3:
                    busy, log, checkpointed = result[0], result[1], result[2]
                    if busy == 0 and log == 0:
                        app.logger.debug(f"✅ WAL Checkpoint completed: {checkpointed} pages checkpointed")
                    else:
                        app.logger.debug(f"⚠️ WAL Checkpoint: busy={busy}, log={log}, checkpointed={checkpointed}")
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                app.logger.warning(f"⚠️ WAL Checkpoint failed: {e}")
    except Exception as e:
        app.logger.warning(f"⚠️ WAL Checkpoint error: {e}")


def quick_wal_checkpoint():
    """تفريغ WAL checkpoint بسرعة - للاستخدام في قوائم الموردين/العملاء/الشركاء"""
    try:
        from flask import current_app
        from sqlalchemy import text
        uri = current_app.config.get("SQLALCHEMY_DATABASE_URI", "")
        if not uri.startswith("sqlite:///"):
            return
        
        try:
            db.session.execute(text("PRAGMA wal_checkpoint(PASSIVE)"))
            db.session.commit()
        except Exception:
            try:
                db.session.execute(text("PRAGMA wal_checkpoint(TRUNCATE)"))
                db.session.commit()
            except Exception:
                db.session.rollback()
    except Exception:
        pass


def perform_vacuum_optimize(app):
    """تنفيذ VACUUM دوري لتنظيف وتحسين قاعدة البيانات"""
    try:
        uri = app.config.get("SQLALCHEMY_DATABASE_URI", "")
        
        with app.app_context():
            try:
                from sqlalchemy import text
                if uri.startswith("sqlite:///"):
                    db.session.execute(text("PRAGMA optimize"))
                    db.session.execute(text("PRAGMA incremental_vacuum"))
                    db.session.commit()
                elif "postgresql" in uri:
                    # PostgreSQL VACUUM cannot run inside a transaction block
                    # We need to use a raw connection with autocommit
                    conn = db.engine.raw_connection()
                    try:
                        conn.set_isolation_level(0) # ISOLATION_LEVEL_AUTOCOMMIT
                        cursor = conn.cursor()
                        cursor.execute("VACUUM ANALYZE")
                        cursor.close()
                    finally:
                        conn.close()
                
                app.logger.debug("✅ Database optimization completed")
            except Exception as e:
                # db.session.rollback() # Not needed for raw connection or if commit failed
                app.logger.warning(f"⚠️ Database optimization failed: {e}")
    except Exception as e:
        app.logger.warning(f"⚠️ Database optimization error: {e}")


def perform_backup_db(app=None):
    """نسخ احتياطي ذكي لقاعدة البيانات - يدعم SQLite و PostgreSQL"""
    try:
        # إذا تم استدعاء الدالة بدون app (مثلاً من قبل المستخدم)
        if app is None:
            from flask import current_app
            app = current_app
        
        uri = app.config.get("SQLALCHEMY_DATABASE_URI", "")
        backup_dir = app.config.get("BACKUP_DB_DIR")
        os.makedirs(backup_dir, exist_ok=True)
        
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        
        # PostgreSQL Backup (dump file format for restore)
        if "postgresql" in uri:
            backup_path = os.path.join(backup_dir, f"backup_{ts}.dump")
            try:
                import subprocess
                from sqlalchemy.engine.url import make_url
                
                u = make_url(uri)
                env = os.environ.copy()
                if u.password:
                    env["PGPASSWORD"] = u.password
                
                # Construct command: pg_dump -h host -p port -U user -d dbname -Fc -f file
                # -Fc means Custom format (compressed, suitable for pg_restore)
                cmd = ["pg_dump", "-h", u.host or "localhost", "-p", str(u.port or 5432), "-U", u.username or "postgres", "-d", u.database, "-Fc", "-f", backup_path]
                
                app.logger.info(f"Starting PostgreSQL backup to {backup_path}")
                process = subprocess.run(cmd, env=env, capture_output=True, text=True)
                
                if process.returncode == 0:
                    backup_info = {
                        "timestamp": ts,
                        "type": "postgresql",
                        "format": "custom",
                        "size": os.path.getsize(backup_path),
                        "version": app.config.get("APP_VERSION", "unknown")
                    }
                    info_path = os.path.join(backup_dir, f"backup_{ts}.info")
                    with open(info_path, "w") as f:
                        import json
                        json.dump(backup_info, f, indent=2)
                    app.logger.info(f"PostgreSQL backup completed successfully")
                    return True, "تم النسخ الاحتياطي بنجاح", backup_path
                else:
                    app.logger.error(f"PostgreSQL backup failed: {process.stderr}")
                    if os.path.exists(backup_path):
                        os.remove(backup_path)
                    return False, f"فشل النسخ الاحتياطي: {process.stderr}", None
            except Exception as e:
                app.logger.error(f"PostgreSQL backup exception: {e}")
                return False, f"خطأ في النسخ الاحتياطي: {str(e)}", None
                
        # SQLite Backup
        elif uri.startswith("sqlite:///"):
            db_path = uri.replace("sqlite:///", "")
            if not os.path.exists(db_path):
                app.logger.error(f"Database file not found: {db_path}")
                return False, "ملف قاعدة البيانات غير موجود", None
            
            backup_path = os.path.join(backup_dir, f"backup_{ts}.db")
            
            # نسخ احتياطي مع التحقق من التكامل
            src = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True, timeout=60)
            dst = sqlite3.connect(backup_path, timeout=60)
            
            try:
                # نسخ احتياطي مع التحقق
                backup_pages = int(app.config.get("BACKUP_DB_PAGES") or 1024)
                if backup_pages <= 0:
                    backup_pages = 1024
                backup_sleep = float(app.config.get("BACKUP_DB_SLEEP") or 0.1)
                if backup_sleep <= 0:
                    backup_sleep = 0.1
                src.execute("PRAGMA busy_timeout=60000")
                dst.execute("PRAGMA busy_timeout=60000")
                src.backup(dst, pages=backup_pages, sleep=backup_sleep)
                
                # التحقق من صحة النسخة الاحتياطية
                result = dst.execute("PRAGMA integrity_check").fetchone()
                if result[0] != "ok":
                    app.logger.error(f"Backup integrity check failed: {result[0]}")
                    dst.close()
                    os.remove(backup_path)
                    return False, f"فشل التحقق من صحة النسخة: {result[0]}", None
                
                # إضافة معلومات النسخة الاحتياطية
                backup_info = {
                    "timestamp": ts,
                    "original_size": os.path.getsize(db_path),
                    "backup_size": os.path.getsize(backup_path),
                    "version": app.config.get("APP_VERSION", "unknown")
                }
                
                # حفظ معلومات النسخة الاحتياطية
                info_path = os.path.join(backup_dir, f"backup_{ts}.info")
                with open(info_path, "w") as f:
                    import json
                    json.dump(backup_info, f, indent=2)
                
                app.logger.info(f"Database backup completed: {backup_path}")
                return True, "تم النسخ الاحتياطي بنجاح", backup_path
                
            except Exception as e:
                app.logger.error(f"Backup failed: {e}")
                if os.path.exists(backup_path):
                    os.remove(backup_path)
                return False, f"فشل النسخ الاحتياطي: {str(e)}", None
            finally:
                src.close()
                dst.close()
        
        else:
            app.logger.warning("Backup skipped: Database type not supported for auto-backup")
            return False, "نوع قاعدة البيانات غير مدعوم للنسخ التلقائي", None

        # تنظيف النسخ القديمة
        keep_last = app.config.get("BACKUP_KEEP_LAST", 5)
        # Match both .db, .sql and .dump files
        backups = sorted(glob.glob(os.path.join(backup_dir, "backup_*.*"))) 
        
        backup_files = sorted([f for f in backups if f.endswith(('.db', '.sql', '.dump'))])
        
        if len(backup_files) > keep_last:
            for old in backup_files[:-keep_last]:
                try:
                    os.remove(old)
                    # حذف ملف المعلومات أيضاً
                    info_file = os.path.splitext(old)[0] + ".info"
                    if os.path.exists(info_file):
                        os.remove(info_file)
                except Exception as e:
                    app.logger.warning(f"Failed to remove old backup {old}: {e}")
                    
    except Exception as e:
        app.logger.error(f"Backup process failed: {e}")
        return False, f"خطأ غير متوقع: {str(e)}", None


def process_asset_depreciation(app):
    try:
        with app.app_context():
            from models import SystemSettings, FixedAsset, FixedAssetCategory, AssetDepreciation, db
            from datetime import date
            from decimal import Decimal
            
            enable_auto = SystemSettings.get_setting('enable_auto_depreciation', False)
            if not enable_auto:
                return
            
            today = date.today()
            current_year = today.year
            current_month = today.month
            
            day_of_month = int(SystemSettings.get_setting('depreciation_day_of_month', 1))
            if today.day != day_of_month:
                return
            
            assets = FixedAsset.query.filter_by(status='ACTIVE').all()
            
            for asset in assets:
                existing = AssetDepreciation.query.filter_by(
                    asset_id=asset.id,
                    fiscal_year=current_year,
                    fiscal_month=current_month
                ).first()
                
                if existing:
                    continue
                
                category = asset.category
                if not category:
                    continue
                
                years_owned = (today - asset.purchase_date).days / 365.25
                if years_owned >= category.useful_life_years:
                    continue
                
                if category.depreciation_method == 'STRAIGHT_LINE':
                    annual_depreciation = float(asset.purchase_price) / category.useful_life_years
                    monthly_depreciation = annual_depreciation / 12
                else:
                    rate = float(category.depreciation_rate or 0) / 100
                    current_value = asset.get_current_book_value(today)
                    annual_depreciation = current_value * rate
                    monthly_depreciation = annual_depreciation / 12
                
                total_previous = db.session.query(func.sum(AssetDepreciation.depreciation_amount)).filter(
                    AssetDepreciation.asset_id == asset.id
                ).scalar() or 0
                
                accumulated = float(total_previous) + monthly_depreciation
                book_value = float(asset.purchase_price) - accumulated
                
                if book_value < 0:
                    book_value = 0
                    monthly_depreciation = float(asset.purchase_price) - float(total_previous)
                
                depreciation = AssetDepreciation(
                    asset_id=asset.id,
                    fiscal_year=current_year,
                    fiscal_month=current_month,
                    depreciation_date=today,
                    depreciation_amount=Decimal(str(round(monthly_depreciation, 2))),
                    accumulated_depreciation=Decimal(str(round(accumulated, 2))),
                    book_value=Decimal(str(round(book_value, 2)))
                )
                db.session.add(depreciation)
                
                from models import _gl_upsert_batch_and_entries, GL_ACCOUNTS
                
                entries = [
                    (GL_ACCOUNTS.get("DEPRECIATION_EXP", "6800_DEPRECIATION"), monthly_depreciation, 0),
                    (category.depreciation_account_code, 0, monthly_depreciation),
                ]
                
                try:
                    batch_id = _gl_upsert_batch_and_entries(
                        db.session.connection(),
                        source_type="DEPRECIATION",
                        source_id=asset.id,
                        purpose="DEPRECIATION",
                        currency="ILS",
                        memo=f"استهلاك {asset.name} - {current_year}/{current_month}",
                        entries=entries,
                        ref=f"DEP-{asset.asset_number}-{current_year}{current_month:02d}",
                        entity_type=None,
                        entity_id=None
                    )
                    depreciation.gl_batch_id = batch_id
                except Exception as e:
                    app.logger.warning(f"Failed to create GL for depreciation: {e}")
            
            db.session.commit()
            app.logger.info(f"[Depreciation] Processed {len(assets)} assets")
            
    except Exception as e:
        app.logger.error(f"[Depreciation] Job failed: {e}")


def update_exchange_rates_job(app):
    try:
        with app.app_context():
            from models import auto_update_missing_rates
            
            result = auto_update_missing_rates()
            
            if result.get('success'):
                updated = result.get('updated_rates', 0)
                app.logger.info(f"[FX Update] Updated {updated} exchange rates")
            else:
                app.logger.warning(f"[FX Update] Failed: {result.get('message', 'Unknown error')}")
                
    except Exception as e:
        app.logger.error(f"[FX Update] Job failed: {e}")


def process_recurring_invoices(app):
    try:
        with app.app_context():
            from models import RecurringInvoiceTemplate, RecurringInvoiceSchedule, db
            from datetime import date
            from routes.recurring_invoices import _generate_recurring_invoice
            
            today = date.today()
            
            templates = RecurringInvoiceTemplate.query.filter(
                RecurringInvoiceTemplate.is_active == True,
                RecurringInvoiceTemplate.next_invoice_date <= today,
                db.or_(
                    RecurringInvoiceTemplate.end_date.is_(None),
                    RecurringInvoiceTemplate.end_date >= today
                )
            ).all()
            
            generated_count = 0
            error_count = 0
            
            for template in templates:
                try:
                    scheduled_date = template.next_invoice_date
                    
                    if scheduled_date > today:
                        continue
                    
                    existing = RecurringInvoiceSchedule.query.filter_by(
                        template_id=template.id,
                        scheduled_date=scheduled_date,
                        status='GENERATED'
                    ).first()
                    
                    if existing:
                        continue
                    
                    _generate_recurring_invoice(template, scheduled_date)
                    db.session.commit()
                    generated_count += 1
                    
                except Exception as e:
                    error_count += 1
                    db.session.rollback()
                    
                    try:
                        schedule = RecurringInvoiceSchedule(
                            template_id=template.id,
                            scheduled_date=scheduled_date,
                            status='FAILED',
                            error_message=str(e)[:500]
                        )
                        db.session.add(schedule)
                        db.session.commit()
                    except Exception:
                        pass
                    
                    app.logger.error(f"[Recurring Invoices] Failed to generate invoice for template {template.id}: {e}")
            
            if generated_count > 0 or error_count > 0:
                app.logger.info(f"[Recurring Invoices] Generated {generated_count} invoices, {error_count} errors")
                
    except Exception as e:
        app.logger.error(f"[Recurring Invoices] Job failed: {e}")


def process_payment_reminders(app):
    try:
        with app.app_context():
            from utils import notify_payment_reminder
            
            result = notify_payment_reminder()
            
            if result.get('success'):
                sent = result.get('sent', 0)
                if sent > 0:
                    app.logger.info(f"[Payment Reminders] Sent {sent} reminders")
            else:
                app.logger.warning(f"[Payment Reminders] Failed: {result.get('error', 'Unknown')}")
                
    except Exception as e:
        app.logger.error(f"[Payment Reminders] Job failed: {e}")


def process_low_stock_alerts(app):
    try:
        with app.app_context():
            from models import Product, StockLevel, db
            from sqlalchemy import func
            from notifications import notify_low_stock
            
            products = db.session.query(
                Product,
                func.coalesce(func.sum(StockLevel.quantity), 0).label('total_stock')
            ).outerjoin(
                StockLevel, StockLevel.product_id == Product.id
            ).group_by(Product.id).having(
                func.coalesce(func.sum(StockLevel.quantity), 0) <= Product.min_qty
            ).all()
            
            alerted_count = 0
            
            for product, stock in products:
                if product.min_qty and stock <= product.min_qty:
                    try:
                        notify_low_stock(
                            product_id=product.id,
                            product_name=product.name,
                            current_stock=int(stock),
                            min_stock=int(product.min_qty or 0)
                        )
                        alerted_count += 1
                    except Exception as e:
                        app.logger.error(f"[Low Stock] Failed to notify for product {product.id}: {e}")
            
            if alerted_count > 0:
                app.logger.info(f"[Low Stock Alerts] Sent {alerted_count} alerts")
                
    except Exception as e:
        app.logger.error(f"[Low Stock Alerts] Job failed: {e}")


def process_check_reminders(app):
    try:
        with app.app_context():
            from models import Check, CheckStatus, db
            from datetime import datetime, timedelta
            from notifications import notify_system_alert, NotificationPriority
            
            today = datetime.utcnow().date()
            reminder_days = 3
            target_date = today + timedelta(days=reminder_days)
            
            upcoming_checks = Check.query.filter(
                Check.status == CheckStatus.PENDING.value,
                Check.check_due_date >= today,
                Check.check_due_date <= target_date
            ).all()
            
            overdue_checks = Check.query.filter(
                Check.status == CheckStatus.PENDING.value,
                Check.check_due_date < today
            ).all()
            
            if upcoming_checks:
                notify_system_alert(
                    title=f"تذكير: {len(upcoming_checks)} شيك مستحق خلال {reminder_days} أيام",
                    message=f"يوجد {len(upcoming_checks)} شيك يستحق التحصيل قريباً",
                    priority=NotificationPriority.MEDIUM
                )
                app.logger.info(f"[Check Reminders] {len(upcoming_checks)} upcoming checks")
            
            if overdue_checks:
                notify_system_alert(
                    title=f"تنبيه: {len(overdue_checks)} شيك متأخر!",
                    message=f"يوجد {len(overdue_checks)} شيك متأخر عن موعد الاستحقاق",
                    priority=NotificationPriority.HIGH
                )
                app.logger.warning(f"[Check Reminders] {len(overdue_checks)} overdue checks")
                
    except Exception as e:
        app.logger.error(f"[Check Reminders] Job failed: {e}")


def perform_backup_sql(app):
    """نسخ احتياطي SQL محسن - يدعم SQLite و PostgreSQL"""
    try:
        uri = app.config.get("SQLALCHEMY_DATABASE_URI", "")
        backup_dir = app.config.get("BACKUP_SQL_DIR")
        os.makedirs(backup_dir, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

        if uri.startswith("sqlite:///"):
            db_path = uri.replace("sqlite:///", "")
            if not os.path.exists(db_path):
                app.logger.error(f"Database file not found: {db_path}")
                return
            
            backup_path = os.path.join(backup_dir, f"backup_{ts}.sql")
            
            conn = sqlite3.connect(db_path)
            try:
                with open(backup_path, "w", encoding="utf-8") as f:
                    f.write(f"-- Database Backup\n")
                    f.write(f"-- Timestamp: {ts}\n")
                    f.write(f"-- Version: {app.config.get('APP_VERSION', 'unknown')}\n")
                    f.write(f"-- Original Size: {os.path.getsize(db_path)} bytes\n\n")
                    
                    for line in conn.iterdump():
                        f.write(f"{line}\n")
                
                app.logger.info(f"SQL backup completed: {backup_path}")
            finally:
                conn.close()

        elif uri.startswith("postgresql"):
            backup_path = os.path.join(backup_dir, f"backup_pg_{ts}.sql")
            
            # Extract connection details
            from urllib.parse import urlparse
            import subprocess
            
            parsed = urlparse(uri)
            db_name = parsed.path[1:]
            user = parsed.username
            password = parsed.password
            host = parsed.hostname
            port = parsed.port or 5432
            
            env = os.environ.copy()
            if password:
                env["PGPASSWORD"] = password
            
            cmd = [
                "pg_dump",
                "-h", host,
                "-p", str(port),
                "-U", user,
                "-F", "p",
                "-f", backup_path,
                db_name
            ]
            
            try:
                subprocess.run(cmd, env=env, check=True)
                app.logger.info(f"PostgreSQL backup completed: {backup_path}")
            except subprocess.CalledProcessError as e:
                app.logger.error(f"PostgreSQL backup failed: {e}")
            except FileNotFoundError:
                app.logger.error("pg_dump not found. Please install PostgreSQL client tools.")
        
        else:
            app.logger.warning("SQL backup skipped: Unsupported database type")

        # تنظيف النسخ القديمة
        keep_last = app.config.get("BACKUP_KEEP_LAST", 5)
        backups = sorted(glob.glob(os.path.join(backup_dir, "backup_*.sql")))
        if len(backups) > keep_last:
            for old in backups[:-keep_last]:
                try:
                    os.remove(old)
                except Exception as e:
                    app.logger.warning(f"Failed to remove old SQL backup {old}: {e}")

    except Exception as e:
        app.logger.error(f"Backup process failed: {e}")


def restore_database(app, backup_path):
    """استعادة قاعدة البيانات من نسخة احتياطية - يدعم SQLite و PostgreSQL"""
    try:
        uri = app.config.get("SQLALCHEMY_DATABASE_URI", "")
        
        # PostgreSQL Restore
        if "postgresql" in uri:
            try:
                import subprocess
                from sqlalchemy.engine.url import make_url
                
                u = make_url(uri)
                env = os.environ.copy()
                if u.password:
                    env["PGPASSWORD"] = u.password
                
                # Construct command: pg_restore -h host -p port -U user -d dbname --clean --if-exists backup_file
                # --clean: drop database objects before creating them
                # --if-exists: used with --clean to prevent errors if objects don't exist
                cmd = [
                    "pg_restore", 
                    "-h", u.host or "localhost", 
                    "-p", str(u.port or 5432), 
                    "-U", u.username or "postgres", 
                    "-d", u.database, 
                    "--clean", 
                    "--if-exists", 
                    "--no-owner",  # Skip ownership restoration
                    "--no-privileges",  # Skip privilege restoration
                    backup_path
                ]
                
                app.logger.info(f"Starting PostgreSQL restore from {backup_path}")
                process = subprocess.run(cmd, env=env, capture_output=True, text=True)
                
                if process.returncode == 0:
                    app.logger.info(f"PostgreSQL restore completed successfully")
                    return True, "تمت استعادة قاعدة البيانات بنجاح"
                else:
                    # pg_restore might return non-zero even on success with warnings
                    # Check if the error is fatal or just warnings
                    if "fatal" in process.stderr.lower() or "error" in process.stderr.lower():
                         app.logger.error(f"PostgreSQL restore failed: {process.stderr}")
                         return False, f"فشل الاستعادة: {process.stderr}"
                    else:
                        app.logger.warning(f"PostgreSQL restore finished with warnings: {process.stderr}")
                        return True, "تمت الاستعادة (مع بعض التحذيرات)"
                        
            except Exception as e:
                app.logger.error(f"PostgreSQL restore exception: {e}")
                return False, f"خطأ في الاستعادة: {str(e)}"

        # SQLite Restore
        elif uri.startswith("sqlite:///"):
            db_path = uri.replace("sqlite:///", "")
            
            try:
                # إغلاق الاتصالات الحالية
                db.session.remove()
                db.engine.dispose()
                
                # نسخ الملف
                import shutil
                shutil.copy2(backup_path, db_path)
                
                app.logger.info(f"SQLite restore completed: {db_path}")
                return True, "تمت استعادة قاعدة البيانات بنجاح"
                
            except Exception as e:
                app.logger.error(f"SQLite restore failed: {e}")
                return False, f"فشل الاستعادة: {str(e)}"
        
        else:
            return False, "نوع قاعدة البيانات غير مدعوم للاستعادة التلقائية"
            
    except Exception as e:
        app.logger.error(f"Restore process failed: {e}")
        return False, f"خطأ غير متوقع: {str(e)}"


def register_fonts(app=None):
    try:
        if not pdfmetrics or not TTFont:
            return
        base_path = os.path.join(app.root_path if app else os.getcwd(), "static", "fonts")
        fonts = {
            "Amiri": "Amiri-Regular.ttf",
            "Amiri-Bold": "Amiri-Bold.ttf",
            "Amiri-Italic": "Amiri-Italic.ttf",
            "Amiri-BoldItalic": "Amiri-BoldItalic.ttf",
        }
        for name, file in fonts.items():
            path = os.path.join(base_path, file)
            if os.path.exists(path):
                pdfmetrics.registerFont(TTFont(name, path))
    except Exception as e:
        logging.error("Font registration failed: %s", e)


def _safe_start_scheduler(app):
    skip_cmds = ("db", "seed", "shell", "migrate", "upgrade", "downgrade", "init")
    if any(cmd in sys.argv for cmd in skip_cmds):
        app.logger.info("Scheduler skipped: CLI context.")
        return
    try:
        if (os.environ.get("GUNICORN_CMD_ARGS") or "gunicorn" in " ".join(sys.argv).lower()) and os.environ.get("ENABLE_SCHEDULER") != "1":
            app.logger.info("Scheduler skipped: gunicorn context (set ENABLE_SCHEDULER=1 to enable).")
            return
    except Exception:
        pass
    try:
        is_uwsgi = ("uwsgi" in sys.modules) or bool(os.environ.get("UWSGI_ORIGINAL_PROC_NAME") or os.environ.get("UWSGI_FILE"))
        is_pythonanywhere = bool(os.environ.get("PYTHONANYWHERE_DOMAIN") or os.environ.get("PYTHONANYWHERE_SITE"))
        if (is_uwsgi or is_pythonanywhere) and os.environ.get("ENABLE_SCHEDULER") != "1":
            app.logger.info("Scheduler skipped: WSGI/uWSGI context (set ENABLE_SCHEDULER=1 to enable).")
            return
    except Exception:
        pass
    if os.environ.get("DISABLE_SCHEDULER"):
        app.logger.info("Scheduler disabled by environment variable.")
        return
    try:
        if not scheduler.running:
            scheduler.start()
            app.logger.info("APScheduler started.")
        else:
            app.logger.info("APScheduler already running; skip start.")
    except Exception as e:
        app.logger.warning(f"Scheduler start skipped: {e}")


def init_extensions(app):
    db.init_app(app)
    migrate.init_app(app, db)

    login_manager.init_app(app)
    login_manager.login_view = app.config.get("LOGIN_VIEW", "auth.login")
    login_manager.login_message_category = app.config.get("LOGIN_MESSAGE_CATEGORY", "warning")

    csrf.init_app(app)
    mail.init_app(app)
    
    compress.init_app(app)
    app.config.setdefault('COMPRESS_MIMETYPES', [
        'text/html', 'text/css', 'text/xml', 'text/javascript',
        'application/json', 'application/javascript'
    ])
    app.config.setdefault('COMPRESS_LEVEL', 9)
    app.config.setdefault('COMPRESS_MIN_SIZE', 100)

    # تعطيل SocketIO في Development mode لتجنب أخطاء WebSocket
    # يمكن تفعيله في Production مع gunicorn + gevent
    if not app.config.get('SOCKETIO_ENABLED', False):
        # تهيئة بدون websocket transport (polling only)
        socketio.init_app(
            app,
            async_mode='threading',  # استخدام threading بدل eventlet/gevent
            cors_allowed_origins=app.config.get("SOCKETIO_CORS_ORIGINS", "*"),
            logger=False,
            engineio_logger=False,
            ping_timeout=20,
            ping_interval=25,
            transports=['polling']  # فقط polling، بدون websocket
        )
    else:
        # في Production mode
        socketio.init_app(
            app,
            async_mode=app.config.get("SOCKETIO_ASYNC_MODE"),
            message_queue=app.config.get("SOCKETIO_MESSAGE_QUEUE"),
            cors_allowed_origins=app.config.get("SOCKETIO_CORS_ORIGINS", "*"),
            logger=app.config.get("SOCKETIO_LOGGER", False),
            engineio_logger=app.config.get("SOCKETIO_ENGINEIO_LOGGER", False),
            ping_timeout=app.config.get("SOCKETIO_PING_TIMEOUT", 20),
            ping_interval=app.config.get("SOCKETIO_PING_INTERVAL", 25),
            max_http_buffer_size=app.config.get("SOCKETIO_MAX_HTTP_BUFFER_SIZE", 100_000_000),
        )

    app.config.setdefault("RATELIMIT_HEADERS_ENABLED", True)
    app.config.setdefault("RATELIMIT_STORAGE_URI", "memory://")
    app.config.setdefault("RATELIMIT_EXEMPT_SUPER", True)

    limiter.init_app(app)
    cache.init_app(app)

    default_limit = app.config.get("RATELIMIT_DEFAULT")
    if default_limit:
        if isinstance(default_limit, (list, tuple)):
            limiter.default_limits = [str(x).strip() for x in default_limit if str(x).strip()]
        else:
            parts = [p.strip() for p in str(default_limit).split(";") if p.strip()]
            limiter.default_limits = parts

    if app.config.get("RATELIMIT_EXEMPT_SUPER", True):
        @limiter.request_filter
        def _exempt_super_admin():
            try:
                from flask_login import current_user
                if getattr(current_user, "is_authenticated", False):
                    if getattr(current_user, "is_super_role", False):
                        return True
                    role_name = str(getattr(getattr(current_user, "role", None), "name", "")).strip().lower()
                    if role_name == "super_admin":
                        return True
            except Exception:
                return False
            return False

    try:
        scheduler.add_job(
            lambda: perform_backup_db(app),
            "interval",
            seconds=app.config.get("BACKUP_DB_INTERVAL").total_seconds(),
            id="db_backup",
            replace_existing=True,
        )
        scheduler.add_job(
            lambda: perform_backup_sql(app),
            "interval",
            seconds=app.config.get("BACKUP_SQL_INTERVAL").total_seconds(),
            id="sql_backup",
            replace_existing=True,
        )
        
        scheduler.add_job(
            lambda: update_exchange_rates_job(app),
            "interval",
            hours=1,
            id="update_fx_rates",
            replace_existing=True,
        )
        
        scheduler.add_job(
            lambda: process_asset_depreciation(app),
            "cron",
            day=1,
            hour=2,
            minute=0,
            id="asset_depreciation",
            replace_existing=True,
        )
        
        scheduler.add_job(
            lambda: process_recurring_invoices(app),
            "cron",
            hour=0,
            minute=5,
            id="recurring_invoices",
            replace_existing=True,
        )
        
        scheduler.add_job(
            lambda: process_payment_reminders(app),
            "cron",
            hour=9,
            minute=0,
            id="payment_reminders",
            replace_existing=True,
        )
        
        scheduler.add_job(
            lambda: process_low_stock_alerts(app),
            "cron",
            hour=8,
            minute=0,
            id="low_stock_alerts",
            replace_existing=True,
        )
        
        scheduler.add_job(
            lambda: process_check_reminders(app),
            "cron",
            hour=7,
            minute=30,
            id="check_reminders",
            replace_existing=True,
        )
        
        scheduler.add_job(
            lambda: perform_wal_checkpoint(app),
            "interval",
            minutes=3,
            id="wal_checkpoint",
            replace_existing=True,
        )
        
        scheduler.add_job(
            lambda: perform_vacuum_optimize(app),
            "interval",
            hours=1,
            id="db_vacuum",
            replace_existing=True,
        )
        
        if app.config.get("ENABLE_AUTOMATED_BACKUPS", True):
            try:
                from backup_automation import schedule_automated_backups
                state = app.extensions.setdefault("auto_backup_scheduler", {})
                if not state.get("scheduled"):
                    schedule_automated_backups(app, scheduler)
                    state["scheduled"] = True
            except Exception as e:
                app.logger.warning(f"Automated backup scheduling failed: {e}")
    except Exception as e:
        app.logger.warning(f"Scheduler job registration failed: {e}")

    _safe_start_scheduler(app)
    register_fonts(app)
    
    try:
        skip_cmds = ("db", "seed", "shell", "migrate", "upgrade", "downgrade", "init")
        if not any(cmd in sys.argv for cmd in skip_cmds):
            if os.environ.get("DISABLE_PERFORMANCE_INDEXES"):
                return
            if not app.config.get("AUTO_CREATE_PERFORMANCE_INDEXES", True):
                return
            ensure_performance_indexes(app)
    except Exception:
        pass

def ensure_performance_indexes(app):
    try:
        from sqlalchemy import text
        with app.app_context():
            uri = app.config.get("SQLALCHEMY_DATABASE_URI", "")
            base_stmts = [
                "CREATE INDEX IF NOT EXISTS ix_users_is_active ON users (is_active)",
                "CREATE INDEX IF NOT EXISTS ix_users_lower_username ON users (lower(username))",
                "CREATE INDEX IF NOT EXISTS ix_users_lower_email ON users (lower(email))",
                "CREATE INDEX IF NOT EXISTS ix_users_last_login ON users (last_login)",
                "CREATE INDEX IF NOT EXISTS ix_users_last_seen ON users (last_seen)",
                "CREATE INDEX IF NOT EXISTS ix_products_name ON products (name)",
                "CREATE INDEX IF NOT EXISTS ix_products_part_number ON products (part_number)",
                "CREATE INDEX IF NOT EXISTS ix_products_brand ON products (brand)",
                "CREATE INDEX IF NOT EXISTS ix_stock_levels_wh ON stock_levels (warehouse_id)",
                "CREATE INDEX IF NOT EXISTS ix_stock_levels_prod ON stock_levels (product_id)",
                "CREATE INDEX IF NOT EXISTS ix_stock_levels_wh_prod ON stock_levels (warehouse_id, product_id)",
                "CREATE INDEX IF NOT EXISTS ix_sales_date ON sales (sale_date)",
                "CREATE INDEX IF NOT EXISTS ix_sales_customer_id ON sales (customer_id)",
                "CREATE INDEX IF NOT EXISTS ix_sales_customer_date ON sales (customer_id, sale_date)",
                "CREATE INDEX IF NOT EXISTS ix_sales_status ON sales (status)",
                "CREATE INDEX IF NOT EXISTS ix_payments_date ON payments (payment_date)",
                "CREATE INDEX IF NOT EXISTS ix_payments_is_archived ON payments (is_archived)",
                "CREATE INDEX IF NOT EXISTS ix_customers_created_at ON customers (created_at)",
                "CREATE INDEX IF NOT EXISTS ix_customers_name ON customers (name)",
                "CREATE INDEX IF NOT EXISTS ix_customers_phone ON customers (phone)",
                "CREATE INDEX IF NOT EXISTS ix_customers_lower_email ON customers (lower(email))",
                "CREATE INDEX IF NOT EXISTS ix_customers_category ON customers (category)",
                "CREATE INDEX IF NOT EXISTS ix_customers_current_balance ON customers (current_balance)",
                "CREATE INDEX IF NOT EXISTS ix_customers_is_active ON customers (is_active)",
                "CREATE INDEX IF NOT EXISTS ix_customers_is_online ON customers (is_online)",
                "CREATE INDEX IF NOT EXISTS ix_customers_is_archived ON customers (is_archived)",
                "CREATE INDEX IF NOT EXISTS ix_payments_status ON payments (status)",
                "CREATE INDEX IF NOT EXISTS ix_payments_direction ON payments (direction)",
                "CREATE INDEX IF NOT EXISTS ix_payments_entity_type ON payments (entity_type)",
                "CREATE INDEX IF NOT EXISTS ix_payments_method ON payments (method)",
                "CREATE INDEX IF NOT EXISTS ix_payments_currency ON payments (currency)",
                "CREATE INDEX IF NOT EXISTS ix_payments_customer_id ON payments (customer_id)",
                "CREATE INDEX IF NOT EXISTS ix_payments_supplier_id ON payments (supplier_id)",
                "CREATE INDEX IF NOT EXISTS ix_payments_partner_id ON payments (partner_id)",
                "CREATE INDEX IF NOT EXISTS ix_payments_invoice_id ON payments (invoice_id)",
                "CREATE INDEX IF NOT EXISTS ix_payments_sale_id ON payments (sale_id)",
                "CREATE INDEX IF NOT EXISTS ix_payments_service_id ON payments (service_id)",
                "CREATE INDEX IF NOT EXISTS ix_payments_customer_date ON payments (customer_id, payment_date)",
                "CREATE INDEX IF NOT EXISTS ix_payments_supplier_date ON payments (supplier_id, payment_date)",
                "CREATE INDEX IF NOT EXISTS ix_payments_partner_date ON payments (partner_id, payment_date)",
                "CREATE INDEX IF NOT EXISTS ix_payments_payment_number ON payments (payment_number)",
                "CREATE INDEX IF NOT EXISTS ix_payments_receipt_number ON payments (receipt_number)",
                "CREATE INDEX IF NOT EXISTS ix_invoices_invoice_number ON invoices (invoice_number)",
                "CREATE INDEX IF NOT EXISTS ix_invoices_invoice_date ON invoices (invoice_date)",
                "CREATE INDEX IF NOT EXISTS ix_invoices_status ON invoices (status)",
                "CREATE INDEX IF NOT EXISTS ix_invoices_customer_id ON invoices (customer_id)",
                "CREATE INDEX IF NOT EXISTS ix_invoices_customer_date ON invoices (customer_id, invoice_date)",
                "CREATE INDEX IF NOT EXISTS ix_service_requests_customer_id ON service_requests (customer_id)",
                "CREATE INDEX IF NOT EXISTS ix_service_requests_mechanic_id ON service_requests (mechanic_id)",
                "CREATE INDEX IF NOT EXISTS ix_service_requests_status ON service_requests (status)",
                "CREATE INDEX IF NOT EXISTS ix_service_requests_priority ON service_requests (priority)",
                "CREATE INDEX IF NOT EXISTS ix_service_requests_received_at ON service_requests (received_at)",
                "CREATE INDEX IF NOT EXISTS ix_service_requests_customer_status_date ON service_requests (customer_id, status, received_at)",
                "CREATE INDEX IF NOT EXISTS ix_service_requests_customer_date ON service_requests (customer_id, received_at)",
                "CREATE INDEX IF NOT EXISTS ix_service_requests_status_created_at ON service_requests (status, created_at)",
                "CREATE INDEX IF NOT EXISTS ix_service_requests_mechanic_status ON service_requests (mechanic_id, status)",
                "CREATE INDEX IF NOT EXISTS ix_service_requests_status_priority ON service_requests (status, priority)",
                "CREATE INDEX IF NOT EXISTS ix_service_requests_received_status ON service_requests (received_at, status)",
                "CREATE INDEX IF NOT EXISTS ix_checks_status_due_date_direction ON checks (status, check_due_date, direction)",
                "CREATE INDEX IF NOT EXISTS ix_checks_customer_id_date ON checks (customer_id, check_date)",
                "CREATE INDEX IF NOT EXISTS ix_checks_supplier_id_date ON checks (supplier_id, check_date)",
                "CREATE INDEX IF NOT EXISTS ix_checks_partner_id_date ON checks (partner_id, check_date)",
                "CREATE INDEX IF NOT EXISTS ix_checks_payment_id_status ON checks (payment_id, status)",
                "CREATE INDEX IF NOT EXISTS ix_checks_is_archived_status ON checks (is_archived, status)",
                "CREATE INDEX IF NOT EXISTS ix_checks_check_date_status ON checks (check_date, status)",
                "CREATE INDEX IF NOT EXISTS ix_checks_payment_id ON checks (payment_id)",
                "CREATE INDEX IF NOT EXISTS ix_checks_check_date ON checks (check_date)",
                "CREATE INDEX IF NOT EXISTS ix_checks_direction ON checks (direction)",
                "CREATE INDEX IF NOT EXISTS ix_checks_status ON checks (status)",
                "CREATE INDEX IF NOT EXISTS ix_partners_is_archived_balance ON partners (is_archived, current_balance)",
                "CREATE INDEX IF NOT EXISTS ix_partners_name_phone ON partners (name, phone_number)",
                "CREATE INDEX IF NOT EXISTS ix_partners_customer_id ON partners (customer_id)",
                "CREATE INDEX IF NOT EXISTS ix_partners_currency_balance ON partners (currency, current_balance)",
                "CREATE INDEX IF NOT EXISTS ix_partners_share_percentage ON partners (share_percentage)",
                "CREATE INDEX IF NOT EXISTS ix_suppliers_name ON suppliers (name)",
                "CREATE INDEX IF NOT EXISTS ix_suppliers_phone ON suppliers (phone_number)",
                "CREATE INDEX IF NOT EXISTS ix_suppliers_lower_email ON suppliers (lower(email))",
                "CREATE INDEX IF NOT EXISTS ix_suppliers_is_archived ON suppliers (is_archived)",
                "CREATE INDEX IF NOT EXISTS ix_suppliers_currency ON suppliers (currency)",
                "CREATE INDEX IF NOT EXISTS ix_suppliers_current_balance ON suppliers (current_balance)",
                "CREATE INDEX IF NOT EXISTS ix_gl_batches_posted_at ON gl_batches (posted_at)",
                "CREATE INDEX IF NOT EXISTS ix_gl_batches_status ON gl_batches (status)"
            ]
            pg_trgm_stmts = [
                "CREATE INDEX IF NOT EXISTS gin_customers_name_trgm ON customers USING gin (name gin_trgm_ops)",
                "CREATE INDEX IF NOT EXISTS gin_suppliers_name_trgm ON suppliers USING gin (name gin_trgm_ops)",
                "CREATE INDEX IF NOT EXISTS gin_partners_name_trgm ON partners USING gin (name gin_trgm_ops)",
                "CREATE INDEX IF NOT EXISTS gin_payments_reference_trgm ON payments USING gin (reference gin_trgm_ops)",
                "CREATE INDEX IF NOT EXISTS gin_payments_notes_trgm ON payments USING gin (notes gin_trgm_ops)",
                "CREATE INDEX IF NOT EXISTS gin_checks_check_number_trgm ON checks USING gin (check_number gin_trgm_ops)",
            ]
            pg_partial_stmts = [
                "CREATE INDEX IF NOT EXISTS ix_payments_date_active ON payments (payment_date) WHERE is_archived = false",
                "CREATE INDEX IF NOT EXISTS ix_payments_customer_date_completed ON payments (customer_id, payment_date) WHERE is_archived = false AND status = 'COMPLETED'",
                "CREATE INDEX IF NOT EXISTS ix_checks_date_pending ON checks (check_date) WHERE status = 'PENDING'",
                "CREATE INDEX IF NOT EXISTS ix_service_received_active ON service_requests (received_at) WHERE status IN ('PENDING','IN_PROGRESS','DIAGNOSIS')",
            ]
            sqlite_partial_stmts = [
                "CREATE INDEX IF NOT EXISTS ix_payments_date_active ON payments (payment_date) WHERE is_archived = 0",
                "CREATE INDEX IF NOT EXISTS ix_payments_customer_date_completed ON payments (customer_id, payment_date) WHERE is_archived = 0 AND status = 'COMPLETED'",
                "CREATE INDEX IF NOT EXISTS ix_checks_date_pending ON checks (check_date) WHERE status = 'PENDING'",
            ]

            if "postgresql" in uri:
                with db.engine.connect() as conn:
                    ac = conn.execution_options(isolation_level="AUTOCOMMIT")

                    def _exec(sql: str) -> bool:
                        try:
                            ac.execute(text(sql))
                            return True
                        except Exception:
                            return False

                    for sql in base_stmts:
                        _exec(sql)

                    pg_trgm_ready = _exec("CREATE EXTENSION IF NOT EXISTS pg_trgm")
                    if not pg_trgm_ready:
                        try:
                            pg_trgm_ready = bool(
                                ac.execute(text("SELECT 1 FROM pg_extension WHERE extname = 'pg_trgm' LIMIT 1")).scalar()
                            )
                        except Exception:
                            pg_trgm_ready = False
                    if pg_trgm_ready:
                        for sql in pg_trgm_stmts:
                            _exec(sql)
                    for sql in pg_partial_stmts:
                        _exec(sql)
            else:
                stmts = list(base_stmts)
                if uri.startswith("sqlite"):
                    stmts += sqlite_partial_stmts
                for sql in stmts:
                    try:
                        db.session.execute(text(sql))
                        db.session.commit()
                    except Exception:
                        try:
                            db.session.rollback()
                        except Exception:
                            pass
    except Exception:
        pass
