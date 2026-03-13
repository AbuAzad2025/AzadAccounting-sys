# فهرس هيكل قاعدة البيانات (DB Schema)

تم التوليد في: 2026-03-13T21:07:13Z

## accounts

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('accounts_id_seq'::regclass) |
| code | VARCHAR(50) | False | - |
| name | VARCHAR(100) | False | - |
| type | VARCHAR(50) | False | - |
| is_active | BOOLEAN | False | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## alembic_version

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| version_num | VARCHAR(32) | False | - |

- **المفتاح الأساسي (PK):** version_num

## archives

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('archives_id_seq'::regclass) |
| record_type | VARCHAR(50) | False | - |
| record_id | INTEGER | False | - |
| table_name | VARCHAR(100) | False | - |
| archived_data | TEXT | False | - |
| archive_reason | VARCHAR(200) | True | - |
| archived_by | INTEGER | False | - |
| archived_at | TIMESTAMP | False | - |
| original_created_at | TIMESTAMP | True | - |
| original_updated_at | TIMESTAMP | True | - |

- **المفتاح الأساسي (PK):** id

## asset_depreciations

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('asset_depreciations_id_seq'::regclass) |
| asset_id | INTEGER | False | - |
| fiscal_year | INTEGER | False | - |
| fiscal_month | INTEGER | True | - |
| depreciation_date | DATE | False | - |
| depreciation_amount | NUMERIC(12, 2) | False | - |
| accumulated_depreciation | NUMERIC(12, 2) | False | - |
| book_value | NUMERIC(12, 2) | False | - |
| gl_batch_id | INTEGER | True | - |
| notes | TEXT | True | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## asset_maintenance

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('asset_maintenance_id_seq'::regclass) |
| asset_id | INTEGER | False | - |
| maintenance_date | DATE | False | - |
| maintenance_type | VARCHAR(100) | True | - |
| cost | NUMERIC(12, 2) | False | - |
| expense_id | INTEGER | True | - |
| description | TEXT | True | - |
| next_maintenance_date | DATE | True | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## audit_logs

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('audit_logs_id_seq'::regclass) |
| model_name | VARCHAR(100) | False | - |
| record_id | INTEGER | True | - |
| customer_id | INTEGER | True | - |
| user_id | INTEGER | True | - |
| action | VARCHAR(20) | False | - |
| old_data | TEXT | True | - |
| new_data | TEXT | True | - |
| ip_address | VARCHAR(45) | True | - |
| user_agent | VARCHAR(255) | True | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## auth_audit

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('auth_audit_id_seq'::regclass) |
| user_id | INTEGER | True | - |
| event | VARCHAR(40) | False | - |
| success | BOOLEAN | False | true |
| ip | VARCHAR(64) | True | - |
| user_agent | VARCHAR(255) | True | - |
| note | VARCHAR(255) | True | - |
| metadata | JSON | True | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## bank_accounts

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('bank_accounts_id_seq'::regclass) |
| code | VARCHAR(50) | False | - |
| name | VARCHAR(200) | False | - |
| bank_name | VARCHAR(200) | False | - |
| account_number | VARCHAR(100) | False | - |
| iban | VARCHAR(34) | True | - |
| swift_code | VARCHAR(50) | True | - |
| currency | VARCHAR(10) | False | - |
| branch_id | INTEGER | True | - |
| gl_account_code | VARCHAR(50) | False | - |
| opening_balance | NUMERIC(15, 2) | False | - |
| current_balance | NUMERIC(15, 2) | False | - |
| last_reconciled_date | DATE | True | - |
| notes | TEXT | True | - |
| is_active | BOOLEAN | False | true |
| created_by | INTEGER | True | - |
| updated_by | INTEGER | True | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## bank_reconciliations

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('bank_reconciliations_id_seq'::regclass) |
| bank_account_id | INTEGER | False | - |
| reconciliation_number | VARCHAR(50) | True | - |
| period_start | DATE | False | - |
| period_end | DATE | False | - |
| book_balance | NUMERIC(15, 2) | False | - |
| bank_balance | NUMERIC(15, 2) | False | - |
| unmatched_book_count | INTEGER | True | - |
| unmatched_bank_count | INTEGER | True | - |
| unmatched_book_amount | NUMERIC(15, 2) | True | - |
| unmatched_bank_amount | NUMERIC(15, 2) | True | - |
| reconciled_by | INTEGER | False | - |
| reconciled_at | TIMESTAMP | False | - |
| approved_by | INTEGER | True | - |
| approved_at | TIMESTAMP | True | - |
| status | VARCHAR(50) | False | - |
| notes | TEXT | True | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## bank_statements

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('bank_statements_id_seq'::regclass) |
| bank_account_id | INTEGER | False | - |
| statement_number | VARCHAR(50) | True | - |
| statement_date | DATE | False | - |
| period_start | DATE | False | - |
| period_end | DATE | False | - |
| opening_balance | NUMERIC(15, 2) | False | - |
| closing_balance | NUMERIC(15, 2) | False | - |
| total_deposits | NUMERIC(15, 2) | True | - |
| total_withdrawals | NUMERIC(15, 2) | True | - |
| file_path | VARCHAR(500) | True | - |
| imported_at | TIMESTAMP | True | - |
| imported_by | INTEGER | True | - |
| status | VARCHAR(50) | False | - |
| notes | TEXT | True | - |
| created_by | INTEGER | True | - |
| updated_by | INTEGER | True | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## bank_transactions

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('bank_transactions_id_seq'::regclass) |
| bank_account_id | INTEGER | False | - |
| statement_id | INTEGER | True | - |
| transaction_date | DATE | False | - |
| value_date | DATE | True | - |
| reference | VARCHAR(100) | True | - |
| description | TEXT | True | - |
| debit | NUMERIC(15, 2) | True | - |
| credit | NUMERIC(15, 2) | True | - |
| balance | NUMERIC(15, 2) | True | - |
| matched | BOOLEAN | False | - |
| payment_id | INTEGER | True | - |
| gl_batch_id | INTEGER | True | - |
| reconciliation_id | INTEGER | True | - |
| notes | TEXT | True | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## blocked_countries

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('blocked_countries_id_seq'::regclass) |
| country_code | VARCHAR(2) | False | - |
| reason | VARCHAR(255) | True | - |
| created_at | TIMESTAMP | True | - |
| blocked_by | INTEGER | True | - |

- **المفتاح الأساسي (PK):** id

- **المفاتيح الأجنبية (FK):**
  - blocked_countries_blocked_by_fkey: (blocked_by) → users(id)

## blocked_ips

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('blocked_ips_id_seq'::regclass) |
| ip | VARCHAR(50) | False | - |
| reason | VARCHAR(255) | True | - |
| created_at | TIMESTAMP | True | - |
| expires_at | TIMESTAMP | True | - |
| blocked_by | INTEGER | True | - |

- **المفتاح الأساسي (PK):** id

- **المفاتيح الأجنبية (FK):**
  - blocked_ips_blocked_by_fkey: (blocked_by) → users(id)

## branches

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('branches_id_seq'::regclass) |
| name | VARCHAR(120) | False | - |
| code | VARCHAR(50) | False | - |
| is_active | BOOLEAN | False | true |
| address | VARCHAR(200) | True | - |
| city | VARCHAR(100) | True | - |
| geo_lat | NUMERIC(10, 6) | True | - |
| geo_lng | NUMERIC(10, 6) | True | - |
| phone | VARCHAR(32) | True | - |
| email | VARCHAR(120) | True | - |
| manager_user_id | INTEGER | True | - |
| manager_employee_id | INTEGER | True | - |
| timezone | VARCHAR(64) | True | - |
| currency | VARCHAR(10) | False | 'ILS'::character varying |
| tax_id | VARCHAR(64) | True | - |
| notes | TEXT | True | - |
| is_archived | BOOLEAN | False | false |
| archived_at | TIMESTAMP | True | - |
| archived_by | INTEGER | True | - |
| archive_reason | VARCHAR(200) | True | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## budget_commitments

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('budget_commitments_id_seq'::regclass) |
| budget_id | INTEGER | False | - |
| source_type | VARCHAR(50) | False | - |
| source_id | INTEGER | False | - |
| committed_amount | NUMERIC(12, 2) | False | - |
| commitment_date | DATE | False | - |
| status | VARCHAR(50) | False | - |
| notes | TEXT | True | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## budgets

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('budgets_id_seq'::regclass) |
| fiscal_year | INTEGER | False | - |
| account_code | VARCHAR(50) | False | - |
| branch_id | INTEGER | True | - |
| site_id | INTEGER | True | - |
| allocated_amount | NUMERIC(12, 2) | False | - |
| notes | TEXT | True | - |
| is_active | BOOLEAN | False | true |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## checks

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('checks_id_seq'::regclass) |
| check_number | VARCHAR(100) | False | - |
| check_bank | VARCHAR(200) | False | - |
| check_date | TIMESTAMP | False | - |
| check_due_date | TIMESTAMP | False | - |
| amount | NUMERIC(12, 2) | False | - |
| currency | VARCHAR(10) | False | - |
| fx_rate_issue | NUMERIC(10, 6) | True | - |
| fx_rate_issue_source | VARCHAR(20) | True | - |
| fx_rate_issue_timestamp | TIMESTAMP | True | - |
| fx_rate_issue_base | VARCHAR(10) | True | - |
| fx_rate_issue_quote | VARCHAR(10) | True | - |
| fx_rate_cash | NUMERIC(10, 6) | True | - |
| fx_rate_cash_source | VARCHAR(20) | True | - |
| fx_rate_cash_timestamp | TIMESTAMP | True | - |
| fx_rate_cash_base | VARCHAR(10) | True | - |
| fx_rate_cash_quote | VARCHAR(10) | True | - |
| direction | VARCHAR(50) | False | - |
| status | VARCHAR(50) | False | - |
| drawer_name | VARCHAR(200) | True | - |
| drawer_phone | VARCHAR(20) | True | - |
| drawer_id_number | VARCHAR(50) | True | - |
| drawer_address | TEXT | True | - |
| payee_name | VARCHAR(200) | True | - |
| payee_phone | VARCHAR(20) | True | - |
| payee_account | VARCHAR(50) | True | - |
| notes | TEXT | True | - |
| internal_notes | TEXT | True | - |
| reference_number | VARCHAR(100) | True | - |
| status_history | TEXT | True | - |
| customer_id | INTEGER | True | - |
| supplier_id | INTEGER | True | - |
| partner_id | INTEGER | True | - |
| payment_id | INTEGER | True | - |
| created_by_id | INTEGER | False | - |
| is_archived | BOOLEAN | False | - |
| archived_at | TIMESTAMP | True | - |
| archived_by | INTEGER | True | - |
| archive_reason | VARCHAR(200) | True | - |
| resubmit_allowed_count | INTEGER | False | - |
| legal_return_allowed_count | INTEGER | False | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## cost_allocation_execution_lines

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('cost_allocation_execution_lines_id_seq'::regclass) |
| execution_id | INTEGER | False | - |
| source_cost_center_id | INTEGER | True | - |
| target_cost_center_id | INTEGER | True | - |
| amount | NUMERIC(15, 2) | False | - |
| percentage | NUMERIC(5, 2) | True | - |
| gl_batch_id | INTEGER | True | - |

- **المفتاح الأساسي (PK):** id

## cost_allocation_executions

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('cost_allocation_executions_id_seq'::regclass) |
| rule_id | INTEGER | True | - |
| execution_date | DATE | False | - |
| total_amount | NUMERIC(15, 2) | False | - |
| status | VARCHAR(50) | False | 'DRAFT'::character varying |
| gl_batch_id | INTEGER | True | - |
| notes | TEXT | True | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## cost_allocation_lines

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('cost_allocation_lines_id_seq'::regclass) |
| rule_id | INTEGER | False | - |
| target_cost_center_id | INTEGER | False | - |
| percentage | NUMERIC(5, 2) | True | - |
| fixed_amount | NUMERIC(15, 2) | True | - |
| allocation_driver | VARCHAR(100) | True | - |
| driver_value | NUMERIC(15, 2) | True | - |
| notes | TEXT | True | - |

