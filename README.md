<div align="center">

# 🏛️ AzadAccounting-sys
### نظام محاسبي شامل ومتكامل | Comprehensive Enterprise Accounting System

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=flat&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?style=flat&logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-supported-336791?style=flat&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-Proprietary-red.svg)](#-license--الترخيص)
[![Lines of Code](https://img.shields.io/badge/LOC-159K%2B-blueviolet)](#)
[![AI Modules](https://img.shields.io/badge/AI%20Engines-53-orange)](#-ai-brain--محرك-الذكاء-الاصطناعي)

**[العربية](#-بالعربية) · [English](#-in-english) · [Quick Start](#-quick-start--بدء-سريع) · [Architecture](#-architecture--المعمارية)**

</div>

---

## 🌟 بالعربية

### نظرة عامة

**AzadAccounting-sys** هو نظام تخطيط موارد المؤسسات (ERP) ومحاسبة احترافي مبني بلغة Python/Flask، مصمّم خصيصاً لاحتياجات السوق العربي مع تركيز خاص على ورش السيارات والمعدّات الثقيلة، شركات المقاولات، وتجار قطع الغيار. يجمع النظام بين قوة المحاسبة بالقيد المزدوج، إدارة المخزون، تتبع الخدمات، والمتجر الإلكتروني، مع طبقة ذكاء اصطناعي محلية متكاملة (53 محرك متخصص).

> **+159,000 سطر برمجي · 152 نموذج بيانات · 57 وحدة وظيفية · 87 صلاحية نظام**

### ✨ المميزات الرئيسية

#### 💰 المحاسبة المتقدمة
- **قيد مزدوج كامل** مع دفتر أستاذ عام (GL) ودفعات/قبوضات
- **دليل حسابات** متعدد المستويات
- **الفواتير المتكررة** الآلية
- **الموازنات والالتزامات** (Budgets & Commitments)
- **مراكز التكلفة** مع قواعد توزيع آلية
- **الأصول الثابتة والإهلاك** بطرق متعددة
- **التسوية البنكية** ومتابعة الشيكات (مودع/مرتد/مصروف)
- **متعدد العملات** مع أسعار صرف ديناميكية
- **ضرائب فلسطين والـ VAT** جاهزة

#### 📦 المخزون والمبيعات
- إدارة **مخازن متعددة** عبر فروع ومواقع
- **حركة مخزون** كاملة + جرد فعلي
- **التحويلات** بين المخازن + **المقايضة** (Exchange)
- **شراكات في المخازن والمنتجات** مع توزيع الأرباح
- **شحنات** مع شراكات تمويل
- **مبيعات + مرتجعات + حجوزات** (PreOrders)
- **دفعات متعددة الطرق**: نقدي، شيك، بطاقة، تحويل، إلكتروني

#### 🔧 خدمات الورشة
- أوامر إصلاح (Service Requests) مع قطع غيار ومهام
- ربط مباشر بالمحاسبة والمخزون
- معرفة AI خاصة بالميكانيك، ECU، والمعدات الثقيلة

#### 🛒 المتجر الإلكتروني
- سلة تسوّق + دفعات إلكترونية (بوابة Blooprint)
- تقييمات المنتجات + برنامج ولاء العملاء
- حجوزات مسبقة (Pre-orders)

#### 👥 الموارد البشرية
- موظفين + سلف + خصومات + تايم شيت
- فرق هندسية مع مهارات متخصصة

#### 🏗️ إدارة المشاريع
- مشاريع كاملة بمراحل، معالم، مخاطر، تكاليف، إيرادات
- موارد، أوامر تغيير، مشاكل، قراءات وقت

#### 🤖 الذكاء الاصطناعي (الميزة المميزة)
**53 محرك AI متخصص** يعمل محلياً (LOCAL_ONLY) أو هجين (HYBRID) أو سحابي (Groq/OpenAI/Anthropic):
- محاسب آلي محترف + مدقق حسابات
- محرك تشخيص ميكانيكي + خبرة ECU
- تعلّم ذاتي مستمر + تطور آلي
- تحليلات تنبؤية + كشف أنشطة مشبوهة
- مساعد محادثة بلغة طبيعية عربية

#### 🔐 الأمان على مستوى المؤسسات
- **RBAC** كامل بـ 87 صلاحية و Roles ديناميكية
- **حماية ضد Brute Force** (Redis + memory fallback)
- **حظر IP والدول** المشبوهة
- **CSRF + Talisman + SameSite cookies**
- **حماية من timing attacks وrace conditions**
- **تشفير PAN** للبطاقات الائتمانية
- **تدقيق كامل** (AuditLog) لكل عملية
- **حذف ناعم** مع أرشيف قابل للاسترداد

#### 🌐 خصائص هندسية
- 🌍 **متعدد اللغات** (Babel) — عربي/إنجليزي
- 📱 **PWA** جاهز (service worker + manifest)
- ⚡ **WebSocket realtime** (Flask-SocketIO)
- 📊 **Prometheus metrics** + **Sentry**
- 💾 **نسخ احتياطي آلي** كل ساعة
- 🗄️ **متعدد قواعد البيانات**: PostgreSQL، MySQL، SQLite
- 📨 **Twilio WhatsApp/SMS** + **Email**
- 🏷️ **مسح الباركود + OCR** (OpenCV + RapidOCR)
- 📄 **تقارير PDF احترافية** (WeasyPrint + ReportLab)

---

## 🌟 In English

### Overview

**AzadAccounting-sys** is a professional, full-featured ERP and accounting platform built with Python/Flask, purpose-built for the Arabic-speaking market with a strong focus on automotive/heavy-equipment workshops, contracting companies, and spare-parts retailers. It combines double-entry accounting, multi-warehouse inventory, service tracking, an online shop, and a fully integrated local AI brain (53 specialized engines).

> **159K+ lines of code · 152 data models · 57 functional modules · 87 system permissions**

### ✨ Key Features

- 💰 **Full double-entry accounting** — General Ledger, multi-level Chart of Accounts, recurring invoices, budgets, cost centers, fixed assets & depreciation, bank reconciliation, multi-currency with dynamic FX rates, Palestinian tax & VAT.
- 📦 **Multi-warehouse inventory** — branches/sites, stock movements & audits, transfers, product exchanges, partnerships in warehouses & products, shipments with funding partners.
- 🛒 **Sales pipeline** — sales, returns, pre-orders, multi-method payments (cash, cheque, card, wire, online), online shop with cart, payments gateway, ratings, and customer loyalty.
- 🔧 **Workshop service management** — service requests with parts & tasks, fully linked to accounting & inventory, with AI mechanical/ECU/heavy-equipment expertise.
- 👥 **HR + project management** — employees, advances, deductions, timesheets, engineering teams, full project lifecycle (phases, milestones, risks, costs, change orders, issues).
- 🤖 **53 specialized AI engines** — professional accountant, GL auditor, mechanical diagnostics, continuous self-learning, predictive analytics, NLP in Arabic. Runs locally (LOCAL_ONLY), hybrid, or with cloud providers (Groq/OpenAI/Anthropic).
- 🔐 **Enterprise-grade security** — RBAC (87 permissions), brute-force protection, IP/country blocking, CSRF + Talisman, timing-attack & race-condition guards, PAN encryption, full audit log, soft delete with recoverable archive.
- 🌐 **Production-ready engineering** — i18n (Arabic/English), PWA, WebSocket realtime, Prometheus metrics, Sentry, hourly auto-backup, multi-DB (PostgreSQL/MySQL/SQLite), Twilio WhatsApp/SMS, barcode scanning, OCR, PDF reports.

---

## 🏗️ Architecture | المعمارية

### High-Level System Diagram

```mermaid
graph TB
    subgraph Client["🖥️ Client Layer"]
        Browser["Web Browser<br/>(Bootstrap + AdminLTE)"]
        PWA["PWA / Mobile<br/>(Service Worker)"]
        Scanner["Barcode Scanner<br/>(OpenCV + pyzbar)"]
    end

    subgraph Edge["🚪 Edge / Gateway"]
        Nginx["Reverse Proxy<br/>(Gunicorn/Waitress)"]
        CORS["CORS + Talisman"]
        RateLimit["Rate Limiter<br/>(Flask-Limiter)"]
    end

    subgraph App["🧠 Flask Application Core"]
        Auth["Auth Layer<br/>Flask-Login + CSRF"]
        ACL["ACL Layer<br/>87 Permissions"]
        Routes["57 Blueprints"]
        Services["Domain Services<br/>(Ledger / Workflow / Backup)"]
        AI["AI Brain<br/>53 Engines"]
    end

    subgraph Data["💾 Data Layer"]
        DB[("PostgreSQL /<br/>MySQL / SQLite")]
        Redis[("Redis<br/>Cache + Sessions")]
        Files["File Storage<br/>(uploads / backups)"]
    end

    subgraph Async["⚙️ Async Workers"]
        Celery["Celery Workers"]
        APScheduler["APScheduler<br/>(Backups + AI Training)"]
        SocketIO["SocketIO<br/>(Realtime)"]
    end

    subgraph External["🌍 External Services"]
        Twilio["Twilio<br/>(WhatsApp/SMS)"]
        SMTP["SMTP Mail"]
        Sentry["Sentry"]
        Prometheus["Prometheus"]
        Groq["Groq / OpenAI /<br/>Anthropic"]
        Gateway["Payment Gateway<br/>(Blooprint)"]
        FX["forex-python /<br/>yfinance"]
    end

    Client --> Edge --> App
    App --> Data
    App --> Async
    Async --> Data
    App -.-> External
    AI -.-> Groq
```

### Module Map | خريطة الوحدات

```mermaid
mindmap
  root((AzadAccounting))
    Accounting
      General Ledger
      Chart of Accounts
      Recurring Invoices
      Budgets
      Cost Centers
      Fixed Assets
      Bank Reconciliation
      Multi-currency
      Taxes & VAT
    Inventory
      Warehouses
      Stock Movements
      Transfers
      Exchanges
      Partners
      Shipments
      Barcode
      Stock Audit
    Sales
      Sales & Returns
      PreOrders
      Payments
      Cheques
      Online Shop
      Loyalty
      Ratings
    Service
      Service Requests
      Service Parts
      Service Tasks
      Equipment Types
    HR
      Employees
      Advances
      Deductions
      Timesheets
    Projects
      Phases
      Milestones
      Risks
      Costs
      Change Orders
    AI Brain
      Accounting Auditor
      Mechanical Expert
      ECU Knowledge
      Heavy Equipment
      Self-Learning
      Predictive Analytics
    Security
      RBAC
      Audit Log
      IP Blocking
      Rate Limiting
      Soft Delete
```

### Data Flow: Sale → GL

```mermaid
sequenceDiagram
    actor User
    participant UI as Frontend
    participant Sales as Sales Blueprint
    participant DB as Database
    participant Ledger as LedgerService
    participant GL as GL Engine
    participant AI as AI Auditor

    User->>UI: Create Sale
    UI->>Sales: POST /sales/new
    Sales->>DB: Create Sale + SaleLines
    Sales->>DB: Reduce StockLevel
    Sales->>Ledger: run_sale_gl_sync_after_commit()
    Ledger->>GL: Generate GLBatch + GLEntries
    GL->>DB: Persist (Debit/Credit balanced)
    GL->>AI: Submit batch for review
    AI-->>UI: Async anomaly alert (if any)
    Sales-->>User: Sale confirmed
```

---

## 🚀 Quick Start | بدء سريع

### Prerequisites | المتطلبات

| Tool | Version | Notes |
|---|---|---|
| Python | 3.11+ | Tested on 3.11 / 3.12 |
| PostgreSQL | 14+ | Recommended (MySQL & SQLite also supported) |
| Redis | 6+ | Optional but recommended for cache + rate limiting |
| Node.js | (none) | Pure Python stack |

### 🪟 Windows (PowerShell)

```powershell
# Clone
git clone https://github.com/AbuAzad2025/AzadAccounting-sys.git
cd AzadAccounting-sys

# One-shot setup (creates venv, installs deps, runs migrations)
.\setup_windows.ps1

# Or step-by-step
.\setup_venv_and_run.ps1
```

### 🐧 Linux / macOS

```bash
# Clone
git clone https://github.com/AbuAzad2025/AzadAccounting-sys.git
cd AzadAccounting-sys

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip wheel setuptools
pip install -r requirements.txt

# Configure environment (see Configuration section)
cp .env.example .env  # then edit .env

# Run migrations
export FLASK_APP=app:create_app
flask db upgrade

# Initialize system (seeds roles + permissions)
python cli.py init-system   # or via Flask CLI

# Run development server
python app.py
# → http://127.0.0.1:5000
```

### 🐳 Docker (recommended for production)

```bash
# Quick start with docker-compose (Postgres + Redis + App)
# (docker-compose.yml is recommended to be added - see Roadmap)

docker build -t azadaccounting .
docker run -d \
  -p 5000:5000 \
  -e DATABASE_URL=postgresql://user:pass@host:5432/db \
  -e REDIS_URL=redis://redis:6379/0 \
  -e SECRET_KEY=$(openssl rand -hex 32) \
  --name azadaccounting \
  azadaccounting
```

### 🚢 Production Deployment

```bash
# Recommended: Gunicorn + Nginx reverse proxy
gunicorn -w 4 -k gevent --timeout 120 \
  -b 0.0.0.0:5000 \
  "app:create_app()"
```

---

## ⚙️ Configuration | الإعدادات

Create a `.env` file in the project root. **Required** variables marked with ⭐.

### Core Settings

```env
# === App ===
APP_ENV=production              # production | development | local
DEBUG=false
FLASK_APP=app:create_app
SECRET_KEY=                     # ⭐ generate with: python -c "import secrets;print(secrets.token_hex(32))"
HOST=0.0.0.0
PORT=5000
APP_VERSION=1.0.0

# === Database ===
DATABASE_URL=postgresql://user:password@host:5432/azad_db   # ⭐
# Or build from parts:
# PGHOST=localhost
# PGPORT=5432
# PGUSER=postgres
# PGPASSWORD=secret
# PGDATABASE=azad_db
DB_SSLMODE_REQUIRE=false
SQLALCHEMY_POOL_SIZE=100
SQLALCHEMY_MAX_OVERFLOW=200

# === Cache & Queue ===
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2
CACHE_TYPE=flask_caching.backends.redis.RedisCache
CACHE_DEFAULT_TIMEOUT=1800

# === Security ===
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_SAMESITE=Lax
WTF_CSRF_ENABLED=true
CORS_ORIGINS=https://your-domain.com
SOCKETIO_CORS_ORIGINS=https://your-domain.com
PASSWORD_HASH_METHOD=scrypt
MAX_LOGIN_ATTEMPTS=5
LOGIN_BLOCK_DURATION_MINUTES=15
ENABLE_TIMING_ATTACK_PROTECTION=true
ENABLE_RACE_CONDITION_PROTECTION=true
CARD_ENC_KEY=                   # base64-encoded 32 bytes for PCI-grade PAN encryption
```

### Optional Integrations

```env
# === Email ===
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=noreply@example.com
MAIL_PASSWORD=app-password
MAIL_DEFAULT_SENDER="AzadAccounting <noreply@example.com>"

# === Twilio (WhatsApp + SMS) ===
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_WHATSAPP_NUMBER=whatsapp:+1234567890

# === Payment Gateway ===
ONLINE_GATEWAY_DEFAULT=blooprint
BLOOPRINT_WEBHOOK_SECRET=

# === Observability ===
SENTRY_DSN=
SENTRY_TRACES_SAMPLE_RATE=0.1
JSON_LOGS=true
LOG_LEVEL=INFO

# === AI Providers (optional - system runs locally by default) ===
GROQ_API_KEY=
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
AI_SYSTEMS_ENABLED=true

# === Business Defaults ===
DEFAULT_CURRENCY=ILS
GL_AUTO_POST_ON_EXCHANGE=false
GL_EXCHANGE_INV_ACCOUNT=1205_INV_EXCHANGE
GL_EXCHANGE_COGS_ACCOUNT=5105_COGS_EXCHANGE
GL_EXCHANGE_AP_ACCOUNT=2000_AP

# === Backups ===
ENABLE_AUTOMATED_BACKUPS=true
BACKUP_KEEP_LAST=5
BACKUP_DIR=./instance/backups
```

---

## 📂 Project Structure | بنية المشروع

```
AzadAccounting-sys/
├── app.py                      # Application factory + bootstrap
├── config.py                   # Environment-driven settings
├── extensions.py               # Flask extensions init (DB, cache, auth, etc.)
├── models.py                   # 152 SQLAlchemy models (17K LOC)
├── forms.py                    # WTForms (5K LOC)
├── cli.py                      # Management commands (seeding, audits)
├── acl.py                      # Centralized ACL attachment
├── reports.py                  # Financial reporting engine
├── utils.py / utils/           # Helpers (security, money, etc.)
│
├── routes/                     # 57 Blueprints (one per domain)
│   ├── auth.py, main.py
│   ├── sales.py, payments.py, expenses.py
│   ├── warehouses.py, parts.py, shipments.py
│   ├── service.py, projects.py, engineering.py
│   ├── ledger_blueprint.py, financial_reports.py
│   ├── ai_routes.py, ai_admin.py
│   ├── workflows.py, archive.py, performance.py
│   └── ...
│
├── services/                   # Cross-cutting domain services
│   ├── ledger_service.py       # GL automation + caching
│   ├── workflow_engine.py      # State-machine workflow runner
│   ├── backup_service.py       # Scheduled backups
│   ├── prometheus_service.py   # Metrics exporter
│   ├── system_initializer.py   # Bootstrap seeding
│   └── ghost_manager.py        # Soft-delete orchestration
│
├── AI/                         # 🤖 Local AI brain
│   ├── scheduler.py            # AI cron jobs
│   └── engine/                 # 53 specialized AI modules
│       ├── ai_service.py
│       ├── ai_accounting_professional.py
│       ├── ai_diagnostic_engine.py
│       ├── ai_mechanical_knowledge.py
│       ├── ai_predictive_analytics.py
│       └── ...
│
├── permissions_config/         # 87 system permissions + ACL guards
├── middleware/                 # Custom security middleware
├── helpers/                    # Balance event helpers
├── migrations/                 # Alembic database migrations
├── translations/               # i18n (Babel)
├── templates/                  # 50 Jinja2 template directories
└── static/                     # CSS / JS / images / vendor libs
```

---

## 🤖 AI Brain | محرك الذكاء الاصطناعي

The system ships with **53 specialized AI engines** totaling ~30K LOC, organized by domain:

| Category | Engines | Purpose |
|---|---|---|
| **🧾 Accounting** | `ai_accounting_professional`, `ai_accounting_auditor`, `ai_gl_knowledge`, `ai_knowledge_finance` | Auto-classification, journal review, tax knowledge |
| **🔧 Technical** | `ai_mechanical_knowledge`, `ai_ecu_knowledge`, `ai_heavy_equipment_expert`, `ai_diagnostic_engine` | Workshop diagnostics & technical advice |
| **🧠 Cognition** | `ai_reasoning_engine`, `ai_nlp_engine`, `ai_comprehension_engine`, `ai_unified_mind`, `ai_master_controller` | Reasoning + Arabic NLP |
| **📚 Learning** | `ai_continuous_learner`, `ai_auto_learning`, `ai_intensive_trainer`, `ai_marathon_trainer`, `ai_self_evolution` | Self-improving knowledge base |
| **🔍 Discovery** | `ai_auto_discovery`, `ai_data_awareness`, `ai_database_expert`, `ai_database_search` | Auto-introspection of the system |
| **📈 Analytics** | `ai_predictive_analytics`, `ai_performance_tracker`, `ai_code_quality_monitor` | Forecasts & monitoring |
| **🛡️ Safety** | `ai_security`, `ai_self_review`, `ai_permissions` | AI guardrails |

**Modes of operation:**

| Mode | Description | Use Case |
|---|---|---|
| `LOCAL_ONLY` (default) | 100% on-device, no external calls | Privacy-first / air-gapped |
| `HYBRID` | Local first, cloud fallback | Best of both worlds |
| `API_ONLY` | Always use cloud LLM | Highest accuracy |

Configure via `AI_SYSTEMS_ENABLED` + provider keys (`GROQ_API_KEY`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`).

---

## 🔐 Security & Permissions | الأمان والصلاحيات

- **RBAC**: 87 fine-grained permissions across all domains. Defined in `permissions_config/enums.py`, attached per-blueprint in `permissions_config/blueprint_guards.py`.
- **Brute-force protection**: 5 failed attempts → 15-min block (Redis-backed, with in-memory fallback).
- **Geo-blocking**: `BlockedIP` and `BlockedCountry` tables for fine-grained access control.
- **Rate limiting**: `100/day; 20/hour; 5/minute` defaults, stricter on `/auth` and `/api`.
- **CSRF**: Enabled everywhere except explicit webhook endpoints.
- **Talisman**: Forces HTTPS, sets HSTS, X-Frame-Options, CSP in production.
- **Cookies**: `HttpOnly`, `SameSite=Lax`, `Secure` in production.
- **Audit**: Every model that matters mixes in `AuditMixin` → who/when/what tracked automatically.
- **Soft delete + Archive**: Recoverable deletion via `Archive` and `DeletionLog`.

---

## 📊 API & Endpoints | الواجهات البرمجية

The system exposes ~57 blueprints with both HTML and JSON endpoints. Key APIs:

| Endpoint Prefix | Purpose |
|---|---|
| `/auth` | Login / logout / password reset |
| `/api` | JSON API (programmatic access) |
| `/api/balances` | Real-time balance queries |
| `/health` | Health-check + system status |
| `/ai` | AI assistant endpoints |
| `/reports` | Financial reports (HTML + PDF + Excel) |
| `/shop` | Public storefront |
| `/sales`, `/purchases`, `/payments` | Core transactional flows |

Full OpenAPI spec generation is on the roadmap.

---

## 🗄️ Database Migrations

```bash
# Apply latest migrations
flask db upgrade

# Create a new migration
flask db migrate -m "describe your change"

# Rollback one step
flask db downgrade -1
```

Current migration history (9 migrations):
1. `79cf2ae42e8e` — Initial comprehensive schema
2. `b1a3f0c6d8a9` — Composite indexes for settlements
3. `d4e5f6a7b8c9` — Legacy columns + data backfill
4. `a7b8c9d0e1f2` — Expand GL entries account length
5. `e5f6a7b8c9d0` — Expand accounts code length
6. `f6a7b8c9d0e1` — Expand GL entries ref length
7. `94948c531c03` — Add `return_date` to `SaleReturn`
8. `c3a0f1b8d2e4` — Expand expense payee type constraint
9. `10f6c0ee04dc` — Check schema

---

## 🧪 Testing | الاختبار

```bash
# Run all tests
pytest

# With coverage
pytest --cov=. --cov-report=html

# Lint
flake8 .
```

---

## 📈 Observability | المراقبة

| Tool | What it tracks |
|---|---|
| **Prometheus** | HTTP metrics, DB pool, custom counters at `/metrics` |
| **Sentry** | Errors + transaction traces (set `SENTRY_DSN`) |
| **Health endpoint** | `/health` → DB, cache, disk, memory, AI status |
| **Audit log** | `AuditLog` table — every mutation tracked |
| **Performance monitor** | Built-in middleware (set `PERF_MONITOR_ENABLED=true`) |

---

## 🛣️ Roadmap | خارطة الطريق

- [ ] 🐳 Docker / docker-compose for one-click deployment
- [ ] 📱 Mobile app (React Native / Flutter) consuming the JSON API
- [ ] 📖 OpenAPI 3.0 spec + Swagger UI
- [ ] 🧩 Refactor monolithic `models.py` (17K LOC) into a `models/` package
- [ ] 🧩 Consolidate the 53 AI engines into 8–10 cohesive modules
- [ ] 🌐 Full English UI parity (currently Arabic-first)
- [ ] 🧾 Electronic invoicing compliance (Saudi/UAE/Egypt e-invoice standards)
- [ ] 📊 Real-time dashboards with WebSocket-driven charts
- [ ] 🔌 Plugin system for third-party extensions

---

## 🤝 Contributing | المساهمة

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Follow PEP 8 + run `flake8`
4. Write/update tests
5. Submit a PR with a clear description

---

## 📜 License | الترخيص

This is a **proprietary** business system. All rights reserved © 2026 **AbuAzad2025**.
For licensing inquiries, please contact the repository owner.

هذا نظام **خاص ومحفوظ الحقوق**. جميع الحقوق محفوظة © 2026 **AbuAzad2025**.
للاستفسار عن التراخيص، يرجى التواصل مع مالك المستودع.

---

## 📞 Contact & Support | التواصل والدعم

- **GitHub Issues**: [Open an issue](https://github.com/AbuAzad2025/AzadAccounting-sys/issues)
- **Discussions**: [GitHub Discussions](https://github.com/AbuAzad2025/AzadAccounting-sys/discussions)
- **Sponsor**: See [`.github/FUNDING.yml`](.github/FUNDING.yml)

---

<div align="center">

### Built with ❤️ for the Arabic accounting community
### بُني بكل ❤️ لمجتمع المحاسبة العربي

⭐ **Star this repo if you find it useful!** ⭐

</div>
