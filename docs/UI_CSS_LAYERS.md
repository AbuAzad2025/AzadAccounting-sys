# نظام الثيم — Arabic ERP Theme System

## المصدر الوحيد (من مايو 2026)

- **JSON:** `docs/arabic_erp_theme_system.json`
- **CSS:** `static/css/erp-theme/index.css` (tokens + components + patterns + responsive + security-bridge)
- **JS:** `static/js/erp-theme.js`

## القوالب الموحّدة

| القالب | الاستخدام |
|--------|-----------|
| `templates/base.html` | ERP بعد الدخول (مالك، مبيعات، تقارير…) |
| `templates/layouts/erp_public.html` | دخول، أخطاء، صفحات عامة |
| `templates/security/base_security.html` | وحدة الأمان (شريط/سايدبار ERP مخفيان) |

## Partials مشتركة

- `partials/erp_theme_head_early.html` — منع وميض الثيم
- `partials/erp_head_assets.html` — CSS/JS موحّد (`erp_head_mode`: app \| public)
- `partials/erp_public_navbar.html` + `erp_public_drawer.html`
- `partials/navbar.html` + `sidebar.html` + `footer.html`

## الترتيب في `base.html`

1. AdminLTE + Select2 (هيكل فقط)
2. `ui.css` (تخطيط sidebar)
3. `mobile.css`, `mobile-app.css`, `gm-*` (صفحات متخصصة)
4. `numbers-fix`, `bs5-utils`, `tenant-scope`, `ux-messages`
5. **`erp-theme/index.css`** — كل الألوان والمكوّنات
6. `{% block styles %}` / `extra_css`

## تم إيقافه (لا يُحمَّل)

`style.css`, `enhancements.css`, `ux-unified.css`, `ux-contrast.css`, `erp-arabic-ui.css`, `erp-forms-spacing.css`, `erp-conflict-fixes.css`, `erp-content-migrated.css`

## وحدة الأمان

`erp-security-layout.css` + `erp-security-migrated.css` + نفس `erp-theme` من `base.html`

## وحدة الأمان

- `erp-security-layout.css` — هيكل فقط
- `erp-security.css` — ألوان فاتحة
- `security_responsive.css`

## JavaScript

- `safe-enhancements.js` — يتخطى تزيين حقول التاريخ عند `body.erp-unified`
- `base.html` — `applySidebarPosition()` يضبط هوامش الشريط (لا تغيّر ارتفاع الحقول)

## عند إضافة CSS جديد

- لا تضع `!important` على `.form-control` / `.table thead` بعد طبقة ERP
- استخدم `body.erp-unified .content-wrapper` للنطاق
- صفحات خاصة: `{% block extra_css %}` فقط للاستثناءات