- **المفتاح الأساسي (PK):** id

## cost_allocation_rules

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('cost_allocation_rules_id_seq'::regclass) |
| code | VARCHAR(50) | False | - |
| name | VARCHAR(200) | False | - |
| description | TEXT | True | - |
| source_cost_center_id | INTEGER | True | - |
| allocation_method | VARCHAR(50) | False | - |
| frequency | VARCHAR(50) | True | - |
| is_active | BOOLEAN | False | true |
| auto_execute | BOOLEAN | False | false |
| last_executed_at | TIMESTAMP | True | - |
| next_execution_at | TIMESTAMP | True | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## cost_center_alert_logs

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('cost_center_alert_logs_id_seq'::regclass) |
| alert_id | INTEGER | True | - |
| cost_center_id | INTEGER | True | - |
| triggered_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| trigger_value | NUMERIC(15, 2) | True | - |
| threshold_value | NUMERIC(15, 2) | True | - |
| message | TEXT | True | - |
| severity | VARCHAR(50) | True | - |
| notified_users | JSON | True | - |
| notification_sent | BOOLEAN | False | false |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## cost_center_alerts

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('cost_center_alerts_id_seq'::regclass) |
| cost_center_id | INTEGER | False | - |
| alert_type | VARCHAR(50) | False | - |
| threshold_type | VARCHAR(50) | False | 'PERCENTAGE'::character varying |
| threshold_value | NUMERIC(15, 2) | False | - |
| is_active | BOOLEAN | False | true |
| notify_manager | BOOLEAN | False | true |
| notify_emails | JSON | True | - |
| notify_users | JSON | True | - |
| last_triggered_at | TIMESTAMP | True | - |
| trigger_count | INTEGER | False | 0 |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## cost_center_allocations

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('cost_center_allocations_id_seq'::regclass) |
| cost_center_id | INTEGER | False | - |
| source_type | VARCHAR(50) | False | - |
| source_id | INTEGER | False | - |
| amount | NUMERIC(15, 2) | False | - |
| percentage | NUMERIC(5, 2) | True | - |
| allocation_date | DATE | False | - |
| notes | TEXT | True | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## cost_centers

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('cost_centers_id_seq'::regclass) |
| code | VARCHAR(50) | False | - |
| name | VARCHAR(200) | False | - |
| parent_id | INTEGER | True | - |
| description | TEXT | True | - |
| manager_id | INTEGER | True | - |
| gl_account_code | VARCHAR(50) | True | - |
| budget_amount | NUMERIC(15, 2) | True | - |
| actual_amount | NUMERIC(15, 2) | True | - |
| is_active | BOOLEAN | False | true |
| created_by | INTEGER | True | - |
| updated_by | INTEGER | True | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## currencies

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| code | VARCHAR(50) | False | - |
| name | VARCHAR(100) | False | - |
| symbol | VARCHAR(10) | True | - |
| decimals | INTEGER | False | 2 |
| is_active | BOOLEAN | False | true |

- **المفتاح الأساسي (PK):** code

## customer_loyalty

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('customer_loyalty_id_seq'::regclass) |
| customer_id | INTEGER | False | - |
| total_points | INTEGER | False | - |
| available_points | INTEGER | False | - |
| used_points | INTEGER | False | - |
| loyalty_tier | VARCHAR(50) | False | - |
| total_spent | NUMERIC(12, 2) | False | - |
| last_activity | TIMESTAMP | True | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## customer_loyalty_points

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('customer_loyalty_points_id_seq'::regclass) |
| customer_id | INTEGER | False | - |
| points | INTEGER | False | - |
| reason | VARCHAR(255) | False | - |
| type | VARCHAR(50) | False | - |
| reference_id | INTEGER | True | - |
| reference_type | VARCHAR(50) | True | - |
| expires_at | TIMESTAMP | True | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## customers

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('customers_id_seq'::regclass) |
| name | VARCHAR(100) | False | - |
| phone | VARCHAR(20) | False | - |
| whatsapp | VARCHAR(20) | True | - |
| email | VARCHAR(120) | True | - |
| address | VARCHAR(200) | True | - |
| password_hash | VARCHAR(512) | True | - |
| category | VARCHAR(20) | True | - |
| notes | TEXT | True | - |
| is_active | BOOLEAN | False | true |
| is_online | BOOLEAN | False | false |
| is_archived | BOOLEAN | False | false |
| archived_at | TIMESTAMP | True | - |
| archived_by | INTEGER | True | - |
| archive_reason | VARCHAR(200) | True | - |
| credit_limit | NUMERIC(12, 2) | False | 0 |
| discount_rate | NUMERIC(5, 2) | False | 0 |
| currency | VARCHAR(10) | False | 'ILS'::character varying |
| opening_balance | NUMERIC(12, 2) | False | 0 |
| current_balance | NUMERIC(12, 2) | False | 0 |
| sales_balance | NUMERIC(12, 2) | False | 0 |
| returns_balance | NUMERIC(12, 2) | False | 0 |
| invoices_balance | NUMERIC(12, 2) | False | 0 |
| services_balance | NUMERIC(12, 2) | False | 0 |
| preorders_balance | NUMERIC(12, 2) | False | 0 |
| online_orders_balance | NUMERIC(12, 2) | False | 0 |
| payments_in_balance | NUMERIC(12, 2) | False | 0 |
| payments_out_balance | NUMERIC(12, 2) | False | 0 |
| checks_in_balance | NUMERIC(12, 2) | False | 0 |
| checks_out_balance | NUMERIC(12, 2) | False | 0 |
| returned_checks_in_balance | NUMERIC(12, 2) | False | 0 |
| returned_checks_out_balance | NUMERIC(12, 2) | False | 0 |
| expenses_balance | NUMERIC(12, 2) | False | 0 |
| service_expenses_balance | NUMERIC(12, 2) | False | 0 |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## deletion_logs

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('deletion_logs_id_seq'::regclass) |
| deletion_type | VARCHAR(20) | False | - |
| entity_id | INTEGER | False | - |
| entity_name | VARCHAR(200) | False | - |
| status | VARCHAR(50) | False | - |
| created_at | TIMESTAMP | False | - |
| updated_at | TIMESTAMP | False | - |
| deleted_by | INTEGER | False | - |
| deletion_reason | TEXT | True | - |
| confirmation_code | VARCHAR(50) | True | - |
| deleted_data | JSON | True | - |
| related_entities | JSON | True | - |
| stock_reversals | JSON | True | - |
| accounting_reversals | JSON | True | - |
| balance_reversals | JSON | True | - |
| restored_at | TIMESTAMP | True | - |
| restored_by | INTEGER | True | - |
| restoration_notes | TEXT | True | - |

- **المفتاح الأساسي (PK):** id

## employee_advance_installments

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('employee_advance_installments_id_seq'::regclass) |
| employee_id | INTEGER | False | - |
| advance_expense_id | INTEGER | False | - |
| installment_number | INTEGER | False | - |
| total_installments | INTEGER | False | - |
| amount | NUMERIC(12, 2) | False | - |
| currency | VARCHAR(10) | False | - |
| due_date | DATE | False | - |
| paid | BOOLEAN | False | - |
| paid_date | DATE | True | - |
| paid_in_salary_expense_id | INTEGER | True | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## employee_advances

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('employee_advances_id_seq'::regclass) |
| employee_id | INTEGER | False | - |
| amount | NUMERIC(12, 2) | False | - |
| currency | VARCHAR(10) | False | - |
| advance_date | DATE | False | - |
| reason | TEXT | True | - |
| total_installments | INTEGER | False | - |
| installments_paid | INTEGER | False | - |
| fully_paid | BOOLEAN | False | - |
| notes | TEXT | True | - |
| expense_id | INTEGER | True | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## employee_deductions

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('employee_deductions_id_seq'::regclass) |
| employee_id | INTEGER | False | - |
| deduction_type | VARCHAR(50) | False | - |
| amount | NUMERIC(12, 2) | False | - |
| currency | VARCHAR(10) | False | - |
| start_date | DATE | False | - |
| end_date | DATE | True | - |
| is_active | BOOLEAN | False | - |
| notes | TEXT | True | - |
| expense_id | INTEGER | True | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## employee_skills

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('employee_skills_id_seq'::regclass) |
| employee_id | INTEGER | False | - |
| skill_id | INTEGER | False | - |
| proficiency_level | VARCHAR(50) | False | - |
| years_experience | INTEGER | False | 0 |
| certification_number | VARCHAR(100) | True | - |
| certification_authority | VARCHAR(200) | True | - |
| certification_date | DATE | True | - |
| expiry_date | DATE | True | - |
| verified_by | INTEGER | True | - |
| verification_date | DATE | True | - |
| notes | TEXT | True | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## employees

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('employees_id_seq'::regclass) |
| name | VARCHAR(100) | False | - |
| position | VARCHAR(100) | True | - |
| salary | NUMERIC(15, 2) | True | - |
| phone | VARCHAR(20) | True | - |
| email | VARCHAR(120) | True | - |
| hire_date | DATE | True | - |
| bank_name | VARCHAR(100) | True | - |
| account_number | VARCHAR(100) | True | - |
| notes | TEXT | True | - |
| currency | VARCHAR(10) | False | 'ILS'::character varying |
| branch_id | INTEGER | False | - |
| site_id | INTEGER | True | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## engineering_skills

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('engineering_skills_id_seq'::regclass) |
| code | VARCHAR(50) | False | - |
| name | VARCHAR(200) | False | - |
| name_ar | VARCHAR(200) | True | - |
| category | VARCHAR(100) | True | - |
| description | TEXT | True | - |
| is_certification_required | BOOLEAN | False | false |
| certification_validity_months | INTEGER | True | - |
| is_active | BOOLEAN | False | true |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## engineering_tasks

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('engineering_tasks_id_seq'::regclass) |
| task_number | VARCHAR(50) | False | - |
| title | VARCHAR(300) | False | - |
| description | TEXT | True | - |
| task_type | VARCHAR(50) | False | - |
| priority | VARCHAR(50) | False | 'MEDIUM'::character varying |
| status | VARCHAR(50) | False | 'PENDING'::character varying |
| assigned_team_id | INTEGER | True | - |
| assigned_to_id | INTEGER | True | - |
| required_skills | JSON | True | - |
| estimated_hours | NUMERIC(8, 2) | True | - |
| actual_hours | NUMERIC(8, 2) | False | 0 |
| estimated_cost | NUMERIC(15, 2) | True | - |
| actual_cost | NUMERIC(15, 2) | False | 0 |
| scheduled_start | TIMESTAMP | True | - |
| scheduled_end | TIMESTAMP | True | - |
| actual_start | TIMESTAMP | True | - |
| actual_end | TIMESTAMP | True | - |
| customer_id | INTEGER | True | - |
| location | VARCHAR(300) | True | - |
| equipment_needed | TEXT | True | - |
| tools_needed | TEXT | True | - |
| materials_needed | JSON | True | - |
| safety_requirements | TEXT | True | - |
| quality_standards | TEXT | True | - |
| completion_notes | TEXT | True | - |
| completion_photos | JSON | True | - |
| customer_satisfaction_rating | INTEGER | True | - |
| customer_feedback | TEXT | True | - |
| cost_center_id | INTEGER | True | - |
| project_id | INTEGER | True | - |
| service_request_id | INTEGER | True | - |
| parent_task_id | INTEGER | True | - |
| gl_batch_id | INTEGER | True | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## engineering_team_members

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('engineering_team_members_id_seq'::regclass) |
| team_id | INTEGER | False | - |
| employee_id | INTEGER | False | - |
| role | VARCHAR(50) | False | - |
| join_date | DATE | False | CURRENT_DATE |
| leave_date | DATE | True | - |
| hourly_rate | NUMERIC(10, 2) | True | - |
| is_active | BOOLEAN | False | true |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## engineering_teams

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('engineering_teams_id_seq'::regclass) |
| code | VARCHAR(50) | False | - |
| name | VARCHAR(200) | False | - |
| team_leader_id | INTEGER | True | - |
| specialty | VARCHAR(50) | False | - |
| cost_center_id | INTEGER | True | - |
| branch_id | INTEGER | True | - |
| max_concurrent_tasks | INTEGER | False | 5 |
| is_active | BOOLEAN | False | true |
| description | TEXT | True | - |
| equipment_inventory | JSON | True | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## engineering_timesheets

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('engineering_timesheets_id_seq'::regclass) |
| employee_id | INTEGER | False | - |
| task_id | INTEGER | True | - |
| work_date | DATE | False | - |
| start_time | TIME | False | - |
| end_time | TIME | False | - |
| break_duration_minutes | INTEGER | False | 0 |
| actual_work_hours | NUMERIC(5, 2) | False | - |
| billable_hours | NUMERIC(5, 2) | True | - |
| hourly_rate | NUMERIC(10, 2) | True | - |
| total_cost | NUMERIC(15, 2) | True | - |
| productivity_rating | VARCHAR(50) | True | - |
| work_description | TEXT | True | - |
| issues_encountered | TEXT | True | - |
| materials_used | JSON | True | - |
| location | VARCHAR(300) | True | - |
| status | VARCHAR(50) | False | 'DRAFT'::character varying |
| approved_by | INTEGER | True | - |
| approval_date | TIMESTAMP | True | - |
| approval_notes | TEXT | True | - |
| cost_center_id | INTEGER | True | - |
| gl_batch_id | INTEGER | True | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## equipment_types

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('equipment_types_id_seq'::regclass) |
| name | VARCHAR(100) | False | - |
| model_number | VARCHAR(100) | True | - |
| chassis_number | VARCHAR(100) | True | - |
| notes | TEXT | True | - |
| category | VARCHAR(50) | True | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## exchange_rates

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('exchange_rates_id_seq'::regclass) |
| base_code | VARCHAR(50) | False | - |
| quote_code | VARCHAR(50) | False | - |
| rate | NUMERIC(18, 8) | False | - |
| valid_from | TIMESTAMP | False | CURRENT_TIMESTAMP |
| source | VARCHAR(50) | True | - |
| is_active | BOOLEAN | False | true |

