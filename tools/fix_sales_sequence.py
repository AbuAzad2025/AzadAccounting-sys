import os
import sys
from sqlalchemy import text

project_home = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_home not in sys.path:
    sys.path.insert(0, project_home)

from app import create_app
from extensions import db


def _q_ident(name: str) -> str:
    return '"' + (name or "").replace('"', '""') + '"'


def sync_all_sequences():
    from sqlalchemy import inspect as sa_inspect
    insp = sa_inspect(db.engine)
    tables = insp.get_table_names(schema="public")
    synced = []
    skipped = []
    for tbl in tables:
        try:
            seq_name = db.session.execute(
                text("SELECT pg_get_serial_sequence(:tname, 'id')"),
                {"tname": f'public.{tbl}'}
            ).scalar()
            if not seq_name:
                skipped.append(tbl)
                continue
            qt = f'public.{_q_ident(tbl)}'
            max_id = db.session.execute(text(f"SELECT COALESCE(MAX(id), 0) FROM {qt}")).scalar() or 0
            is_called = bool(max_id > 0)
            val = max_id if is_called else 1
            db.session.execute(
                text("SELECT setval(:seq::regclass, :val, :called)"),
                {"seq": seq_name, "val": int(val), "called": is_called}
            )
            synced.append((tbl, seq_name, int(max_id)))
        except Exception:
            db.session.rollback()
            skipped.append(tbl)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
    return synced, skipped


def main():
    app = create_app()
    with app.app_context():
        try:
            synced, skipped = sync_all_sequences()
            print("✅ تمت مزامنة التسلسلات")
            for tbl, seq, m in synced:
                print(f" - {tbl}: seq={seq} max_id={m}")
            if skipped:
                print("⚠️ جداول متروكة بدون تسلسل id:")
                for tbl in skipped:
                    print(f" - {tbl}")

            try:
                from models import AuditLog
                # تصحيح seller_id في جدول المبيعات عند فقدانه أو عدم صلاحية المرجع
                bad_sales = db.session.execute(text("""
                    SELECT s.id
                    FROM public.sales s
                    LEFT JOIN public.users u ON u.id = s.seller_id
                    WHERE u.id IS NULL
                """)).fetchall()
                bad_ids = [int(r[0]) for r in bad_sales]
                fixed = 0
                defaults_used = 0
                default_user_id = db.session.execute(text("""
                    SELECT id FROM public.users WHERE is_active = true ORDER BY id LIMIT 1
                """)).scalar()
                for sid in bad_ids:
                    uid = db.session.execute(text("""
                        SELECT user_id FROM public.audit_logs
                        WHERE model_name = 'Sale' AND record_id = :sid AND action = 'CREATE' AND user_id IS NOT NULL
                        ORDER BY id LIMIT 1
                    """), {"sid": sid}).scalar()
                    if not uid:
                        # محاولة استخدام cancelled_by أو archived_by
                        uid = db.session.execute(text("""
                            SELECT COALESCE(cancelled_by, archived_by) FROM public.sales WHERE id = :sid
                        """), {"sid": sid}).scalar()
                    if not uid:
                        uid = default_user_id
                        defaults_used += 1
                    if uid:
                        db.session.execute(text("""
                            UPDATE public.sales SET seller_id = :uid WHERE id = :sid
                        """), {"uid": int(uid), "sid": sid})
                        fixed += 1
                db.session.commit()
                print(f"✅ تم تصحيح seller_id للمبيعات: {fixed} صفوف")
                if defaults_used:
                    print(f"ℹ️ تم استخدام المستخدم الافتراضي لعدد {defaults_used} صفوف")
            except Exception as e_fk:
                db.session.rollback()
                print(f"⚠️ تعذر تصحيح seller_id: {e_fk}")
        except Exception as e:
            print(f"❌ خطأ أثناء المزامنة: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
