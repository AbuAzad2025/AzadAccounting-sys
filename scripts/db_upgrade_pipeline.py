import os
import sys
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

ROOT = str(Path(__file__).resolve().parent.parent)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
os.chdir(ROOT)

from app import bootstrap_database
from extensions import db, migrate
from flask_migrate import stamp, upgrade
from flask import Flask
from config import Config

def create_minimal_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    migrate.init_app(app, db)
    return app


def _q(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def _fetch_scalar(conn, sql: str, params=None):
    return conn.execute(text(sql), params or {}).scalar()


def _fetch_rows(conn, sql: str, params=None):
    return conn.execute(text(sql), params or {}).fetchall()


def _tables_without_pk(conn):
    sql = """
    select c.relname
    from pg_class c
    join pg_namespace n on n.oid = c.relnamespace
    where c.relkind = 'r'
      and n.nspname = 'public'
      and not exists (
        select 1
        from pg_constraint pc
        where pc.conrelid = c.oid
          and pc.contype = 'p'
      )
    order by c.relname
    """
    return [r[0] for r in _fetch_rows(conn, sql)]


def _has_column(conn, table: str, column: str) -> bool:
    sql = """
    select count(*)
    from information_schema.columns
    where table_schema = 'public'
      and table_name = :table
      and column_name = :column
    """
    return int(_fetch_scalar(conn, sql, {"table": table, "column": column}) or 0) > 0


def _ensure_id_sequence(conn, table: str):
    seq_name = f"{table}_id_seq"
    qt = _q(table)
    qseq = _q(seq_name)
    conn.execute(text(f"create sequence if not exists {qseq}"))
    conn.execute(text(f"alter table {qt} alter column id set default nextval('{seq_name}')"))
    conn.execute(text(f"select setval('{seq_name}', coalesce((select max(id) from {qt}), 0) + 1, false)"))


def _ensure_pk_on_table(conn, table: str):
    qt = _q(table)
    dup_count = int(
        _fetch_scalar(
            conn,
            f"select count(*) from (select id from {qt} group by id having count(*) > 1) d",
        )
        or 0
    )
    if dup_count > 0:
        raise RuntimeError(f"duplicate id values in {table}: {dup_count}")
    null_count = int(_fetch_scalar(conn, f"select count(*) from {qt} where id is null") or 0)
    if null_count > 0:
        conn.execute(
            text(
                f"""
                with m as (select coalesce(max(id), 0) as mx from {qt}),
                n as (
                    select ctid, row_number() over (order by ctid) + (select mx from m) as new_id
                    from {qt}
                    where id is null
                )
                update {qt} t
                set id = n.new_id
                from n
                where t.ctid = n.ctid
                """
            )
        )
    conn.execute(text(f"alter table {qt} alter column id set not null"))
    _ensure_id_sequence(conn, table)
    sql = f"""
    do $$
    begin
      if not exists (
        select 1
        from pg_constraint
        where conrelid = '{table}'::regclass
          and contype = 'p'
      ) then
        execute 'alter table {qt} add constraint {table}_pkey primary key (id)';
      end if;
    end $$;
    """
    conn.execute(text(sql))


def _ensure_unique_constraint(conn, table: str, column: str, constraint_name: str):
    qt = _q(table)
    qc = _q(column)
    exists = int(
        _fetch_scalar(
            conn,
            """
            select count(*)
            from pg_constraint
            where conname = :name
              and conrelid = to_regclass(:tbl)
            """,
            {"name": constraint_name, "tbl": table},
        )
        or 0
    )
    if exists:
        return
    sql = f"""
    do $$
    begin
      if not exists (
        select 1
        from pg_constraint
        where conname = '{constraint_name}'
          and conrelid = '{table}'::regclass
      ) then
        execute 'alter table {qt} add constraint {constraint_name} unique ({qc})';
      end if;
    end $$;
    """
    conn.execute(text(sql))


def _normalize_users(conn):
    if not _public_table_exists(conn, "users"):
        return
    _run_if_column(conn, "users", "username", "update users set username = trim(username)")
    _run_if_column(conn, "users", "email", "update users set email = lower(trim(email))")
    if _column_exists(conn, "users", "username"):
        conn.execute(
            text(
                """
                update users
                set username = 'user_' || id::text
                where username is null or trim(username) = ''
                """
            )
        )
        conn.execute(
            text(
                """
                with d as (
                    select id, row_number() over (partition by username order by id) as rn
                    from users
                )
                update users u
                set username = u.username || '_' || u.id::text
                from d
                where u.id = d.id and d.rn > 1
                """
            )
        )
        _ensure_unique_constraint(conn, "users", "username", "uq_users_username")
    if _column_exists(conn, "users", "email"):
        conn.execute(
            text(
                """
                update users
                set email = 'user_' || id::text || '@local.invalid'
                where email is null or trim(email) = ''
                """
            )
        )
        conn.execute(
            text(
                """
                with d as (
                    select id, row_number() over (partition by email order by id) as rn
                    from users
                )
                update users u
                set email = split_part(u.email, '@', 1) || '_' || u.id::text || '@' || split_part(u.email, '@', 2)
                from d
                where u.id = d.id and d.rn > 1
                """
            )
        )
        _ensure_unique_constraint(conn, "users", "email", "uq_users_email")


def _ensure_default_accounts(conn):
    """ضمان وجود الحسابات الافتراضية في دليل الحسابات لتجنب أخطاء القيود"""
    if not _public_table_exists(conn, "accounts"):
        return

    # القائمة القياسية للحسابات المستخدمة في النظام
    # (Code, Name, Type)
    defaults = [
        ("1000_CASH", "النقدية بالصندوق", "ASSET"),
        ("1010_BANK", "البنك", "ASSET"),
        ("1020_CARD_CLEARING", "تسويات البطاقات", "ASSET"),
        ("1100_AR", "الذمم المدينة (العملاء)", "ASSET"),
        ("1200_INVENTORY", "المخزون", "ASSET"),
        ("1205_INV_EXCHANGE", "مخزون الصرف", "ASSET"),
        ("1300_INV_RSV", "احتياطي المخزون", "LIABILITY"),
        ("1599_ACC_DEP", "مجمع الإهلاك", "ASSET"),
        
        ("2000_AP", "الذمم الدائنة (الموردين)", "LIABILITY"),
        ("2100_VAT_PAYABLE", "ضريبة القيمة المضافة المستحقة", "LIABILITY"),
        ("2200_INCOME_TAX_PAYABLE", "ضريبة الدخل المستحقة", "LIABILITY"),
        ("2300_ADV_PAY", "دفعات مقدمة من العملاء", "LIABILITY"),
        
        ("3000_CAPITAL", "رأس المال", "EQUITY"),
        ("3100_RETAINED_EARNINGS", "الأرباح المحتجزة", "EQUITY"),
        
        ("4000_SALES", "المبيعات", "REVENUE"),
        ("4050_SALES_DISCOUNT", "خصم المبيعات", "REVENUE"),
        ("4100_SERVICE_REVENUE", "إيرادات الخدمات", "REVENUE"),
        ("4200_SHIPPING_INCOME", "إيرادات الشحن", "REVENUE"),
        
        ("5000_EXPENSES", "المصروفات العامة", "EXPENSE"),
        ("5000_COGS", "تكلفة البضاعة المباعة", "EXPENSE"),
        ("5105_COGS_EXCHANGE", "تكلفة صرف المخزون", "EXPENSE"),
        ("6200_INCOME_TAX_EXPENSE", "مصروف ضريبة الدخل", "EXPENSE"),
        ("6800_DEPRECIATION", "مصروف الإهلاك", "EXPENSE"),
    ]

    for code, name, type_ in defaults:
        exists = _fetch_scalar(conn, "select 1 from accounts where code = :code", {"code": code})
        if not exists:
            conn.execute(
                text("""
                    INSERT INTO accounts (code, name, type, is_active, created_at, updated_at)
                    VALUES (:code, :name, :type, true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """),
                {"code": code, "name": name, "type": type_}
            )
            print(f"CREATED_ACCOUNT: {code} - {name}")


def _ensure_financial_integrity(conn):
    """تدقيق وإصلاح البيانات المالية لضمان التكامل المرجعي والمحاسبي"""
    
    # 1. Sales Integrity
    if _public_table_exists(conn, "sales"):
        # تعيين العملة الافتراضية
        _run_if_column(conn, "sales", "currency", "UPDATE sales SET currency = 'ILS' WHERE currency IS NULL OR TRIM(currency) = ''")
        # تعيين المجاميع الصفرية بدلاً من NULL
        _run_if_column(conn, "sales", "total_amount", "UPDATE sales SET total_amount = 0 WHERE total_amount IS NULL")
        _run_if_column(conn, "sales", "tax_amount", "UPDATE sales SET tax_amount = 0 WHERE tax_amount IS NULL")
        _run_if_column(conn, "sales", "discount_amount", "UPDATE sales SET discount_amount = 0 WHERE discount_amount IS NULL")
        _run_if_column(conn, "sales", "paid_amount", "UPDATE sales SET paid_amount = 0 WHERE paid_amount IS NULL")
        _run_if_column(conn, "sales", "remaining_amount", "UPDATE sales SET remaining_amount = 0 WHERE remaining_amount IS NULL")
        # تصحيح الحالات
        _run_if_column(conn, "sales", "status", "UPDATE sales SET status = 'DRAFT' WHERE status IS NULL OR TRIM(status) = ''")
        _run_if_column(conn, "sales", "payment_status", "UPDATE sales SET payment_status = 'PENDING' WHERE payment_status IS NULL OR TRIM(payment_status) = ''")

    # 2. Payments Integrity
    if _public_table_exists(conn, "payments"):
        _run_if_column(conn, "payments", "currency", "UPDATE payments SET currency = 'ILS' WHERE currency IS NULL OR TRIM(currency) = ''")
        _run_if_column(conn, "payments", "amount", "UPDATE payments SET amount = 0 WHERE amount IS NULL")
        _run_if_column(conn, "payments", "method", "UPDATE payments SET method = 'CASH' WHERE method IS NULL OR TRIM(method) = ''")
        _run_if_column(conn, "payments", "status", "UPDATE payments SET status = 'COMPLETED' WHERE status IS NULL OR TRIM(status) = ''")
        _run_if_column(conn, "payments", "direction", "UPDATE payments SET direction = 'IN' WHERE direction IS NULL OR TRIM(direction) = ''")

    # 3. Expenses Integrity
    if _public_table_exists(conn, "expenses"):
        _run_if_column(conn, "expenses", "currency", "UPDATE expenses SET currency = 'ILS' WHERE currency IS NULL OR TRIM(currency) = ''")
        _run_if_column(conn, "expenses", "amount", "UPDATE expenses SET amount = 0 WHERE amount IS NULL")
        _run_if_column(conn, "expenses", "tax_amount", "UPDATE expenses SET tax_amount = 0 WHERE tax_amount IS NULL")
        _run_if_column(conn, "expenses", "payee_type", "UPDATE expenses SET payee_type = 'OTHER' WHERE payee_type IS NULL OR TRIM(payee_type) = ''")

    # 4. Service Requests Integrity
    if _public_table_exists(conn, "service_requests"):
        _run_if_column(conn, "service_requests", "currency", "UPDATE service_requests SET currency = 'ILS' WHERE currency IS NULL OR TRIM(currency) = ''")
        conn.execute(text("UPDATE service_requests SET total_cost = 0 WHERE total_cost IS NULL"))
        conn.execute(text("UPDATE service_requests SET status = 'PENDING' WHERE status IS NULL OR TRIM(status) = ''"))

    # 5. GL Batches Integrity
    if _public_table_exists(conn, "gl_batches"):
        # تعيين العملة
        conn.execute(text("UPDATE gl_batches SET currency = 'ILS' WHERE currency IS NULL OR TRIM(currency) = ''"))
        # إصلاح الحالات
        conn.execute(text("UPDATE gl_batches SET status = 'DRAFT' WHERE status IS NULL OR TRIM(status) = ''"))
        # التأكد من وجود تاريخ ترحيل للمرحلين
        conn.execute(text("UPDATE gl_batches SET posted_at = created_at WHERE status = 'POSTED' AND posted_at IS NULL"))
        conn.execute(text("UPDATE gl_batches SET posted_at = NULL WHERE status != 'POSTED'"))

    # 6. GL Entries Integrity (Critical: Account FK)
    if _public_table_exists(conn, "gl_entries"):
        conn.execute(text("UPDATE gl_entries SET currency = 'ILS' WHERE currency IS NULL OR TRIM(currency) = ''"))
        conn.execute(text("UPDATE gl_entries SET debit = 0 WHERE debit IS NULL"))
        conn.execute(text("UPDATE gl_entries SET credit = 0 WHERE credit IS NULL"))
        
        # التأكد من أن كل القيود تشير لحسابات موجودة
        # إذا وجدنا قيوداً لحسابات غير موجودة، نقوم بإنشائها كحسابات معلقة
        if _public_table_exists(conn, "accounts"):
            # تنظيف الفراغات أولاً لضمان المطابقة
            conn.execute(text("UPDATE gl_entries SET account = UPPER(TRIM(account)) WHERE account IS NOT NULL"))
            
            missing_accounts = _fetch_rows(conn, """
                SELECT DISTINCT e.account 
                FROM gl_entries e 
                LEFT JOIN accounts a ON UPPER(TRIM(e.account)) = UPPER(TRIM(a.code))
                WHERE a.code IS NULL AND e.account IS NOT NULL AND e.account != ''
            """)
            for row in missing_accounts:
                missing_code = row[0]
                if missing_code:
                    with open("upgrade_debug.log", "a") as log:
                        log.write(f"FIXING_MISSING_ACCOUNT_IN_GL: {missing_code}\n")
                    print(f"FIXING_MISSING_ACCOUNT_IN_GL: {missing_code}")
                    # محاولة معرفة النوع من الكود (أول رقم)

                    act_type = 'EXPENSE'
                    if missing_code.startswith('1'): act_type = 'ASSET'
                    elif missing_code.startswith('2'): act_type = 'LIABILITY'
                    elif missing_code.startswith('3'): act_type = 'EQUITY'
                    elif missing_code.startswith('4'): act_type = 'REVENUE'
                    
                    conn.execute(
                        text("""
                            INSERT INTO accounts (code, name, type, is_active, created_at, updated_at)
                            VALUES (:code, :name, :type, false, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                            ON CONFLICT (code) DO NOTHING
                        """),
                        {"code": missing_code, "name": f"حساب مرحل تلقائي {missing_code}", "type": act_type}
                    )
    
    _ensure_settlements_integrity(conn)


def _deep_clean_and_optimize(conn):
    """تحسين عميق للبيانات وإصلاح المشاكل المنطقية (Business Logic Fixes)"""
    print("Running _deep_clean_and_optimize...")
    
    # 1. Orphaned Records Cleanup (Delete children without parents)
    # -----------------------------------------------------------
    orphans_map = [
        ("sale_lines", "sale_id", "sales", "id"),
        ("invoice_lines", "invoice_id", "invoices", "id"),
        ("payment_splits", "payment_id", "payments", "id"),
        ("stock_movements", "product_id", "products", "id"),
        ("product_ratings", "product_id", "products", "id"),
    ]
    
    for child_table, fk_col, parent_table, pk_col in orphans_map:
        if _public_table_exists(conn, child_table) and _public_table_exists(conn, parent_table):
            sql = f"""
            DELETE FROM {child_table}
            WHERE {fk_col} IS NOT NULL 
              AND {fk_col} NOT IN (SELECT {pk_col} FROM {parent_table})
            """
            result = conn.execute(text(sql))
            if result.rowcount > 0:
                print(f"CLEANED_ORPHANS: Deleted {result.rowcount} rows from {child_table}")

    # 2. Standardize Statuses (Uppercase)
    # -----------------------------------------------------------
    status_tables = ["sales", "payments", "invoices", "service_requests", "projects", "tasks"]
    for table in status_tables:
        if _public_table_exists(conn, table) and _has_column(conn, table, "status"):
            conn.execute(text(f"UPDATE {table} SET status = UPPER(TRIM(status)) WHERE status IS NOT NULL"))

    # 3. Recalculate Logic (Safe Fixes)
    # -----------------------------------------------------------
    
    # A. Sales: Remaining Amount = Total - Paid
    if _public_table_exists(conn, "sales"):
        if _has_column(conn, "sales", "remaining_amount") and _has_column(conn, "sales", "total_amount") and _has_column(conn, "sales", "paid_amount"):
            conn.execute(text("""
                UPDATE sales 
                SET remaining_amount = total_amount - paid_amount
                WHERE abs(remaining_amount - (total_amount - paid_amount)) > 0.01
            """))
        
    # B. Invoices: Balance = Total - Paid
    if _public_table_exists(conn, "invoices"):
        # If columns exist
        if _has_column(conn, "invoices", "total_amount") and _has_column(conn, "invoices", "paid_amount") and _has_column(conn, "invoices", "balance_due"):
             conn.execute(text("""
                UPDATE invoices 
                SET balance_due = total_amount - paid_amount
                WHERE abs(balance_due - (total_amount - paid_amount)) > 0.01
            """))

    # 4. Date Logic Fixes
    # -----------------------------------------------------------
    # Ensure updated_at >= created_at
    tables_with_dates = ["users", "products", "customers", "suppliers", "sales", "payments"]
    for table in tables_with_dates:
        if _public_table_exists(conn, table) and _has_column(conn, table, "created_at") and _has_column(conn, table, "updated_at"):
            conn.execute(text(f"UPDATE {table} SET updated_at = created_at WHERE updated_at < created_at"))

    # 5. User Roles Integrity
    # -----------------------------------------------------------
    # If a user has no role, maybe we should warn or assign default?
    # For now, let's just ensure active users have valid data
    if _public_table_exists(conn, "users"):
        conn.execute(text("UPDATE users SET is_active = true WHERE is_active IS NULL"))


def _ensure_settlements_integrity(conn):
    """ضمان سلامة بيانات التسويات (موردين وشركاء) وحسابات الأرصدة"""
    print("Running _ensure_settlements_integrity...")
    
    # 1. Supplier Settlements
    if _public_table_exists(conn, "supplier_settlements"):
        # تصحيح الحقول الأساسية
        conn.execute(text("UPDATE supplier_settlements SET currency = 'ILS' WHERE currency IS NULL OR TRIM(currency) = ''"))
        conn.execute(text("UPDATE supplier_settlements SET status = 'DRAFT' WHERE status IS NULL OR TRIM(status) = ''"))
        conn.execute(text("UPDATE supplier_settlements SET mode = 'ON_RECEIPT' WHERE mode IS NULL OR TRIM(mode) = ''"))
        
        # تصحيح الأرصدة والمجاميع
        zeros = ["total_gross", "total_due", "opening_balance", "closing_balance", 
                 "rights_exchange", "rights_total", "obligations_sales", "obligations_services", 
                 "obligations_preorders", "obligations_expenses", "obligations_total", 
                 "payments_out", "payments_in", "payments_returns", "payments_net"]
        for col in zeros:
             if _has_column(conn, "supplier_settlements", col):
                 conn.execute(text(f"UPDATE supplier_settlements SET {col} = 0 WHERE {col} IS NULL"))
    
    if _public_table_exists(conn, "supplier_settlement_lines"):
        conn.execute(text("UPDATE supplier_settlement_lines SET gross_amount = 0 WHERE gross_amount IS NULL"))
        conn.execute(text("UPDATE supplier_settlement_lines SET quantity = 0 WHERE quantity IS NULL"))
        conn.execute(text("UPDATE supplier_settlement_lines SET unit_price = 0 WHERE unit_price IS NULL"))

    # 2. Partner Settlements
    if _public_table_exists(conn, "partner_settlements"):
        conn.execute(text("UPDATE partner_settlements SET currency = 'ILS' WHERE currency IS NULL OR TRIM(currency) = ''"))
        conn.execute(text("UPDATE partner_settlements SET status = 'DRAFT' WHERE status IS NULL OR TRIM(status) = ''"))
        
        p_zeros = ["total_gross", "total_share", "total_costs", "total_due", 
                   "opening_balance", "closing_balance", "rights_inventory", "rights_sales_share", 
                   "rights_preorders", "rights_total", "obligations_sales_to_partner", 
                   "obligations_services", "obligations_damaged", "obligations_expenses", 
                   "obligations_returns", "obligations_total", "payments_out", "payments_in", "payments_net"]
        for col in p_zeros:
            if _has_column(conn, "partner_settlements", col):
                conn.execute(text(f"UPDATE partner_settlements SET {col} = 0 WHERE {col} IS NULL"))

    if _public_table_exists(conn, "partner_settlement_lines"):
        conn.execute(text("UPDATE partner_settlement_lines SET gross_amount = 0 WHERE gross_amount IS NULL"))
        conn.execute(text("UPDATE partner_settlement_lines SET share_amount = 0 WHERE share_amount IS NULL"))
        conn.execute(text("UPDATE partner_settlement_lines SET share_percent = 0 WHERE share_percent IS NULL"))

    # 3. Opening Balances Integrity
    if _public_table_exists(conn, "partners"):
        if _has_column(conn, "partners", "opening_balance"):
            conn.execute(text("UPDATE partners SET opening_balance = 0 WHERE opening_balance IS NULL"))
    
    if _public_table_exists(conn, "suppliers"):
        if _has_column(conn, "suppliers", "opening_balance"):
            conn.execute(text("UPDATE suppliers SET opening_balance = 0 WHERE opening_balance IS NULL"))
            
    # 4. Exchange & Stock Integrity
    # التأكد من عدم وجود null في أرصدة التبادل
    if _public_table_exists(conn, "suppliers") and _has_column(conn, "suppliers", "exchange_items_balance"):
        conn.execute(text("UPDATE suppliers SET exchange_items_balance = 0 WHERE exchange_items_balance IS NULL"))
        
    if _public_table_exists(conn, "stock_levels"):
        conn.execute(text("UPDATE stock_levels SET quantity = 0 WHERE quantity IS NULL"))
        conn.execute(text("UPDATE stock_levels SET reserved_quantity = 0 WHERE reserved_quantity IS NULL"))





def _ensure_timestamp_tz(conn):
    """
    Ensure all TIMESTAMP columns are TIMESTAMP WITH TIME ZONE (TIMESTAMPTZ).
    This guarantees rigorous time handling across timezones.
    """
    with open("upgrade_debug.log", "a") as log:
        log.write("Running _ensure_timestamp_tz...\n")
    
    # Find all columns that are TIMESTAMP WITHOUT TIME ZONE
    sql = """
    SELECT table_name, column_name 
    FROM information_schema.columns 
    WHERE table_schema = 'public' 
      AND data_type = 'timestamp without time zone'
    """
    columns = _fetch_rows(conn, sql)
    
    for row in columns:
        table, col = row
        # Skip migration tables or temp tables if any
        if table.startswith('alembic'): continue
        
        try:
            # We assume current data is UTC (or server local time which we treat as the base)
            # Using 'AT TIME ZONE "UTC"' converts the naive timestamp to a TZ-aware timestamp at UTC.
            # Example: 2023-01-01 12:00:00 (Naive) -> 2023-01-01 12:00:00+00 (Aware)
            conn.execute(text(f'ALTER TABLE "{table}" ALTER COLUMN "{col}" TYPE TIMESTAMP WITH TIME ZONE USING "{col}" AT TIME ZONE \'UTC\''))
            print(f"FIXED_TIMESTAMP_TZ: {table}.{col} -> TIMESTAMPTZ")
            with open("upgrade_debug.log", "a") as log:
                log.write(f"FIXED_TIMESTAMP_TZ: {table}.{col} -> TIMESTAMPTZ\n")
        except Exception as e:
            print(f"FAILED_TIMESTAMP_TZ: {table}.{col} - {e}")
            with open("upgrade_debug.log", "a") as log:
                log.write(f"FAILED_TIMESTAMP_TZ: {table}.{col} - {e}\n")


def _ensure_column_lengths(conn):
    """Ensure critical columns have enough length for Enum values"""
    with open("upgrade_debug.log", "a") as log:
        log.write("Running _ensure_column_lengths...\n")
        
        # List of (Table, Column, Type)
        columns_to_fix = [
            # Original Critical Fixes
            ("sales", "status", "VARCHAR(50)"),
            ("sales", "payment_status", "VARCHAR(50)"),
            ("sales", "sale_number", "VARCHAR(50)"),
            ("payments", "status", "VARCHAR(50)"),
            ("payments", "method", "VARCHAR(50)"),
            ("preorders", "status", "VARCHAR(50)"),
            ("preorders", "payment_method", "VARCHAR(50)"),
            ("service_requests", "status", "VARCHAR(50)"),
            ("suppliers", "status", "VARCHAR(50)"),
            ("customers", "status", "VARCHAR(50)"),
            ("partners", "status", "VARCHAR(50)"),
            ("supplier_settlements", "status", "VARCHAR(50)"),
            ("supplier_settlements", "mode", "VARCHAR(50)"),
            ("partner_settlements", "status", "VARCHAR(50)"),
            
            # 🔴 CRITICAL AUDIT FINDINGS (Status Columns)
            ("bank_reconciliations", "status", "VARCHAR(50)"),
            ("bank_statements", "status", "VARCHAR(50)"),
            ("budget_commitments", "status", "VARCHAR(50)"),
            ("checks", "status", "VARCHAR(50)"),
            ("cost_allocation_executions", "status", "VARCHAR(50)"),
            ("deletion_logs", "status", "VARCHAR(50)"),
            ("engineering_tasks", "status", "VARCHAR(50)"),
            ("engineering_timesheets", "status", "VARCHAR(50)"),
            ("fixed_assets", "status", "VARCHAR(50)"),
            ("gl_batches", "status", "VARCHAR(50)"),
            ("notification_logs", "status", "VARCHAR(50)"),
            ("online_carts", "status", "VARCHAR(50)"),
            ("online_payments", "status", "VARCHAR(50)"),
            ("online_preorders", "status", "VARCHAR(50)"),
            ("online_preorders", "payment_status", "VARCHAR(50)"),
            ("project_change_orders", "status", "VARCHAR(50)"),
            ("project_issues", "status", "VARCHAR(50)"),
            ("project_milestones", "status", "VARCHAR(50)"),
            ("project_phases", "status", "VARCHAR(50)"),
            ("project_resources", "status", "VARCHAR(50)"),
            ("project_risks", "status", "VARCHAR(50)"),
            ("project_tasks", "status", "VARCHAR(50)"),
            ("projects", "status", "VARCHAR(50)"),
            ("recurring_invoice_schedules", "status", "VARCHAR(50)"),
            ("saas_invoices", "status", "VARCHAR(50)"),
            ("saas_subscriptions", "status", "VARCHAR(50)"),
            ("sale_returns", "status", "VARCHAR(50)"),
            ("shipments", "status", "VARCHAR(50)"),
            ("workflow_instances", "status", "VARCHAR(50)"),

            # ⚠️ WARNING FINDINGS (Codes & Types)
            ("accounts", "type", "VARCHAR(50)"),
            ("bank_accounts", "code", "VARCHAR(50)"),
            ("bank_accounts", "gl_account_code", "VARCHAR(50)"),
            ("bank_accounts", "swift_code", "VARCHAR(50)"),
            ("branches", "code", "VARCHAR(50)"),
            ("budget_commitments", "source_type", "VARCHAR(50)"),
            ("budgets", "account_code", "VARCHAR(50)"),
            ("checks", "direction", "VARCHAR(50)"),
            ("cost_allocation_rules", "allocation_method", "VARCHAR(50)"),
            ("cost_allocation_rules", "code", "VARCHAR(50)"),
            ("cost_allocation_rules", "frequency", "VARCHAR(50)"),
            ("cost_center_alert_logs", "severity", "VARCHAR(50)"),
            ("cost_center_alerts", "alert_type", "VARCHAR(50)"),
            ("cost_center_alerts", "threshold_type", "VARCHAR(50)"),
            ("cost_center_allocations", "source_type", "VARCHAR(50)"),
            ("cost_centers", "code", "VARCHAR(50)"),
            ("currencies", "code", "VARCHAR(50)"),
            ("employee_skills", "proficiency_level", "VARCHAR(50)"),
            ("engineering_tasks", "priority", "VARCHAR(50)"),
            ("engineering_tasks", "task_type", "VARCHAR(50)"),
            ("engineering_team_members", "role", "VARCHAR(50)"),
            ("engineering_teams", "code", "VARCHAR(50)"),
            ("engineering_teams", "specialty", "VARCHAR(50)"),
            ("engineering_timesheets", "productivity_rating", "VARCHAR(50)"),
            ("exchange_rates", "base_code", "VARCHAR(50)"),
            ("exchange_rates", "quote_code", "VARCHAR(50)"),
            ("exchange_transactions", "direction", "VARCHAR(50)"),
            ("fixed_asset_categories", "account_code", "VARCHAR(50)"),
            ("fixed_asset_categories", "code", "VARCHAR(50)"),
            ("fixed_asset_categories", "depreciation_account_code", "VARCHAR(50)"),
            ("fixed_asset_categories", "depreciation_method", "VARCHAR(50)"),
            ("invoices", "kind", "VARCHAR(50)"),
            ("invoices", "source", "VARCHAR(50)"),
            ("notes", "priority", "VARCHAR(50)"),
            ("partner_settlements", "code", "VARCHAR(50)"),
            ("payment_splits", "method", "VARCHAR(50)"),
            ("payments", "direction", "VARCHAR(50)"),
            ("payments", "entity_type", "VARCHAR(50)"),
            ("products", "condition", "VARCHAR(50)"),
            ("project_costs", "cost_type", "VARCHAR(50)"),
            ("project_issues", "category", "VARCHAR(50)"),
            ("project_issues", "priority", "VARCHAR(50)"),
            ("project_issues", "severity", "VARCHAR(50)"),
            ("project_resources", "resource_type", "VARCHAR(50)"),
            ("project_revenues", "revenue_type", "VARCHAR(50)"),
            ("project_risks", "category", "VARCHAR(50)"),
            ("project_risks", "impact", "VARCHAR(50)"),
            ("project_risks", "probability", "VARCHAR(50)"),
            ("project_tasks", "priority", "VARCHAR(50)"),
            ("projects", "code", "VARCHAR(50)"),
            ("sale_return_lines", "condition", "VARCHAR(50)"),
            ("sale_return_lines", "liability_party", "VARCHAR(50)"),
            ("service_requests", "priority", "VARCHAR(50)"),
            ("sites", "code", "VARCHAR(50)"),
            ("supplier_settlements", "code", "VARCHAR(50)"),
            ("transfers", "direction", "VARCHAR(50)"),
            ("warehouses", "warehouse_type", "VARCHAR(50)"),
            ("workflow_actions", "action_type", "VARCHAR(50)"),
            ("workflow_definitions", "entity_type", "VARCHAR(50)"),
            ("workflow_definitions", "workflow_type", "VARCHAR(50)"),
        ]
        
        for table, col, new_type in columns_to_fix:
            exists_table = _public_table_exists(conn, table)
            exists_col = _has_column(conn, table, col) if exists_table else False
            
            if exists_table and exists_col:
                # Check current length
                curr_len = _fetch_scalar(conn, f"SELECT character_maximum_length FROM information_schema.columns WHERE table_name = '{table}' AND column_name = '{col}'")
                log.write(f"CHECKING: {table}.{col} (Len: {curr_len})\n")
                
                try:
                    conn.execute(text(f"ALTER TABLE {table} ALTER COLUMN {col} TYPE {new_type}"))
                    log.write(f"FIXED_COLUMN_LENGTH: {table}.{col} -> {new_type}\n")
                    
                    # Verify
                    new_len = _fetch_scalar(conn, f"SELECT character_maximum_length FROM information_schema.columns WHERE table_name = '{table}' AND column_name = '{col}'")
                    log.write(f"VERIFY: {table}.{col} (Len: {new_len})\n")
                except Exception as e:
                    log.write(f"FAILED_FIX_COLUMN: {table}.{col} - {e}\n")


def _normalize_core_data(conn):
    # تم دمج معظم المنطق في _ensure_financial_integrity
    # هنا نركز على البيانات الأساسية غير المالية
    
    _run_if_column(conn, "customers", "name", "update customers set name = 'عميل غير محدد' where name is null or trim(name) = ''")
    _run_if_column(conn, "suppliers", "name", "update suppliers set name = 'مورد غير محدد' where name is null or trim(name) = ''")
    _run_if_column(conn, "partners", "name", "update partners set name = 'شريك غير محدد' where name is null or trim(name) = ''")
    
    # ضمان وجود فئات للمنتجات
    if _public_table_exists(conn, "categories") and _public_table_exists(conn, "products"):
        # إنشاء فئة افتراضية إذا لم توجد
        default_cat_id = _fetch_scalar(conn, "SELECT id FROM categories LIMIT 1")
        if not default_cat_id:
            conn.execute(text("INSERT INTO categories (name, created_at, updated_at) VALUES ('عام', NOW(), NOW())"))
            default_cat_id = _fetch_scalar(conn, "SELECT id FROM categories WHERE name = 'عام' LIMIT 1")
        
        # ربط المنتجات التي ليس لها فئة بالفئة الافتراضية
        if default_cat_id and _has_column(conn, "products", "category_id"):
            conn.execute(
                text("UPDATE products SET category_id = :cid WHERE category_id IS NULL"), 
                {"cid": default_cat_id}
            )
            
    # ✅ ضمان وجود عميل تلقائي لكل مورد وشريك (لضمان التكامل المرجعي)
    # 1. Suppliers
    if _public_table_exists(conn, "suppliers") and _public_table_exists(conn, "customers") and _has_column(conn, "suppliers", "customer_id"):
        suppliers_without_customer = _fetch_rows(conn, "SELECT id, name, phone, email, address, currency FROM suppliers WHERE customer_id IS NULL")
        for s_row in suppliers_without_customer:
            sid, sname, sphone, semail, saddr, scurr = s_row
            # البحث عن عميل موجود بنفس الهاتف
            existing_cid = None
            if sphone:
                existing_cid = _fetch_scalar(conn, "SELECT id FROM customers WHERE phone = :p LIMIT 1", {"p": sphone})
            
            if existing_cid:
                conn.execute(text("UPDATE suppliers SET customer_id = :cid WHERE id = :sid"), {"cid": existing_cid, "sid": sid})
            else:
                # إنشاء عميل جديد
                new_phone = sphone or f"SUP-{sid}-{int(datetime.now().timestamp())}"
                conn.execute(
                    text("""
                        INSERT INTO customers (name, phone, email, address, currency, category, is_active, notes, created_at, updated_at)
                        VALUES (:name, :phone, :email, :addr, :curr, 'مورد', true, :note, NOW(), NOW())
                    """),
                    {
                        "name": sname or f"Supplier {sid}",
                        "phone": new_phone,
                        "email": semail,
                        "addr": saddr,
                        "curr": scurr or 'ILS',
                        "note": f"AUTO-SUPPLIER-{sid}"
                    }
                )
                new_cid = _fetch_scalar(conn, "SELECT id FROM customers WHERE phone = :p LIMIT 1", {"p": new_phone})
                if new_cid:
                    conn.execute(text("UPDATE suppliers SET customer_id = :cid WHERE id = :sid"), {"cid": new_cid, "sid": sid})
                    print(f"AUTO_LINK_SUPPLIER: Linked Supplier #{sid} to new Customer #{new_cid}")

    # 2. Partners
    if _public_table_exists(conn, "partners") and _public_table_exists(conn, "customers") and _has_column(conn, "partners", "customer_id"):
        partners_without_customer = _fetch_rows(conn, "SELECT id, name, phone_number, email, address, currency FROM partners WHERE customer_id IS NULL")
        for p_row in partners_without_customer:
            pid, pname, pphone, pemail, paddr, pcurr = p_row
            # البحث عن عميل موجود بنفس الهاتف
            existing_cid = None
            if pphone:
                existing_cid = _fetch_scalar(conn, "SELECT id FROM customers WHERE phone = :p LIMIT 1", {"p": pphone})
            
            if existing_cid:
                conn.execute(text("UPDATE partners SET customer_id = :cid WHERE id = :pid"), {"cid": existing_cid, "pid": pid})
            else:
                # إنشاء عميل جديد
                new_phone = pphone or f"PRT-{pid}-{int(datetime.now().timestamp())}"
                conn.execute(
                    text("""
                        INSERT INTO customers (name, phone, email, address, currency, category, is_active, notes, created_at, updated_at)
                        VALUES (:name, :phone, :email, :addr, :curr, 'شريك', true, :note, NOW(), NOW())
                    """),
                    {
                        "name": pname or f"Partner {pid}",
                        "phone": new_phone,
                        "email": pemail,
                        "addr": paddr,
                        "curr": pcurr or 'ILS',
                        "note": f"AUTO-PARTNER-{pid}"
                    }
                )
                new_cid = _fetch_scalar(conn, "SELECT id FROM customers WHERE phone = :p LIMIT 1", {"p": new_phone})
                if new_cid:
                    conn.execute(text("UPDATE partners SET customer_id = :cid WHERE id = :pid"), {"cid": new_cid, "pid": pid})
                    print(f"AUTO_LINK_PARTNER: Linked Partner #{pid} to new Customer #{new_cid}")



def _normalize_extended_data(conn):
    """تنظيف شامل للبيانات وتعبئة الحقول الإجبارية الفارغة"""
    
    # 1. Customers
    if _public_table_exists(conn, "customers"):
        if _column_exists(conn, "customers", "phone"):
            # Fix empty phones
            conn.execute(text("update customers set phone = 'UNKNOWN-' || id where phone is null or trim(phone) = ''"))
            # Fix duplicate phones by appending ID
            conn.execute(text("""
                with dups as (
                    select id, row_number() over (partition by phone order by id) as rn
                    from customers
                )
                update customers c
                set phone = c.phone || '-' || c.id
                from dups d
                where c.id = d.id and d.rn > 1
            """))
            _ensure_unique_constraint(conn, "customers", "phone", "uq_customers_phone")
            
        _run_if_column(conn, "customers", "currency", "update customers set currency = 'ILS' where currency is null or trim(currency) = ''")
        _run_if_column(conn, "customers", "credit_limit", "update customers set credit_limit = 0 where credit_limit is null")
        _run_if_column(conn, "customers", "discount_rate", "update customers set discount_rate = 0 where discount_rate is null")

    # 2. Suppliers
    if _public_table_exists(conn, "suppliers"):
        if _column_exists(conn, "suppliers", "name"):
             conn.execute(text("update suppliers set name = 'مورد غير محدد - ' || id where name is null or trim(name) = ''"))
        _run_if_column(conn, "suppliers", "currency", "update suppliers set currency = 'ILS' where currency is null or trim(currency) = ''")
        _run_if_column(conn, "suppliers", "is_local", "update suppliers set is_local = true where is_local is null")

    # 3. Products
    if _public_table_exists(conn, "products"):
        if _column_exists(conn, "products", "name"):
             conn.execute(text("update products set name = 'منتج غير محدد - ' || id where name is null or trim(name) = ''"))
        _run_if_column(conn, "products", "selling_price", "update products set selling_price = 0 where selling_price is null")
        _run_if_column(conn, "products", "cost_price", "update products set cost_price = 0 where cost_price is null")
        _run_if_column(conn, "products", "stock_quantity", "update products set stock_quantity = 0 where stock_quantity is null")

    # 4. Sales & Service
    if _public_table_exists(conn, "sales"):
        _run_if_column(conn, "sales", "total_amount", "update sales set total_amount = 0 where total_amount is null")
        _run_if_column(conn, "sales", "paid_amount", "update sales set paid_amount = 0 where paid_amount is null")
        _run_if_column(conn, "sales", "remaining_amount", "update sales set remaining_amount = 0 where remaining_amount is null")

    if _public_table_exists(conn, "service_requests"):
        _run_if_column(conn, "service_requests", "total_cost", "update service_requests set total_cost = 0 where total_cost is null")
        _run_if_column(conn, "service_requests", "paid_amount", "update service_requests set paid_amount = 0 where paid_amount is null")


def _ensure_accounts_code_unique(conn):
    if not _public_table_exists(conn, "accounts") or not _column_exists(conn, "accounts", "code"):
        return
    dup_count = int(
        _fetch_scalar(
            conn,
            "select count(*) from (select code from accounts group by code having count(*) > 1) d",
        )
        or 0
    )
    if dup_count > 0:
        raise RuntimeError(f"duplicate accounts.code values: {dup_count}")
    _ensure_unique_constraint(conn, "accounts", "code", "uq_accounts_code")


def _table_exists(conn, table: str) -> bool:
    return bool(_fetch_scalar(conn, "select to_regclass(:t) is not null", {"t": table}))


def _public_table_exists(conn, table: str) -> bool:
    return _table_exists(conn, f"public.{table}")


def _column_exists(conn, table: str, column: str) -> bool:
    return _has_column(conn, table, column)


def _run_if_column(conn, table: str, column: str, sql: str) -> bool:
    if not _public_table_exists(conn, table):
        return False
    if not _column_exists(conn, table, column):
        return False
    conn.execute(text(sql))
    return True


def _acquire_upgrade_lock(conn):
    conn.execute(text("select pg_advisory_xact_lock(hashtext('garage_manager.db_upgrade_pipeline'))"))


def _ensure_missing_fk_indexes(conn):
    """إضافة فهارس تلقائية للأعمدة التي تعمل كمفاتيح أجنبية (FK) لتحسين أداء الاستعلامات"""
    sql = """
    select
        t.relname as table_name,
        a.attname as column_name,
        c.conname as constraint_name
    from pg_constraint c
    join pg_class t on c.conrelid = t.oid
    join pg_attribute a on a.attrelid = t.oid and a.attnum = any(c.conkey)
    join pg_namespace n on n.nspname = 'public' and n.oid = t.relnamespace
    where c.contype = 'f'
      and not exists (
        select 1
        from pg_index i
        where i.indrelid = t.oid
          and a.attnum = any(i.indkey)
      )
    """
    missing = _fetch_rows(conn, sql)
    for row in missing:
        table, col, con = row
        idx_name = f"idx_fk_{table}_{col}"
        # Limit index name length for Postgres
        if len(idx_name) > 63:
            idx_name = f"idx_fk_{hash(table + col) % 1000000}"
        
        try:
            conn.execute(text(f"create index if not exists {_q(idx_name)} on {_q(table)} ({_q(col)})"))
            print(f"CREATED_INDEX: {idx_name} on {table}({col})")
        except Exception as e:
            print(f"FAILED_TO_CREATE_INDEX: {idx_name} on {table} - {e}")


def _prepare_notifications_migration(conn):
    conn.execute(text("drop index if exists ix_notifications_created_at"))
    conn.execute(text("drop index if exists ix_notifications_updated_at"))
    version = _fetch_scalar(conn, "select version_num from alembic_version limit 1")
    if version != "a7b8c9d0e1f2":
        return
    has_notifications = _table_exists(conn, "public.notifications")
    has_backup = _table_exists(conn, "public.notifications_legacy_pre10f6")
    if has_notifications and not has_backup:
        conn.execute(text("alter table notifications rename to notifications_legacy_pre10f6"))


def _ensure_currencies_pk(conn):
    if not _table_exists(conn, "public.currencies"):
        return
    conn.execute(text("update currencies set code = upper(trim(code))"))
    conn.execute(text("alter table currencies alter column code set not null"))
    dup = int(_fetch_scalar(conn, "select count(*) from (select code from currencies group by code having count(*)>1) d") or 0)
    if dup > 0:
        raise RuntimeError(f"duplicate currencies.code values: {dup}")
    sql = """
    do $$
    begin
      if not exists (
        select 1 from pg_constraint where conrelid='currencies'::regclass and contype='p'
      ) then
        execute 'alter table currencies add constraint currencies_pkey primary key (code)';
      end if;
    end $$;
    """
    conn.execute(text(sql))


def _ensure_permission_bridge_pk(conn, table: str, left_col: str, right_col: str):
    if not _table_exists(conn, f"public.{table}"):
        return
    qt = _q(table)
    ql = _q(left_col)
    qr = _q(right_col)
    conn.execute(text(f"delete from {qt} a using {qt} b where a.ctid < b.ctid and a.{ql}=b.{ql} and a.{qr}=b.{qr}"))
    conn.execute(text(f"alter table {qt} alter column {ql} set not null"))
    conn.execute(text(f"alter table {qt} alter column {qr} set not null"))
    sql = f"""
    do $$
    begin
      if not exists (
        select 1 from pg_constraint where conrelid='{table}'::regclass and contype='p'
      ) then
        execute 'alter table {qt} add constraint {table}_pkey primary key ({ql}, {qr})';
      end if;
    end $$;
    """
    conn.execute(text(sql))


def _restore_notifications_data(conn):
    if not _table_exists(conn, "public.notifications_legacy_pre10f6"):
        return
    if not _table_exists(conn, "public.notifications"):
        return
    conn.execute(
        text(
            """
            insert into notifications
            (id, user_id, title, message, type, priority, data, action_url, is_read, read_at, expires_at, created_at, updated_at)
            select
                id,
                user_id,
                coalesce(title, 'تنبيه'),
                coalesce(message, ''),
                coalesce(type, 'info'),
                coalesce(priority, 'normal'),
                data,
                action_url,
                coalesce(is_read, false),
                read_at,
                expires_at,
                coalesce(created_at, now()),
                coalesce(updated_at, now())
            from notifications_legacy_pre10f6
            on conflict (id) do nothing
            """
        )
    )
    _ensure_id_sequence(conn, "notifications")


def _ensure_sale_returns_return_date(conn):
    if not _has_column(conn, "sale_returns", "return_date"):
        conn.execute(text("alter table sale_returns add column return_date timestamp"))
    conn.execute(text("create index if not exists ix_sale_returns_return_date on sale_returns (return_date)"))


def _upgrade_with_reconcile():
    try:
        upgrade()
        return
    except Exception as exc:
        with db.engine.connect() as conn:
            current = _fetch_scalar(conn, "select version_num from alembic_version limit 1")
        if current != "a7b8c9d0e1f2":
            raise
        with db.engine.begin() as conn:
            _ensure_sale_returns_return_date(conn)
        stamp(revision="94948c531c03")


def run():
    with open("upgrade_debug.log", "w") as log:
        log.write("Starting upgrade pipeline...\n")
    
    app = create_minimal_app()
    with app.app_context():
        # Step 1: Ensure Column Lengths (Critical Fix)
        try:
            with db.engine.begin() as conn:
                _ensure_column_lengths(conn)
        except Exception as e:
            with open("upgrade_debug.log", "a") as log:
                log.write(f"ERROR in step 1: {e}\n")
            print(f"ERROR in step 1: {e}")

        # Step 2: PKs and basic normalization
        with db.engine.begin() as conn:
            _acquire_upgrade_lock(conn)
            without_pk = _tables_without_pk(conn)
            for table in without_pk:
                if _has_column(conn, table, "id"):
                    _ensure_pk_on_table(conn, table)
            _normalize_users(conn)
            _ensure_default_accounts(conn)
            _ensure_accounts_code_unique(conn)
            
            with open("upgrade_debug.log", "a") as log:
                log.write("Running _ensure_financial_integrity...\n")
            _ensure_financial_integrity(conn)
            
            _normalize_core_data(conn)
            _normalize_extended_data(conn)
            _deep_clean_and_optimize(conn)

            _ensure_currencies_pk(conn)
            _ensure_permission_bridge_pk(conn, "role_permissions", "role_id", "permission_id")
            _ensure_permission_bridge_pk(conn, "user_permissions", "user_id", "permission_id")
            _ensure_missing_fk_indexes(conn)
            _prepare_notifications_migration(conn)

        _upgrade_with_reconcile()
        
        # Run column fix AFTER upgrade to ensure it persists
        with db.engine.begin() as fix_conn:
            _ensure_column_lengths(fix_conn)
            _ensure_timestamp_tz(fix_conn)

        db.create_all()
        bootstrap_database()
        with db.engine.begin() as post_conn:
            _restore_notifications_data(post_conn)

        with db.engine.connect() as verify_conn:
            alembic_version = _fetch_scalar(verify_conn, "select version_num from alembic_version limit 1")
            print(f"ALEMBIC_VERSION={alembic_version}")
            sales_nulls = _fetch_scalar(verify_conn, "select count(*) from sales where status is null or trim(status) = ''")
            payments_nulls = _fetch_scalar(verify_conn, "select count(*) from payments where status is null or trim(status) = ''")
            service_nulls = _fetch_scalar(verify_conn, "select count(*) from service_requests where status is null or trim(status) = ''")
            print(f"SALES_STATUS_NULLS={sales_nulls}")
            print(f"PAYMENTS_STATUS_NULLS={payments_nulls}")
            print(f"SERVICE_STATUS_NULLS={service_nulls}")
            no_pk = _fetch_scalar(
                verify_conn,
                """
                select count(*)
                from (
                    select c.relname
                    from pg_class c
                    join pg_namespace n on n.oid = c.relnamespace
                    where c.relkind = 'r'
                      and n.nspname = 'public'
                      and not exists (
                        select 1 from pg_constraint pc where pc.conrelid = c.oid and pc.contype = 'p'
                      )
                ) t
                """,
            )
            print(f"TABLES_WITHOUT_PK={no_pk}")


if __name__ == "__main__":
    try:
        run()
        print("DB_UPGRADE_PIPELINE_OK")
    except SQLAlchemyError as e:
        print(f"DB_UPGRADE_PIPELINE_SQL_ERROR={e}")
        raise
    except Exception as e:
        print(f"DB_UPGRADE_PIPELINE_ERROR={e}")
        raise