- **المفتاح الأساسي (PK):** id

## exchange_transactions

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('exchange_transactions_id_seq'::regclass) |
| product_id | INTEGER | False | - |
| warehouse_id | INTEGER | False | - |
| supplier_id | INTEGER | True | - |
| partner_id | INTEGER | True | - |
| quantity | INTEGER | False | - |
| direction | VARCHAR(50) | False | 'IN'::character varying |
| unit_cost | NUMERIC(12, 2) | True | - |
| is_priced | BOOLEAN | False | false |
| notes | TEXT | True | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## expense_types

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('expense_types_id_seq'::regclass) |
| name | VARCHAR(100) | False | - |
| description | TEXT | True | - |
| is_active | BOOLEAN | False | - |
| code | VARCHAR(50) | True | - |
| fields_meta | JSON | True | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## expenses

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('expenses_id_seq'::regclass) |
| date | TIMESTAMP | False | - |
| amount | NUMERIC(12, 2) | False | - |
| currency | VARCHAR(10) | False | - |
| fx_rate_used | NUMERIC(10, 6) | True | - |
| fx_rate_source | VARCHAR(20) | True | - |
| fx_rate_timestamp | TIMESTAMP | True | - |
| fx_base_currency | VARCHAR(10) | True | - |
| fx_quote_currency | VARCHAR(10) | True | - |
| type_id | INTEGER | False | - |
| branch_id | INTEGER | False | - |
| site_id | INTEGER | True | - |
| employee_id | INTEGER | True | - |
| customer_id | INTEGER | True | - |
| warehouse_id | INTEGER | True | - |
| partner_id | INTEGER | True | - |
| supplier_id | INTEGER | True | - |
| shipment_id | INTEGER | True | - |
| utility_account_id | INTEGER | True | - |
| stock_adjustment_id | INTEGER | True | - |
| payee_type | VARCHAR(20) | False | - |
| payee_entity_id | INTEGER | True | - |
| payee_name | VARCHAR(200) | True | - |
| beneficiary_name | VARCHAR(200) | True | - |
| paid_to | VARCHAR(200) | True | - |
| disbursed_by | VARCHAR(200) | True | - |
| period_start | DATE | True | - |
| period_end | DATE | True | - |
| payment_method | VARCHAR(20) | False | - |
| payment_details | TEXT | True | - |
| description | VARCHAR(200) | True | - |
| notes | TEXT | True | - |
| tax_invoice_number | VARCHAR(100) | True | - |
| check_number | VARCHAR(100) | True | - |
| check_bank | VARCHAR(100) | True | - |
| check_due_date | DATE | True | - |
| check_payee | VARCHAR(200) | True | - |
| bank_transfer_ref | VARCHAR(100) | True | - |
| bank_name | VARCHAR(100) | True | - |
| account_number | VARCHAR(100) | True | - |
| account_holder | VARCHAR(200) | True | - |
| card_number | VARCHAR(8) | True | - |
| card_holder | VARCHAR(120) | True | - |
| card_expiry | VARCHAR(10) | True | - |
| online_gateway | VARCHAR(50) | True | - |
| online_ref | VARCHAR(100) | True | - |
| telecom_phone_number | VARCHAR(30) | True | - |
| telecom_service_type | VARCHAR(20) | True | - |
| insurance_company_name | VARCHAR(200) | True | - |
| insurance_company_address | VARCHAR(200) | True | - |
| insurance_company_phone | VARCHAR(30) | True | - |
| marketing_company_name | VARCHAR(200) | True | - |
| marketing_company_address | VARCHAR(200) | True | - |
| marketing_coverage_details | VARCHAR(200) | True | - |
| bank_fee_bank_name | VARCHAR(200) | True | - |
| bank_fee_notes | TEXT | True | - |
| gov_fee_entity_name | VARCHAR(200) | True | - |
| gov_fee_entity_address | VARCHAR(200) | True | - |
| gov_fee_notes | TEXT | True | - |
| port_fee_port_name | VARCHAR(200) | True | - |
| port_fee_notes | TEXT | True | - |
| travel_destination | VARCHAR(200) | True | - |
| travel_reason | VARCHAR(200) | True | - |
| travel_notes | TEXT | True | - |
| shipping_company_name | VARCHAR(200) | True | - |
| shipping_notes | TEXT | True | - |
| maintenance_provider_name | VARCHAR(200) | True | - |
| maintenance_provider_address | VARCHAR(200) | True | - |
| maintenance_notes | TEXT | True | - |
| rent_property_address | VARCHAR(200) | True | - |
| rent_property_notes | TEXT | True | - |
| tech_provider_name | VARCHAR(200) | True | - |
| tech_provider_phone | VARCHAR(30) | True | - |
| tech_provider_address | VARCHAR(200) | True | - |
| tech_subscription_id | VARCHAR(100) | True | - |
| storage_property_address | VARCHAR(200) | True | - |
| storage_expected_days | INTEGER | True | - |
| storage_start_date | DATE | True | - |
| storage_notes | TEXT | True | - |
| customs_arrival_date | DATE | True | - |
| customs_departure_date | DATE | True | - |
| customs_origin | VARCHAR(200) | True | - |
| customs_port_name | VARCHAR(200) | True | - |
| customs_notes | TEXT | True | - |
| training_company_name | VARCHAR(200) | True | - |
| training_location | VARCHAR(200) | True | - |
| training_duration_days | INTEGER | True | - |
| training_participants_count | INTEGER | True | - |
| training_notes | TEXT | True | - |
| training_participants_names | TEXT | True | - |
| training_topics | TEXT | True | - |
| entertainment_duration_days | INTEGER | True | - |
| entertainment_notes | TEXT | True | - |
| bank_fee_reference | VARCHAR(100) | True | - |
| bank_fee_contact_name | VARCHAR(200) | True | - |
| bank_fee_contact_phone | VARCHAR(30) | True | - |
| gov_fee_reference | VARCHAR(100) | True | - |
| port_fee_reference | VARCHAR(100) | True | - |
| port_fee_agent_name | VARCHAR(200) | True | - |
| port_fee_agent_phone | VARCHAR(30) | True | - |
| salary_notes | TEXT | True | - |
| salary_reference | VARCHAR(100) | True | - |
| travel_duration_days | INTEGER | True | - |
| travel_start_date | DATE | True | - |
| travel_companions | TEXT | True | - |
| travel_cost_center | VARCHAR(100) | True | - |
| employee_advance_period | VARCHAR(100) | True | - |
| employee_advance_reason | VARCHAR(200) | True | - |
| employee_advance_notes | TEXT | True | - |
| shipping_date | DATE | True | - |
| shipping_reference | VARCHAR(100) | True | - |
| shipping_mode | VARCHAR(50) | True | - |
| shipping_tracking_number | VARCHAR(100) | True | - |
| maintenance_details | TEXT | True | - |
| maintenance_completion_date | DATE | True | - |
| maintenance_technician_name | VARCHAR(200) | True | - |
| import_tax_reference | VARCHAR(100) | True | - |
| import_tax_notes | TEXT | True | - |
| hospitality_type | VARCHAR(20) | True | - |
| hospitality_notes | TEXT | True | - |
| hospitality_attendees | TEXT | True | - |
| hospitality_location | VARCHAR(200) | True | - |
| telecom_notes | TEXT | True | - |
| office_supplier_name | VARCHAR(200) | True | - |
| office_notes | TEXT | True | - |
| office_items_list | TEXT | True | - |
| office_purchase_reference | VARCHAR(100) | True | - |
| home_relation_to_company | VARCHAR(100) | True | - |
| home_address | VARCHAR(200) | True | - |
| home_owner_name | VARCHAR(200) | True | - |
| home_notes | TEXT | True | - |
| home_cost_share | NUMERIC(12, 2) | True | - |
| partner_expense_reason | VARCHAR(200) | True | - |
| partner_expense_notes | TEXT | True | - |
| partner_expense_reference | VARCHAR(100) | True | - |
| supplier_expense_reason | VARCHAR(200) | True | - |
| supplier_expense_notes | TEXT | True | - |
| supplier_expense_reference | VARCHAR(100) | True | - |
| handling_notes | TEXT | True | - |
| handling_quantity | NUMERIC(12, 2) | True | - |
| handling_unit | VARCHAR(50) | True | - |
| handling_reference | VARCHAR(100) | True | - |
| fuel_vehicle_number | VARCHAR(50) | True | - |
| fuel_driver_name | VARCHAR(100) | True | - |
| fuel_usage_type | VARCHAR(20) | True | - |
| fuel_volume | NUMERIC(12, 3) | True | - |
| fuel_notes | TEXT | True | - |
| fuel_station_name | VARCHAR(200) | True | - |
| fuel_odometer_start | INTEGER | True | - |
| fuel_odometer_end | INTEGER | True | - |
| transport_beneficiary_name | VARCHAR(200) | True | - |
| transport_reason | VARCHAR(200) | True | - |
| transport_usage_type | VARCHAR(20) | True | - |
| transport_notes | TEXT | True | - |
| transport_route_details | TEXT | True | - |
| insurance_policy_number | VARCHAR(100) | True | - |
| insurance_notes | TEXT | True | - |
| legal_company_name | VARCHAR(200) | True | - |
| legal_company_address | VARCHAR(200) | True | - |
| legal_case_notes | TEXT | True | - |
| legal_case_number | VARCHAR(100) | True | - |
| legal_case_type | VARCHAR(100) | True | - |
| is_archived | BOOLEAN | False | - |
| archived_at | TIMESTAMP | True | - |
| archived_by | INTEGER | True | - |
| archive_reason | VARCHAR(200) | True | - |
| cost_center_id | INTEGER | True | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## fixed_asset_categories

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('fixed_asset_categories_id_seq'::regclass) |
| code | VARCHAR(50) | False | - |
| name | VARCHAR(100) | False | - |
| account_code | VARCHAR(50) | False | - |
| depreciation_account_code | VARCHAR(50) | False | - |
| useful_life_years | INTEGER | False | - |
| depreciation_method | VARCHAR(50) | False | - |
| depreciation_rate | NUMERIC(5, 2) | True | - |
| is_active | BOOLEAN | False | true |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## fixed_assets

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('fixed_assets_id_seq'::regclass) |
| asset_number | VARCHAR(50) | False | - |
| name | VARCHAR(200) | False | - |
| category_id | INTEGER | False | - |
| branch_id | INTEGER | True | - |
| site_id | INTEGER | True | - |
| purchase_date | DATE | False | - |
| purchase_price | NUMERIC(12, 2) | False | - |
| supplier_id | INTEGER | True | - |
| serial_number | VARCHAR(100) | True | - |
| barcode | VARCHAR(100) | True | - |
| location | VARCHAR(200) | True | - |
| status | VARCHAR(50) | False | - |
| disposal_date | DATE | True | - |
| disposal_amount | NUMERIC(12, 2) | True | - |
| disposal_notes | TEXT | True | - |
| notes | TEXT | True | - |
| is_archived | BOOLEAN | False | false |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## gl_batches

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('gl_batches_id_seq'::regclass) |
| code | VARCHAR(50) | True | - |
| source_type | VARCHAR(30) | True | - |
| source_id | INTEGER | True | - |
| purpose | VARCHAR(30) | True | - |
| memo | VARCHAR(255) | True | - |
| posted_at | TIMESTAMP | True | - |
| currency | VARCHAR(10) | False | - |
| entity_type | VARCHAR(30) | True | - |
| entity_id | INTEGER | True | - |
| status | VARCHAR(50) | False | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## gl_entries

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('gl_entries_id_seq'::regclass) |
| batch_id | INTEGER | False | - |
| account | VARCHAR(50) | False | - |
| debit | NUMERIC(12, 2) | False | - |
| credit | NUMERIC(12, 2) | False | - |
| currency | VARCHAR(10) | False | - |
| ref | VARCHAR(50) | True | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## import_runs

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('import_runs_id_seq'::regclass) |
| warehouse_id | INTEGER | True | - |
| user_id | INTEGER | True | - |
| filename | VARCHAR(255) | True | - |
| file_sha256 | VARCHAR(64) | True | - |
| dry_run | BOOLEAN | False | false |
| inserted | INTEGER | False | 0 |
| updated | INTEGER | False | 0 |
| skipped | INTEGER | False | 0 |
| errors | INTEGER | False | 0 |
| duration_ms | INTEGER | False | 0 |
| report_path | VARCHAR(255) | True | - |
| notes | VARCHAR(255) | True | - |
| meta | JSON | True | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## invoice_lines

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('invoice_lines_id_seq'::regclass) |
| invoice_id | INTEGER | False | - |
| description | VARCHAR(200) | False | - |
| quantity | DOUBLE PRECISION | False | - |
| unit_price | NUMERIC(12, 2) | False | - |
| tax_rate | NUMERIC(5, 2) | False | - |
| discount | NUMERIC(5, 2) | False | - |
| product_id | INTEGER | True | - |

