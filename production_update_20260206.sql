-- Manual production migration fallback - 2026-02-06
-- Target Alembic head: c3a0f1b8d2e4
--
-- Notes:
-- - This script uses non-CONCURRENT index creation for simplicity.
-- - Run during a maintenance window if tables are large.

BEGIN;

-- 1) Composite indexes for settlements
CREATE INDEX IF NOT EXISTS ix_exchange_supplier_dir_created_at
    ON public.exchange_transactions (supplier_id, direction, created_at);

CREATE INDEX IF NOT EXISTS ix_exchange_partner_dir_created_at
    ON public.exchange_transactions (partner_id, direction, created_at);

CREATE INDEX IF NOT EXISTS ix_pay_supplier_dir_status_date
    ON public.payments (supplier_id, direction, status, payment_date);

CREATE INDEX IF NOT EXISTS ix_pay_partner_dir_status_date
    ON public.payments (partner_id, direction, status, payment_date);

CREATE INDEX IF NOT EXISTS ix_pay_customer_dir_status_date
    ON public.payments (customer_id, direction, status, payment_date);

CREATE INDEX IF NOT EXISTS ix_expense_payee_type_entity_date
    ON public.expenses (payee_type, payee_entity_id, date);

-- 2) Expand expenses payee_type allowed values
ALTER TABLE public.expenses
    DROP CONSTRAINT IF EXISTS ck_expense_payee_type_allowed;

ALTER TABLE public.expenses
    ADD CONSTRAINT ck_expense_payee_type_allowed
    CHECK (payee_type IN ('EMPLOYEE','SUPPLIER','CUSTOMER','PARTNER','WAREHOUSE','SHIPMENT','UTILITY','OTHER'));

-- 3) Bump Alembic version (single head)
DELETE FROM public.alembic_version;
INSERT INTO public.alembic_version (version_num) VALUES ('c3a0f1b8d2e4');

COMMIT;