- **المفتاح الأساسي (PK):** id

## invoices

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('invoices_id_seq'::regclass) |
| invoice_number | VARCHAR(50) | False | - |
| invoice_date | TIMESTAMP | False | - |
| due_date | TIMESTAMP | True | - |
| customer_id | INTEGER | False | - |
| supplier_id | INTEGER | True | - |
| partner_id | INTEGER | True | - |
| sale_id | INTEGER | True | - |
| service_id | INTEGER | True | - |
| preorder_id | INTEGER | True | - |
| source | VARCHAR(50) | False | - |
| kind | VARCHAR(50) | False | - |
| credit_for_id | INTEGER | True | - |
| refund_of_id | INTEGER | True | - |
| currency | VARCHAR(10) | False | - |
| fx_rate_used | NUMERIC(10, 6) | True | - |
| fx_rate_source | VARCHAR(20) | True | - |
| fx_rate_timestamp | TIMESTAMP | True | - |
| fx_base_currency | VARCHAR(10) | True | - |
| fx_quote_currency | VARCHAR(10) | True | - |
| total_amount | NUMERIC(12, 2) | False | - |
| tax_amount | NUMERIC(12, 2) | False | - |
| discount_amount | NUMERIC(12, 2) | False | - |
| notes | TEXT | True | - |
| terms | TEXT | True | - |
| refunded_total | NUMERIC(12, 2) | False | - |
| idempotency_key | VARCHAR(64) | True | - |
| cancelled_at | TIMESTAMP | True | - |
| cancelled_by | INTEGER | True | - |
| cancel_reason | VARCHAR(200) | True | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## notes

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('notes_id_seq'::regclass) |
| content | TEXT | False | - |
| author_id | INTEGER | True | - |
| entity_type | VARCHAR(50) | True | - |
| entity_id | VARCHAR(50) | True | - |
| is_pinned | BOOLEAN | False | false |
| priority | VARCHAR(50) | False | - |
| target_type | VARCHAR(50) | True | - |
| target_ids | TEXT | True | - |
| notification_type | VARCHAR(50) | True | - |
| notification_date | TIMESTAMP | True | - |
| is_sent | BOOLEAN | False | false |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## notification_logs

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('notification_logs_id_seq'::regclass) |
| type | VARCHAR(20) | False | - |
| recipient | VARCHAR(255) | False | - |
| subject | VARCHAR(500) | True | - |
| content | TEXT | True | - |
| status | VARCHAR(50) | False | - |
| provider_id | VARCHAR(100) | True | - |
| error_message | TEXT | True | - |
| extra_data | TEXT | True | - |
| sent_at | TIMESTAMP | True | - |
| delivered_at | TIMESTAMP | True | - |
| created_at | TIMESTAMP | False | - |
| customer_id | INTEGER | True | - |
| user_id | INTEGER | True | - |

- **المفتاح الأساسي (PK):** id

## notifications

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('notifications_id_seq'::regclass) |
| user_id | INTEGER | True | - |
| title | VARCHAR(255) | False | - |
| message | TEXT | False | - |
| type | VARCHAR(50) | False | - |
| priority | VARCHAR(20) | False | - |
| data | JSON | True | - |
| action_url | VARCHAR(500) | True | - |
| is_read | BOOLEAN | False | - |
| read_at | TIMESTAMP | True | - |
| expires_at | TIMESTAMP | True | - |
| created_at | TIMESTAMP | False | now() |
| updated_at | TIMESTAMP | False | now() |

- **المفتاح الأساسي (PK):** id

- **المفاتيح الأجنبية (FK):**
  - notifications_user_id_fkey: (user_id) → users(id)

## online_cart_items

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('online_cart_items_id_seq'::regclass) |
| cart_id | INTEGER | False | - |
| product_id | INTEGER | False | - |
| quantity | INTEGER | False | - |
| price | NUMERIC(12, 2) | False | - |
| added_at | TIMESTAMP | True | - |

- **المفتاح الأساسي (PK):** id

## online_carts

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('online_carts_id_seq'::regclass) |
| cart_id | VARCHAR(50) | True | - |
| customer_id | INTEGER | True | - |
| session_id | VARCHAR(100) | True | - |
| status | VARCHAR(50) | False | - |
| expires_at | TIMESTAMP | True | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## online_payments

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('online_payments_id_seq'::regclass) |
| payment_ref | VARCHAR(100) | True | - |
| order_id | INTEGER | False | - |
| amount | NUMERIC(12, 2) | False | - |
| currency | VARCHAR(10) | False | - |
| fx_rate_used | NUMERIC(10, 6) | True | - |
| fx_rate_source | VARCHAR(20) | True | - |
| fx_rate_timestamp | TIMESTAMP | True | - |
| fx_base_currency | VARCHAR(10) | True | - |
| fx_quote_currency | VARCHAR(10) | True | - |
| method | VARCHAR(50) | True | - |
| gateway | VARCHAR(50) | True | - |
| status | VARCHAR(50) | False | - |
| transaction_data | JSON | True | - |
| processed_at | TIMESTAMP | True | - |
| card_last4 | VARCHAR(4) | True | - |
| card_encrypted | BYTEA | True | - |
| card_expiry | VARCHAR(5) | True | - |
| cardholder_name | VARCHAR(128) | True | - |
| card_brand | VARCHAR(20) | True | - |
| card_fingerprint | VARCHAR(64) | True | - |
| payment_id | INTEGER | True | - |
| idempotency_key | VARCHAR(64) | True | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## online_preorder_items

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('online_preorder_items_id_seq'::regclass) |
| order_id | INTEGER | False | - |
| product_id | INTEGER | False | - |
| quantity | INTEGER | False | - |
| price | NUMERIC(12, 2) | False | - |

- **المفتاح الأساسي (PK):** id

## online_preorders

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('online_preorders_id_seq'::regclass) |
| order_number | VARCHAR(50) | True | - |
| customer_id | INTEGER | False | - |
| cart_id | INTEGER | True | - |
| warehouse_id | INTEGER | True | - |
| prepaid_amount | NUMERIC(12, 2) | True | - |
| total_amount | NUMERIC(12, 2) | True | - |
| base_amount | NUMERIC(12, 2) | True | - |
| tax_rate | NUMERIC(5, 2) | True | - |
| tax_amount | NUMERIC(12, 2) | True | - |
| currency | VARCHAR(10) | False | - |
| fx_rate_used | NUMERIC(10, 6) | True | - |
| fx_rate_source | VARCHAR(20) | True | - |
| fx_rate_timestamp | TIMESTAMP | True | - |
| fx_base_currency | VARCHAR(10) | True | - |
| fx_quote_currency | VARCHAR(10) | True | - |
| expected_fulfillment | TIMESTAMP | True | - |
| actual_fulfillment | TIMESTAMP | True | - |
| status | VARCHAR(50) | False | - |
| payment_status | VARCHAR(50) | False | - |
| payment_method | VARCHAR(50) | True | - |
| notes | TEXT | True | - |
| shipping_address | TEXT | True | - |
| billing_address | TEXT | True | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## partner_settlement_lines

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('partner_settlement_lines_id_seq'::regclass) |
| settlement_id | INTEGER | False | - |
| source_type | VARCHAR(30) | False | - |
| source_id | INTEGER | True | - |
| description | VARCHAR(255) | True | - |
| product_id | INTEGER | True | - |
| warehouse_id | INTEGER | True | - |
| quantity | NUMERIC(12, 3) | True | - |
| unit_price | NUMERIC(12, 2) | True | - |
| gross_amount | NUMERIC(12, 2) | True | - |
| share_percent | NUMERIC(6, 3) | True | - |
| share_amount | NUMERIC(12, 2) | True | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## partner_settlements

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('partner_settlements_id_seq'::regclass) |
| code | VARCHAR(50) | True | - |
| partner_id | INTEGER | False | - |
| from_date | TIMESTAMP | False | - |
| to_date | TIMESTAMP | False | - |
| currency | VARCHAR(10) | False | - |
| fx_rate_used | NUMERIC(10, 6) | True | - |
| fx_rate_source | VARCHAR(20) | True | - |
| fx_rate_timestamp | TIMESTAMP | True | - |
| fx_base_currency | VARCHAR(10) | True | - |
| fx_quote_currency | VARCHAR(10) | True | - |
| status | VARCHAR(50) | False | - |
| notes | TEXT | True | - |
| total_gross | NUMERIC(12, 2) | False | - |
| total_share | NUMERIC(12, 2) | False | - |
| total_costs | NUMERIC(12, 2) | False | - |
| total_due | NUMERIC(12, 2) | False | - |
| previous_settlement_id | INTEGER | True | - |
| opening_balance | NUMERIC(12, 2) | False | 0 |
| rights_inventory | NUMERIC(12, 2) | False | 0 |
| rights_sales_share | NUMERIC(12, 2) | False | 0 |
| rights_preorders | NUMERIC(12, 2) | False | 0 |
| rights_total | NUMERIC(12, 2) | False | 0 |
| obligations_sales_to_partner | NUMERIC(12, 2) | False | 0 |
| obligations_services | NUMERIC(12, 2) | False | 0 |
| obligations_damaged | NUMERIC(12, 2) | False | 0 |
| obligations_expenses | NUMERIC(12, 2) | False | 0 |
| obligations_returns | NUMERIC(12, 2) | False | 0 |
| obligations_total | NUMERIC(12, 2) | False | 0 |
| payments_out | NUMERIC(12, 2) | False | 0 |
| payments_in | NUMERIC(12, 2) | False | 0 |
| payments_net | NUMERIC(12, 2) | False | 0 |
| closing_balance | NUMERIC(12, 2) | False | 0 |
| is_approved | BOOLEAN | False | false |
| approved_by | INTEGER | True | - |
| approved_at | TIMESTAMP | True | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## partners

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('partners_id_seq'::regclass) |
| name | VARCHAR(100) | False | - |
| contact_info | VARCHAR(200) | True | - |
| identity_number | VARCHAR(100) | True | - |
| phone_number | VARCHAR(20) | True | - |
| email | VARCHAR(120) | True | - |
| address | VARCHAR(200) | True | - |
| share_percentage | NUMERIC(5, 2) | False | 0 |
| currency | VARCHAR(10) | False | 'ILS'::character varying |
| opening_balance | NUMERIC(12, 2) | False | 0 |
| current_balance | NUMERIC(12, 2) | False | 0 |
| inventory_balance | NUMERIC(12, 2) | False | 0 |
| sales_share_balance | NUMERIC(12, 2) | False | 0 |
| sales_to_partner_balance | NUMERIC(12, 2) | False | 0 |
| service_fees_balance | NUMERIC(12, 2) | False | 0 |
| preorders_to_partner_balance | NUMERIC(12, 2) | False | 0 |
| preorders_prepaid_balance | NUMERIC(12, 2) | False | 0 |
| damaged_items_balance | NUMERIC(12, 2) | False | 0 |
| payments_in_balance | NUMERIC(12, 2) | False | 0 |
| payments_out_balance | NUMERIC(12, 2) | False | 0 |
| returned_checks_in_balance | NUMERIC(12, 2) | False | 0 |
| returned_checks_out_balance | NUMERIC(12, 2) | False | 0 |
| expenses_balance | NUMERIC(12, 2) | False | 0 |
| service_expenses_balance | NUMERIC(12, 2) | False | 0 |
| notes | TEXT | True | - |
| customer_id | INTEGER | True | - |
| is_archived | BOOLEAN | False | - |
| archived_at | TIMESTAMP | True | - |
| archived_by | INTEGER | True | - |
| archive_reason | VARCHAR(200) | True | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## payment_splits

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('payment_splits_id_seq'::regclass) |
| payment_id | INTEGER | False | - |
| method | VARCHAR(50) | False | - |
| amount | NUMERIC(12, 2) | False | - |
| details | JSON | False | - |
| currency | VARCHAR(10) | False | - |
| converted_amount | NUMERIC(12, 2) | False | - |
| converted_currency | VARCHAR(10) | False | - |
| fx_rate_used | NUMERIC(10, 6) | True | - |
| fx_rate_source | VARCHAR(20) | True | - |
| fx_rate_timestamp | TIMESTAMP | True | - |
| fx_base_currency | VARCHAR(10) | True | - |
| fx_quote_currency | VARCHAR(10) | True | - |

- **المفتاح الأساسي (PK):** id

## payments

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('payments_id_seq'::regclass) |
| payment_number | VARCHAR(50) | False | - |
| payment_date | TIMESTAMP | False | - |
| subtotal | NUMERIC(12, 2) | True | - |
| tax_rate | NUMERIC(5, 2) | True | - |
| tax_amount | NUMERIC(12, 2) | True | - |
| total_amount | NUMERIC(12, 2) | False | - |
| currency | VARCHAR(10) | False | - |
| fx_rate_used | NUMERIC(10, 6) | True | - |
| fx_rate_source | VARCHAR(20) | True | - |
| fx_rate_timestamp | TIMESTAMP | True | - |
| fx_base_currency | VARCHAR(10) | True | - |
| fx_quote_currency | VARCHAR(10) | True | - |
| method | VARCHAR(50) | False | - |
| status | VARCHAR(50) | False | - |
| direction | VARCHAR(50) | False | - |
| entity_type | VARCHAR(50) | False | - |
| reference | VARCHAR(100) | True | - |
| receipt_number | VARCHAR(50) | True | - |
| notes | TEXT | True | - |
| receiver_name | VARCHAR(200) | True | - |
| deliverer_name | VARCHAR(200) | True | - |
| check_number | VARCHAR(100) | True | - |
| check_bank | VARCHAR(100) | True | - |
| check_due_date | TIMESTAMP | True | - |
| card_holder | VARCHAR(100) | True | - |
| card_expiry | VARCHAR(10) | True | - |
| card_last4 | VARCHAR(4) | True | - |
| bank_transfer_ref | VARCHAR(100) | True | - |
| created_by | INTEGER | True | - |
| customer_id | INTEGER | True | - |
| supplier_id | INTEGER | True | - |
| partner_id | INTEGER | True | - |
| shipment_id | INTEGER | True | - |
| expense_id | INTEGER | True | - |
| loan_settlement_id | INTEGER | True | - |
| sale_id | INTEGER | True | - |
| invoice_id | INTEGER | True | - |
| preorder_id | INTEGER | True | - |
| service_id | INTEGER | True | - |
| refund_of_id | INTEGER | True | - |
| idempotency_key | VARCHAR(64) | True | - |
| is_archived | BOOLEAN | False | - |
| archived_at | TIMESTAMP | True | - |
| archived_by | INTEGER | True | - |
| archive_reason | VARCHAR(200) | True | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## permissions

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('permissions_id_seq'::regclass) |
| name | VARCHAR(100) | False | - |
| code | VARCHAR(100) | True | - |
| description | VARCHAR(255) | True | - |
| name_ar | VARCHAR(120) | True | - |
| module | VARCHAR(50) | True | - |
| is_protected | BOOLEAN | False | false |
| aliases | JSON | True | - |

- **المفتاح الأساسي (PK):** id

## preorders

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('preorders_id_seq'::regclass) |
| reference | VARCHAR(50) | True | - |
| preorder_date | TIMESTAMP | True | - |
| expected_date | TIMESTAMP | True | - |
| customer_id | INTEGER | True | - |
| supplier_id | INTEGER | True | - |
| partner_id | INTEGER | True | - |
| product_id | INTEGER | False | - |
| warehouse_id | INTEGER | False | - |
| quantity | INTEGER | False | - |
| prepaid_amount | NUMERIC(12, 2) | True | 0 |
| tax_rate | NUMERIC(5, 2) | True | 0 |
| status | VARCHAR(50) | False | 'PENDING'::character varying |
| notes | TEXT | True | - |
| payment_method | VARCHAR(50) | False | 'cash'::character varying |
| currency | VARCHAR(10) | False | 'ILS'::character varying |
| fx_rate_used | NUMERIC(10, 6) | True | - |
| fx_rate_source | VARCHAR(20) | True | - |
| fx_rate_timestamp | TIMESTAMP | True | - |
| fx_base_currency | VARCHAR(10) | True | - |
| fx_quote_currency | VARCHAR(10) | True | - |
| refunded_total | NUMERIC(12, 2) | False | 0 |
| refund_of_id | INTEGER | True | - |
| idempotency_key | VARCHAR(64) | True | - |
| cancelled_at | TIMESTAMP | True | - |
| cancelled_by | INTEGER | True | - |
| cancel_reason | VARCHAR(200) | True | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## product_categories

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('product_categories_id_seq'::regclass) |
| name | VARCHAR(100) | False | - |
| parent_id | INTEGER | True | - |
| description | TEXT | True | - |
| image_url | VARCHAR(255) | True | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## product_partners

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('product_partners_id_seq'::regclass) |
| product_id | INTEGER | False | - |
| partner_id | INTEGER | False | - |
| share_percent | DOUBLE PRECISION | False | - |
| share_amount | NUMERIC(12, 2) | True | - |
| notes | TEXT | True | - |

- **المفتاح الأساسي (PK):** id

## product_rating_helpful

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('product_rating_helpful_id_seq'::regclass) |
| rating_id | INTEGER | False | - |
| customer_id | INTEGER | True | - |
| ip_address | VARCHAR(45) | True | - |
| is_helpful | BOOLEAN | False | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## product_ratings

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('product_ratings_id_seq'::regclass) |
| product_id | INTEGER | False | - |
| customer_id | INTEGER | True | - |
| rating | INTEGER | False | - |
| title | VARCHAR(255) | True | - |
| comment | TEXT | True | - |
| is_verified_purchase | BOOLEAN | False | - |
| is_approved | BOOLEAN | False | - |
| helpful_count | INTEGER | False | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## product_supplier_loans

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('product_supplier_loans_id_seq'::regclass) |
| product_id | INTEGER | False | - |
| supplier_id | INTEGER | False | - |
| loan_value | NUMERIC(12, 2) | False | - |
| deferred_price | NUMERIC(12, 2) | True | - |
| is_settled | BOOLEAN | True | - |
| partner_share_quantity | INTEGER | False | - |
| partner_share_value | NUMERIC(12, 2) | False | - |
| notes | TEXT | True | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## products

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('products_id_seq'::regclass) |
| sku | VARCHAR(50) | True | - |
| name | VARCHAR(255) | False | - |
| description | TEXT | True | - |
| part_number | VARCHAR(100) | True | - |
| brand | VARCHAR(100) | True | - |
| commercial_name | VARCHAR(100) | True | - |
| chassis_number | VARCHAR(100) | True | - |
| serial_no | VARCHAR(100) | True | - |
| barcode | VARCHAR(100) | True | - |
| unit | VARCHAR(50) | True | - |
| category_name | VARCHAR(100) | True | - |
| purchase_price | NUMERIC(12, 2) | False | 0 |
| selling_price | NUMERIC(12, 2) | False | 0 |
| cost_before_shipping | NUMERIC(12, 2) | False | 0 |
| cost_after_shipping | NUMERIC(12, 2) | False | 0 |
| unit_price_before_tax | NUMERIC(12, 2) | False | 0 |
| price | NUMERIC(12, 2) | False | 0 |
| min_price | NUMERIC(12, 2) | True | - |
| max_price | NUMERIC(12, 2) | True | - |
| tax_rate | NUMERIC(5, 2) | False | 0 |
| min_qty | INTEGER | False | 0 |
| reorder_point | INTEGER | True | - |
| image | VARCHAR(255) | True | - |
| notes | TEXT | True | - |
| condition | VARCHAR(50) | False | 'NEW'::character varying |
| origin_country | VARCHAR(50) | True | - |
| warranty_period | INTEGER | True | - |
| weight | NUMERIC(10, 2) | True | - |
| dimensions | VARCHAR(50) | True | - |
| is_active | BOOLEAN | False | true |
| is_digital | BOOLEAN | False | false |
| is_exchange | BOOLEAN | False | false |
| is_published | BOOLEAN | False | true |
| vehicle_type_id | INTEGER | True | - |
| category_id | INTEGER | True | - |
| supplier_id | INTEGER | True | - |
| supplier_international_id | INTEGER | True | - |
| supplier_local_id | INTEGER | True | - |
| online_name | VARCHAR(255) | True | - |
| online_price | NUMERIC(12, 2) | True | 0 |
| online_image | VARCHAR(255) | True | - |
| warehouse_id | INTEGER | True | - |
| currency | VARCHAR(10) | False | 'ILS'::character varying |
| fx_rate_used | NUMERIC(10, 6) | True | - |
| fx_rate_source | VARCHAR(20) | True | - |
| fx_rate_timestamp | TIMESTAMP | True | - |
| fx_base_currency | VARCHAR(10) | True | - |
| fx_quote_currency | VARCHAR(10) | True | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## project_change_orders

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('project_change_orders_id_seq'::regclass) |
| project_id | INTEGER | False | - |
| change_number | VARCHAR(50) | False | - |
| title | VARCHAR(300) | False | - |
| description | TEXT | False | - |
| requested_by | INTEGER | True | - |
| requested_date | DATE | False | - |
| reason | TEXT | True | - |
| scope_change | TEXT | True | - |
| cost_impact | NUMERIC(15, 2) | True | - |
| schedule_impact_days | INTEGER | True | - |
| status | VARCHAR(50) | False | - |
| approved_by | INTEGER | True | - |
| approved_date | DATE | True | - |
| implemented_date | DATE | True | - |
| rejection_reason | TEXT | True | - |
| notes | TEXT | True | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## project_costs

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('project_costs_id_seq'::regclass) |
| project_id | INTEGER | False | - |
| phase_id | INTEGER | True | - |
| cost_type | VARCHAR(50) | False | - |
| source_id | INTEGER | True | - |
| amount | NUMERIC(15, 2) | False | - |
| cost_date | DATE | False | - |
| description | TEXT | True | - |
| gl_batch_id | INTEGER | True | - |
| notes | TEXT | True | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## project_issues

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('project_issues_id_seq'::regclass) |
| project_id | INTEGER | False | - |
| task_id | INTEGER | True | - |
| issue_number | VARCHAR(50) | False | - |
| title | VARCHAR(300) | False | - |
| description | TEXT | False | - |
| category | VARCHAR(50) | False | - |
| severity | VARCHAR(50) | False | - |
| priority | VARCHAR(50) | False | - |
| status | VARCHAR(50) | False | - |
| reported_by | INTEGER | True | - |
| assigned_to | INTEGER | True | - |
| reported_date | DATE | False | - |
| resolved_date | DATE | True | - |
| resolution | TEXT | True | - |
| cost_impact | NUMERIC(15, 2) | True | - |
| schedule_impact_days | INTEGER | True | - |
| root_cause | TEXT | True | - |
| preventive_action | TEXT | True | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## project_milestones

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('project_milestones_id_seq'::regclass) |
| project_id | INTEGER | False | - |
| phase_id | INTEGER | True | - |
| milestone_number | VARCHAR(50) | False | - |
| name | VARCHAR(300) | False | - |
| description | TEXT | True | - |
| due_date | DATE | False | - |
| completed_date | DATE | True | - |
| billing_amount | NUMERIC(15, 2) | True | - |
| tax_rate | NUMERIC(5, 2) | True | - |
| tax_amount | NUMERIC(12, 2) | True | - |
| billing_percentage | NUMERIC(5, 2) | True | - |
| invoice_id | INTEGER | True | - |
| payment_terms_days | INTEGER | True | - |
| status | VARCHAR(50) | False | - |
| completion_criteria | TEXT | True | - |
| deliverables | JSON | True | - |
| approval_required | BOOLEAN | True | - |
| approved_by | INTEGER | True | - |
| approved_at | TIMESTAMP | True | - |
| notes | TEXT | True | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## project_phases

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('project_phases_id_seq'::regclass) |
| project_id | INTEGER | False | - |
| name | VARCHAR(200) | False | - |
| order | INTEGER | False | - |
| start_date | DATE | True | - |
| end_date | DATE | True | - |
| planned_budget | NUMERIC(15, 2) | True | - |
| actual_cost | NUMERIC(15, 2) | True | - |
| status | VARCHAR(50) | False | - |
| completion_percentage | NUMERIC(5, 2) | True | - |
| description | TEXT | True | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## project_resources

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('project_resources_id_seq'::regclass) |
| project_id | INTEGER | False | - |
| task_id | INTEGER | True | - |
| resource_type | VARCHAR(50) | False | - |
| employee_id | INTEGER | True | - |
| product_id | INTEGER | True | - |
| resource_name | VARCHAR(200) | True | - |
| quantity | NUMERIC(10, 2) | False | - |
| unit_cost | NUMERIC(12, 2) | False | - |
| total_cost | NUMERIC(15, 2) | False | - |
| allocation_date | DATE | False | - |
| start_date | DATE | True | - |
| end_date | DATE | True | - |
| hours_allocated | NUMERIC(8, 2) | True | - |
| hours_used | NUMERIC(8, 2) | True | - |
| status | VARCHAR(50) | False | - |
| notes | TEXT | True | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## project_revenues

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('project_revenues_id_seq'::regclass) |
| project_id | INTEGER | False | - |
| phase_id | INTEGER | True | - |
| revenue_type | VARCHAR(50) | False | - |
| source_id | INTEGER | True | - |
| amount | NUMERIC(15, 2) | False | - |
| revenue_date | DATE | False | - |
| description | TEXT | True | - |
| gl_batch_id | INTEGER | True | - |
| notes | TEXT | True | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## project_risks

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('project_risks_id_seq'::regclass) |
| project_id | INTEGER | False | - |
| risk_number | VARCHAR(50) | False | - |
| title | VARCHAR(300) | False | - |
| description | TEXT | False | - |
| category | VARCHAR(50) | False | - |
| probability | VARCHAR(50) | False | - |
| impact | VARCHAR(50) | False | - |
| risk_score | NUMERIC(5, 2) | False | - |
| status | VARCHAR(50) | False | - |
| mitigation_plan | TEXT | True | - |
| contingency_plan | TEXT | True | - |
| owner_id | INTEGER | True | - |
| identified_date | DATE | False | - |
| review_date | DATE | True | - |
| closed_date | DATE | True | - |
| actual_impact_cost | NUMERIC(15, 2) | True | - |
| notes | TEXT | True | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## project_tasks

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('project_tasks_id_seq'::regclass) |
| project_id | INTEGER | False | - |
| phase_id | INTEGER | True | - |
| task_number | VARCHAR(50) | False | - |
| name | VARCHAR(300) | False | - |
| description | TEXT | True | - |
| assigned_to | INTEGER | True | - |
| priority | VARCHAR(50) | False | - |
| status | VARCHAR(50) | False | - |
| start_date | DATE | False | - |
| due_date | DATE | False | - |
| completed_date | DATE | True | - |
| estimated_hours | NUMERIC(8, 2) | True | - |
| actual_hours | NUMERIC(8, 2) | True | - |
| completion_percentage | NUMERIC(5, 2) | True | - |
| depends_on | JSON | True | - |
| blocked_reason | TEXT | True | - |
| notes | TEXT | True | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## projects

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('projects_id_seq'::regclass) |
| code | VARCHAR(50) | False | - |
| name | VARCHAR(200) | False | - |
| client_id | INTEGER | True | - |
| start_date | DATE | False | - |
| end_date | DATE | True | - |
| planned_end_date | DATE | True | - |
| budget_amount | NUMERIC(15, 2) | True | - |
| estimated_cost | NUMERIC(15, 2) | True | - |
| estimated_revenue | NUMERIC(15, 2) | True | - |
| actual_cost | NUMERIC(15, 2) | True | - |
| actual_revenue | NUMERIC(15, 2) | True | - |
| cost_center_id | INTEGER | True | - |
| manager_id | INTEGER | False | - |
| branch_id | INTEGER | True | - |
| status | VARCHAR(50) | False | - |
| completion_percentage | NUMERIC(5, 2) | True | - |
| description | TEXT | True | - |
| notes | TEXT | True | - |
| is_active | BOOLEAN | False | true |
| created_by | INTEGER | True | - |
| updated_by | INTEGER | True | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## recurring_invoice_schedules

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('recurring_invoice_schedules_id_seq'::regclass) |
| template_id | INTEGER | False | - |
| invoice_id | INTEGER | True | - |
| scheduled_date | DATE | False | - |
| generated_at | TIMESTAMP | True | - |
| status | VARCHAR(50) | False | - |
| error_message | TEXT | True | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## recurring_invoice_templates

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('recurring_invoice_templates_id_seq'::regclass) |
| template_name | VARCHAR(200) | False | - |
| customer_id | INTEGER | False | - |
| description | TEXT | True | - |
| amount | NUMERIC(15, 2) | False | - |
| currency | VARCHAR(10) | False | - |
| tax_rate | NUMERIC(5, 2) | True | - |
| frequency | VARCHAR(20) | False | - |
| start_date | DATE | False | - |
| end_date | DATE | True | - |
| next_invoice_date | DATE | True | - |
| is_active | BOOLEAN | False | true |
| branch_id | INTEGER | False | - |
| site_id | INTEGER | True | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## resource_time_logs

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('resource_time_logs_id_seq'::regclass) |
| project_id | INTEGER | False | - |
| task_id | INTEGER | True | - |
| resource_id | INTEGER | True | - |
| employee_id | INTEGER | False | - |
| log_date | DATE | False | - |
| hours_worked | NUMERIC(8, 2) | False | - |
| hourly_rate | NUMERIC(10, 2) | False | - |
| total_cost | NUMERIC(12, 2) | False | - |
| description | TEXT | True | - |
| approved | BOOLEAN | True | - |
| approved_by | INTEGER | True | - |
| approved_at | TIMESTAMP | True | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## role_permissions

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| role_id | INTEGER | False | - |
| permission_id | INTEGER | False | - |

- **المفتاح الأساسي (PK):** role_id, permission_id

## roles

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('roles_id_seq'::regclass) |
| name | VARCHAR(50) | False | - |
| description | VARCHAR(200) | True | - |
| is_default | BOOLEAN | False | - |

- **المفتاح الأساسي (PK):** id

## saas_invoices

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('saas_invoices_id_seq'::regclass) |
| invoice_number | VARCHAR(50) | False | - |
| subscription_id | INTEGER | False | - |
| amount | NUMERIC(10, 2) | False | - |
| currency | VARCHAR(10) | False | - |
| status | VARCHAR(50) | False | - |
| due_date | TIMESTAMP | True | - |
| paid_at | TIMESTAMP | True | - |
| payment_method | VARCHAR(50) | True | - |
| notes | TEXT | True | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## saas_plans

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('saas_plans_id_seq'::regclass) |
| name | VARCHAR(100) | False | - |
| description | TEXT | True | - |
| price_monthly | NUMERIC(10, 2) | False | - |
| price_yearly | NUMERIC(10, 2) | True | - |
| currency | VARCHAR(10) | False | - |
| max_users | INTEGER | True | - |
| max_invoices | INTEGER | True | - |
| storage_gb | INTEGER | True | - |
| features | TEXT | True | - |
| is_active | BOOLEAN | False | true |
| is_popular | BOOLEAN | False | false |
| sort_order | INTEGER | True | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## saas_subscriptions

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('saas_subscriptions_id_seq'::regclass) |
| customer_id | INTEGER | False | - |
| plan_id | INTEGER | False | - |
| status | VARCHAR(50) | False | - |
| start_date | TIMESTAMP | False | - |
| end_date | TIMESTAMP | True | - |
| trial_end_date | TIMESTAMP | True | - |
| auto_renew | BOOLEAN | False | true |
| cancelled_at | TIMESTAMP | True | - |
| cancelled_by | INTEGER | True | - |
| cancellation_reason | TEXT | True | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## sale_lines

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('sale_lines_id_seq'::regclass) |
| sale_id | INTEGER | False | - |
| product_id | INTEGER | False | - |
| warehouse_id | INTEGER | False | - |
| quantity | INTEGER | False | - |
| unit_price | NUMERIC(12, 2) | False | - |
| discount_rate | NUMERIC(5, 2) | False | - |
| tax_rate | NUMERIC(5, 2) | False | - |
| line_receiver | VARCHAR(200) | True | - |
| note | VARCHAR(200) | True | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## sale_return_lines

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('sale_return_lines_id_seq'::regclass) |
| sale_return_id | INTEGER | False | - |
| product_id | INTEGER | False | - |
| warehouse_id | INTEGER | True | - |
| quantity | INTEGER | False | - |
| unit_price | NUMERIC(12, 2) | False | - |
| notes | VARCHAR(200) | True | - |
| condition | VARCHAR(50) | False | - |
| liability_party | VARCHAR(50) | True | - |

- **المفتاح الأساسي (PK):** id

## sale_returns

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('sale_returns_id_seq'::regclass) |
| sale_id | INTEGER | True | - |
| customer_id | INTEGER | True | - |
| warehouse_id | INTEGER | True | - |
| reason | VARCHAR(200) | True | - |
| status | VARCHAR(50) | False | - |
| notes | TEXT | True | - |
| total_amount | NUMERIC(12, 2) | False | - |
| tax_rate | NUMERIC(5, 2) | True | - |
| tax_amount | NUMERIC(12, 2) | True | - |
| currency | VARCHAR(10) | False | - |
| fx_rate_used | NUMERIC(10, 6) | True | - |
| fx_rate_source | VARCHAR(20) | True | - |
| fx_rate_timestamp | TIMESTAMP | True | - |
| fx_base_currency | VARCHAR(10) | True | - |
| fx_quote_currency | VARCHAR(10) | True | - |
| credit_note_id | INTEGER | True | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| return_date | TIMESTAMP | True | - |

- **المفتاح الأساسي (PK):** id

## sales

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('sales_id_seq'::regclass) |
| sale_number | VARCHAR(50) | True | - |
| sale_date | TIMESTAMP | False | - |
| customer_id | INTEGER | False | - |
| seller_id | INTEGER | False | - |
| seller_employee_id | INTEGER | True | - |
| preorder_id | INTEGER | True | - |
| tax_rate | NUMERIC(5, 2) | False | - |
| discount_total | NUMERIC(12, 2) | False | - |
| notes | TEXT | True | - |
| receiver_name | VARCHAR(200) | True | - |
| status | VARCHAR(50) | False | - |
| payment_status | VARCHAR(50) | False | - |
| currency | VARCHAR(10) | False | - |
| fx_rate_used | NUMERIC(10, 6) | True | - |
| fx_rate_source | VARCHAR(20) | True | - |
| fx_rate_timestamp | TIMESTAMP | True | - |
| fx_base_currency | VARCHAR(10) | True | - |
| fx_quote_currency | VARCHAR(10) | True | - |
| shipping_address | TEXT | True | - |
| billing_address | TEXT | True | - |
| shipping_cost | NUMERIC(10, 2) | False | - |
| total_amount | NUMERIC(12, 2) | False | - |
| total_paid | NUMERIC(12, 2) | False | - |
| balance_due | NUMERIC(12, 2) | False | - |
| refunded_total | NUMERIC(12, 2) | False | - |
| refund_of_id | INTEGER | True | - |
| idempotency_key | VARCHAR(64) | True | - |
| cancelled_at | TIMESTAMP | True | - |
| cancelled_by | INTEGER | True | - |
| cancel_reason | VARCHAR(200) | True | - |
| is_archived | BOOLEAN | False | - |
| archived_at | TIMESTAMP | True | - |
| archived_by | INTEGER | True | - |
| archive_reason | VARCHAR(200) | True | - |
| cost_center_id | INTEGER | True | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## service_parts

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('service_parts_id_seq'::regclass) |
| service_id | INTEGER | False | - |
| part_id | INTEGER | False | - |
| warehouse_id | INTEGER | False | - |
| quantity | INTEGER | False | - |
| unit_price | NUMERIC(10, 2) | False | - |
| discount | NUMERIC(12, 2) | True | - |
| tax_rate | NUMERIC(5, 2) | True | - |
| note | VARCHAR(200) | True | - |
| notes | TEXT | True | - |
| partner_id | INTEGER | True | - |
| share_percentage | NUMERIC(5, 2) | True | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## service_requests

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('service_requests_id_seq'::regclass) |
| service_number | VARCHAR(50) | True | - |
| customer_id | INTEGER | False | - |
| mechanic_id | INTEGER | True | - |
| vehicle_type_id | INTEGER | True | - |
| status | VARCHAR(50) | False | - |
| priority | VARCHAR(50) | False | - |
| vehicle_vrn | VARCHAR(50) | True | - |
| vehicle_model | VARCHAR(100) | True | - |
| chassis_number | VARCHAR(100) | True | - |
| engineer_notes | TEXT | True | - |
| description | TEXT | True | - |
| estimated_duration | INTEGER | True | - |
| actual_duration | INTEGER | True | - |
| estimated_cost | NUMERIC(12, 2) | True | - |
| total_cost | NUMERIC(12, 2) | True | - |
| start_time | DATE | True | - |
| end_time | DATE | True | - |
| problem_description | TEXT | True | - |
| diagnosis | TEXT | True | - |
| resolution | TEXT | True | - |
| notes | TEXT | True | - |
| received_at | TIMESTAMP | True | - |
| started_at | TIMESTAMP | True | - |
| expected_delivery | TIMESTAMP | True | - |
| completed_at | TIMESTAMP | True | - |
| currency | VARCHAR(10) | False | - |
| fx_rate_used | NUMERIC(10, 6) | True | - |
| fx_rate_source | VARCHAR(20) | True | - |
| fx_rate_timestamp | TIMESTAMP | True | - |
| fx_base_currency | VARCHAR(10) | True | - |
| fx_quote_currency | VARCHAR(10) | True | - |
| tax_rate | NUMERIC(5, 2) | True | - |
| discount_total | NUMERIC(12, 2) | True | - |
| parts_total | NUMERIC(12, 2) | True | - |
| labor_total | NUMERIC(12, 2) | True | - |
| total_amount | NUMERIC(12, 2) | True | - |
| consume_stock | BOOLEAN | False | - |
| warranty_days | INTEGER | True | - |
| refunded_total | NUMERIC(12, 2) | False | - |
| refund_of_id | INTEGER | True | - |
| idempotency_key | VARCHAR(64) | True | - |
| cancelled_at | TIMESTAMP | True | - |
| cancelled_by | INTEGER | True | - |
| cancel_reason | VARCHAR(200) | True | - |
| is_archived | BOOLEAN | False | - |
| archived_at | TIMESTAMP | True | - |
| archived_by | INTEGER | True | - |
| archive_reason | VARCHAR(200) | True | - |
| cost_center_id | INTEGER | True | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## service_tasks

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('service_tasks_id_seq'::regclass) |
| service_id | INTEGER | False | - |
| partner_id | INTEGER | True | - |
| share_percentage | NUMERIC(5, 2) | True | - |
| description | VARCHAR(200) | False | - |
| quantity | INTEGER | True | - |
| unit_price | NUMERIC(10, 2) | False | - |
| discount | NUMERIC(12, 2) | True | - |
| tax_rate | NUMERIC(5, 2) | True | - |
| note | VARCHAR(200) | True | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## shipment_items

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('shipment_items_id_seq'::regclass) |
| shipment_id | INTEGER | False | - |
| product_id | INTEGER | False | - |
| warehouse_id | INTEGER | True | - |
| quantity | INTEGER | False | - |
| unit_cost | NUMERIC(12, 2) | False | - |
| declared_value | NUMERIC(12, 2) | True | - |
| landed_extra_share | NUMERIC(12, 2) | True | - |
| landed_unit_cost | NUMERIC(12, 2) | True | - |
| notes | VARCHAR(200) | True | - |

- **المفتاح الأساسي (PK):** id

## shipment_partners

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('shipment_partners_id_seq'::regclass) |
| shipment_id | INTEGER | False | - |
| partner_id | INTEGER | False | - |
| identity_number | VARCHAR(100) | True | - |
| phone_number | VARCHAR(20) | True | - |
| address | VARCHAR(200) | True | - |
| unit_price_before_tax | NUMERIC(12, 2) | True | - |
| expiry_date | DATE | True | - |
| share_percentage | NUMERIC(5, 2) | True | - |
| share_amount | NUMERIC(12, 2) | True | - |
| notes | TEXT | True | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## shipments

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('shipments_id_seq'::regclass) |
| number | VARCHAR(50) | True | - |
| shipment_number | VARCHAR(50) | True | - |
| date | TIMESTAMP | True | - |
| shipment_date | TIMESTAMP | True | - |
| expected_arrival | TIMESTAMP | True | - |
| actual_arrival | TIMESTAMP | True | - |
| delivered_date | TIMESTAMP | True | - |
| origin | VARCHAR(100) | True | - |
| destination | VARCHAR(100) | True | - |
| destination_id | INTEGER | True | - |
| status | VARCHAR(50) | False | 'DRAFT'::character varying |
| value_before | NUMERIC(12, 2) | True | - |
| shipping_cost | NUMERIC(12, 2) | True | - |
| customs | NUMERIC(12, 2) | True | - |
| vat | NUMERIC(12, 2) | True | - |
| insurance | NUMERIC(12, 2) | True | - |
| total_cost | NUMERIC(12, 2) | True | - |
| carrier | VARCHAR(100) | True | - |
| tracking_number | VARCHAR(100) | True | - |
| notes | TEXT | True | - |
| currency | VARCHAR(10) | False | - |
| fx_rate_used | NUMERIC(10, 6) | True | - |
| fx_rate_source | VARCHAR(20) | True | - |
| fx_rate_timestamp | TIMESTAMP | True | - |
| fx_base_currency | VARCHAR(10) | True | - |
| fx_quote_currency | VARCHAR(10) | True | - |
| sale_id | INTEGER | True | - |
| weight | NUMERIC(10, 3) | True | - |
| dimensions | VARCHAR(100) | True | - |
| package_count | INTEGER | True | - |
| priority | VARCHAR(20) | True | - |
| delivery_method | VARCHAR(50) | True | - |
| delivery_instructions | TEXT | True | - |
| customs_declaration | VARCHAR(100) | True | - |
| customs_cleared_date | TIMESTAMP | True | - |
| delivery_attempts | INTEGER | True | - |
| last_delivery_attempt | TIMESTAMP | True | - |
| return_reason | TEXT | True | - |
| is_archived | BOOLEAN | False | - |
| archived_at | TIMESTAMP | True | - |
| archived_by | INTEGER | True | - |
| archive_reason | VARCHAR(200) | True | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## sites

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('sites_id_seq'::regclass) |
| branch_id | INTEGER | False | - |
| name | VARCHAR(120) | False | - |
| code | VARCHAR(50) | False | - |
| is_active | BOOLEAN | False | true |
| address | VARCHAR(200) | True | - |
| city | VARCHAR(100) | True | - |
| geo_lat | NUMERIC(10, 6) | True | - |
| geo_lng | NUMERIC(10, 6) | True | - |
| manager_user_id | INTEGER | True | - |
| manager_employee_id | INTEGER | True | - |
| notes | TEXT | True | - |
| is_archived | BOOLEAN | False | false |
| archived_at | TIMESTAMP | True | - |
| archived_by | INTEGER | True | - |
| archive_reason | VARCHAR(200) | True | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## stock_adjustment_items

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('stock_adjustment_items_id_seq'::regclass) |
| adjustment_id | INTEGER | False | - |
| product_id | INTEGER | False | - |
| warehouse_id | INTEGER | True | - |
| quantity | INTEGER | False | - |
| unit_cost | NUMERIC(12, 2) | False | - |
| notes | VARCHAR(200) | True | - |

- **المفتاح الأساسي (PK):** id

## stock_adjustments

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('stock_adjustments_id_seq'::regclass) |
| date | TIMESTAMP | False | - |
| warehouse_id | INTEGER | True | - |
| reason | VARCHAR(20) | False | - |
| notes | TEXT | True | - |
| total_cost | NUMERIC(12, 2) | False | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## stock_levels

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('stock_levels_id_seq'::regclass) |
| product_id | INTEGER | False | - |
| warehouse_id | INTEGER | False | - |
| quantity | INTEGER | False | 0 |
| reserved_quantity | INTEGER | False | 0 |
| min_stock | INTEGER | True | - |
| max_stock | INTEGER | True | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## stock_movements

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('stock_movements_id_seq'::regclass) |
| product_id | INTEGER | False | - |
| warehouse_id | INTEGER | False | - |
| quantity_change | NUMERIC(10, 2) | False | - |
| balance_after | NUMERIC(10, 2) | True | - |
| movement_type | VARCHAR(50) | False | - |
| reference_type | VARCHAR(50) | True | - |
| reference_id | INTEGER | True | - |
| notes | VARCHAR(255) | True | - |
| created_by | INTEGER | True | - |
| created_at | TIMESTAMP | False | now() |
| updated_at | TIMESTAMP | False | now() |

- **المفتاح الأساسي (PK):** id

- **المفاتيح الأجنبية (FK):**
  - stock_movements_created_by_fkey: (created_by) → users(id)
  - stock_movements_product_id_fkey: (product_id) → products(id)
  - stock_movements_warehouse_id_fkey: (warehouse_id) → warehouses(id)

## supplier_loan_settlements

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('supplier_loan_settlements_id_seq'::regclass) |
| loan_id | INTEGER | True | - |
| supplier_id | INTEGER | True | - |
| settled_price | NUMERIC(12, 2) | False | - |
| settlement_date | TIMESTAMP | True | - |
| notes | TEXT | True | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## supplier_settlement_lines

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('supplier_settlement_lines_id_seq'::regclass) |
| settlement_id | INTEGER | False | - |
| source_type | VARCHAR(30) | False | - |
| source_id | INTEGER | True | - |
| description | VARCHAR(255) | True | - |
| product_id | INTEGER | True | - |
| quantity | NUMERIC(12, 3) | True | - |
| unit_price | NUMERIC(12, 2) | True | - |
| gross_amount | NUMERIC(12, 2) | True | - |
| needs_pricing | BOOLEAN | False | - |
| cost_source | VARCHAR(20) | True | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## supplier_settlements

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('supplier_settlements_id_seq'::regclass) |
| code | VARCHAR(50) | True | - |
| supplier_id | INTEGER | False | - |
| from_date | TIMESTAMP | False | - |
| to_date | TIMESTAMP | False | - |
| currency | VARCHAR(10) | False | - |
| fx_rate_used | NUMERIC(10, 6) | True | - |
| fx_rate_source | VARCHAR(20) | True | - |
| fx_rate_timestamp | TIMESTAMP | True | - |
| fx_base_currency | VARCHAR(10) | True | - |
| fx_quote_currency | VARCHAR(10) | True | - |
| status | VARCHAR(50) | False | - |
| mode | VARCHAR(50) | False | - |
| notes | TEXT | True | - |
| total_gross | NUMERIC(12, 2) | True | - |
| total_due | NUMERIC(12, 2) | True | - |
| previous_settlement_id | INTEGER | True | - |
| opening_balance | NUMERIC(12, 2) | False | 0 |
| rights_exchange | NUMERIC(12, 2) | False | 0 |
| rights_total | NUMERIC(12, 2) | False | 0 |
| obligations_sales | NUMERIC(12, 2) | False | 0 |
| obligations_services | NUMERIC(12, 2) | False | 0 |
| obligations_preorders | NUMERIC(12, 2) | False | 0 |
| obligations_expenses | NUMERIC(12, 2) | False | 0 |
| obligations_total | NUMERIC(12, 2) | False | 0 |
| payments_out | NUMERIC(12, 2) | False | 0 |
| payments_in | NUMERIC(12, 2) | False | 0 |
| payments_returns | NUMERIC(12, 2) | False | 0 |
| payments_net | NUMERIC(12, 2) | False | 0 |
| closing_balance | NUMERIC(12, 2) | False | 0 |
| is_approved | BOOLEAN | False | false |
| approved_by | INTEGER | True | - |
| approved_at | TIMESTAMP | True | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## suppliers

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('suppliers_id_seq'::regclass) |
| name | VARCHAR(100) | False | - |
| is_local | BOOLEAN | False | true |
| identity_number | VARCHAR(100) | True | - |
| contact | VARCHAR(200) | True | - |
| phone | VARCHAR(20) | True | - |
| email | VARCHAR(120) | True | - |
| address | VARCHAR(200) | True | - |
| notes | TEXT | True | - |
| payment_terms | VARCHAR(50) | True | - |
| currency | VARCHAR(10) | False | 'ILS'::character varying |
| opening_balance | NUMERIC(12, 2) | False | 0 |
| current_balance | NUMERIC(12, 2) | False | 0 |
| exchange_items_balance | NUMERIC(12, 2) | False | 0 |
| sale_returns_balance | NUMERIC(12, 2) | False | 0 |
| sales_balance | NUMERIC(12, 2) | False | 0 |
| services_balance | NUMERIC(12, 2) | False | 0 |
| preorders_balance | NUMERIC(12, 2) | False | 0 |
| payments_in_balance | NUMERIC(12, 2) | False | 0 |
| payments_out_balance | NUMERIC(12, 2) | False | 0 |
| preorders_prepaid_balance | NUMERIC(12, 2) | False | 0 |
| returns_balance | NUMERIC(12, 2) | False | 0 |
| expenses_balance | NUMERIC(12, 2) | False | 0 |
| service_expenses_balance | NUMERIC(12, 2) | False | 0 |
| returned_checks_in_balance | NUMERIC(12, 2) | False | 0 |
| returned_checks_out_balance | NUMERIC(12, 2) | False | 0 |
| customer_id | INTEGER | True | - |
| is_archived | BOOLEAN | False | - |
| archived_at | TIMESTAMP | True | - |
| archived_by | INTEGER | True | - |
| archive_reason | VARCHAR(200) | True | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## system_settings

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('system_settings_id_seq'::regclass) |
| key | VARCHAR(100) | False | - |
| value | TEXT | True | - |
| description | TEXT | True | - |
| data_type | VARCHAR(20) | True | - |
| is_public | BOOLEAN | True | - |
| created_at | TIMESTAMP | False | - |
| updated_at | TIMESTAMP | False | - |

- **المفتاح الأساسي (PK):** id

## tax_entries

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('tax_entries_id_seq'::regclass) |
| entry_type | VARCHAR(20) | False | - |
| transaction_type | VARCHAR(50) | False | - |
| transaction_id | INTEGER | True | - |
| transaction_reference | VARCHAR(50) | True | - |
| tax_rate | NUMERIC(5, 2) | False | - |
| base_amount | NUMERIC(12, 2) | False | - |
| tax_amount | NUMERIC(12, 2) | False | - |
| total_amount | NUMERIC(12, 2) | False | - |
| currency | VARCHAR(3) | True | - |
| debit_account | VARCHAR(20) | True | - |
| credit_account | VARCHAR(20) | True | - |
| gl_entry_id | INTEGER | True | - |
| fiscal_year | INTEGER | True | - |
| fiscal_month | INTEGER | True | - |
| tax_period | VARCHAR(7) | True | - |
| is_reconciled | BOOLEAN | True | - |
| is_filed | BOOLEAN | True | - |
| filing_reference | VARCHAR(100) | True | - |
| customer_id | INTEGER | True | - |
| supplier_id | INTEGER | True | - |
| notes | TEXT | True | - |
| created_at | TIMESTAMP | False | - |
| created_by | INTEGER | True | - |

- **المفتاح الأساسي (PK):** id

## transfers

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('transfers_id_seq'::regclass) |
| reference | VARCHAR(50) | True | - |
| product_id | INTEGER | False | - |
| source_id | INTEGER | False | - |
| destination_id | INTEGER | False | - |
| quantity | INTEGER | False | - |
| direction | VARCHAR(50) | False | - |
| transfer_date | TIMESTAMP | True | - |
| notes | TEXT | True | - |
| user_id | INTEGER | True | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## user_branches

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('user_branches_id_seq'::regclass) |
| user_id | INTEGER | False | - |
| branch_id | INTEGER | False | - |
| is_primary | BOOLEAN | False | - |
| can_manage | BOOLEAN | False | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## user_permissions

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| user_id | INTEGER | False | - |
| permission_id | INTEGER | False | - |

- **المفتاح الأساسي (PK):** user_id, permission_id

## users

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('users_id_seq'::regclass) |
| username | VARCHAR(50) | False | - |
| email | VARCHAR(120) | False | - |
| password_hash | VARCHAR(255) | False | - |
| role_id | INTEGER | True | - |
| is_active | BOOLEAN | False | true |
| is_system_account | BOOLEAN | False | false |
| last_login | TIMESTAMP | True | - |
| last_seen | TIMESTAMP | True | - |
| last_login_ip | VARCHAR(64) | True | - |
| login_count | INTEGER | False | 0 |
| avatar_url | VARCHAR(500) | True | - |
| notes_text | TEXT | True | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## utility_accounts

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('utility_accounts_id_seq'::regclass) |
| utility_type | VARCHAR(20) | False | - |
| provider | VARCHAR(120) | False | - |
| account_no | VARCHAR(100) | True | - |
| meter_no | VARCHAR(100) | True | - |
| alias | VARCHAR(120) | True | - |
| is_active | BOOLEAN | False | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## warehouse_partner_shares

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('warehouse_partner_shares_id_seq'::regclass) |
| partner_id | INTEGER | False | - |
| warehouse_id | INTEGER | True | - |
| product_id | INTEGER | True | - |
| share_percentage | DOUBLE PRECISION | False | - |
| share_amount | NUMERIC(12, 2) | True | - |
| notes | TEXT | True | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## warehouses

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('warehouses_id_seq'::regclass) |
| name | VARCHAR(100) | False | - |
| warehouse_type | VARCHAR(50) | False | 'MAIN'::character varying |
| location | VARCHAR(200) | True | - |
| branch_id | INTEGER | True | - |
| is_active | BOOLEAN | False | true |
| parent_id | INTEGER | True | - |
| supplier_id | INTEGER | True | - |
| partner_id | INTEGER | True | - |
| share_percent | NUMERIC(5, 2) | True | 0 |
| capacity | INTEGER | True | - |
| current_occupancy | INTEGER | True | 0 |
| notes | TEXT | True | - |
| online_slug | VARCHAR(150) | True | - |
| online_is_default | BOOLEAN | False | false |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## workflow_actions

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('workflow_actions_id_seq'::regclass) |
| workflow_instance_id | INTEGER | False | - |
| step_number | INTEGER | False | - |
| step_name | VARCHAR(200) | False | - |
| action_type | VARCHAR(50) | False | - |
| actor_id | INTEGER | False | - |
| action_date | TIMESTAMP | False | - |
| decision | VARCHAR(50) | True | - |
| comments | TEXT | True | - |
| attachments | JSON | True | - |
| delegated_to | INTEGER | True | - |
| delegated_at | TIMESTAMP | True | - |
| duration_hours | NUMERIC(8, 2) | True | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## workflow_definitions

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('workflow_definitions_id_seq'::regclass) |
| workflow_code | VARCHAR(50) | False | - |
| workflow_name | VARCHAR(200) | False | - |
| workflow_name_ar | VARCHAR(200) | True | - |
| description | TEXT | True | - |
| workflow_type | VARCHAR(50) | False | - |
| entity_type | VARCHAR(50) | False | - |
| steps_definition | JSON | False | - |
| auto_start | BOOLEAN | False | - |
| auto_start_condition | JSON | True | - |
| is_active | BOOLEAN | False | - |
| version | INTEGER | False | - |
| timeout_hours | INTEGER | True | - |
| escalation_rules | JSON | True | - |
| created_by | INTEGER | True | - |
| updated_by | INTEGER | True | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id

## workflow_instances

| العمود | النوع | nullable | default |
|--------|-------|----------|---------|
| id | INTEGER | False | nextval('workflow_instances_id_seq'::regclass) |
| workflow_definition_id | INTEGER | False | - |
| instance_code | VARCHAR(50) | False | - |
| entity_type | VARCHAR(50) | False | - |
| entity_id | INTEGER | False | - |
| status | VARCHAR(50) | False | - |
| current_step | INTEGER | False | - |
| total_steps | INTEGER | False | - |
| started_by | INTEGER | False | - |
| started_at | TIMESTAMP | False | - |
| completed_at | TIMESTAMP | True | - |
| completed_by | INTEGER | True | - |
| cancelled_at | TIMESTAMP | True | - |
| cancelled_by | INTEGER | True | - |
| cancellation_reason | TEXT | True | - |
| due_date | TIMESTAMP | True | - |
| context_data | JSON | True | - |
| created_at | TIMESTAMP | False | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | False | CURRENT_TIMESTAMP |

- **المفتاح الأساسي (PK):** id
