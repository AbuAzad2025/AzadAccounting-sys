# فهرس فهارس قاعدة البيانات (Indexes)

تم التوليد في: 2026-03-13T21:07:13Z

| الجدول | اسم الفهرس | الأعمدة | Unique |
|--------|------------|---------|--------|
| accounts | uq_accounts_code | code | True |
| blocked_countries | idx_fk_blocked_countries_blocked_by | blocked_by | False |
| blocked_countries | ix_blocked_countries_country_code | country_code | True |
| blocked_ips | idx_fk_blocked_ips_blocked_by | blocked_by | False |
| blocked_ips | ix_blocked_ips_ip | ip | True |
| checks | gin_checks_check_number_trgm | check_number | False |
| checks | idx_checks_customer_date | customer_id, check_date | False |
| checks | idx_checks_payment | payment_id | False |
| checks | idx_checks_ref | reference_number | False |
| checks | idx_checks_status | status | False |
| checks | ix_checks_check_date | check_date | False |
| checks | ix_checks_check_date_status | check_date, status | False |
| checks | ix_checks_customer_id_date | customer_id, check_date | False |
| checks | ix_checks_date_pending | check_date | False |
| checks | ix_checks_direction | direction | False |
| checks | ix_checks_is_archived_status | is_archived, status | False |
| checks | ix_checks_partner_id_date | partner_id, check_date | False |
| checks | ix_checks_payment_id | payment_id | False |
| checks | ix_checks_payment_id_status | payment_id, status | False |
| checks | ix_checks_status | status | False |
| checks | ix_checks_status_due_date_direction | status, check_due_date, direction | False |
| checks | ix_checks_supplier_id_date | supplier_id, check_date | False |
| customers | gin_customers_name_trgm | name | False |
| customers | ix_customers_category | category | False |
| customers | ix_customers_created_at | created_at | False |
| customers | ix_customers_current_balance | current_balance | False |
| customers | ix_customers_is_active | is_active | False |
| customers | ix_customers_is_archived | is_archived | False |
| customers | ix_customers_is_online | is_online | False |
| customers | ix_customers_lower_email | <UNKNOWN> | False |
| customers | ix_customers_name | name | False |
| customers | ix_customers_phone | phone | False |
| customers | uq_customers_phone | phone | True |
| expenses | idx_expenses_customer_date | customer_id, date | False |
| gl_batches | ix_gl_batches_posted_at | posted_at | False |
| gl_batches | ix_gl_batches_status | status | False |
| invoices | idx_invoices_customer_date | customer_id, invoice_date | False |
| invoices | ix_invoices_customer_date | customer_id, invoice_date | False |
| invoices | ix_invoices_customer_id | customer_id | False |
| invoices | ix_invoices_invoice_date | invoice_date | False |
| invoices | ix_invoices_invoice_number | invoice_number | False |
| notifications | idx_fk_notifications_user_id | user_id | False |
| partners | gin_partners_name_trgm | name | False |
| partners | ix_partners_currency_balance | currency, current_balance | False |
| partners | ix_partners_customer_id | customer_id | False |
| partners | ix_partners_is_archived_balance | is_archived, current_balance | False |
| partners | ix_partners_name_phone | name, phone_number | False |
| partners | ix_partners_share_percentage | share_percentage | False |
| payments | gin_payments_notes_trgm | notes | False |
| payments | gin_payments_reference_trgm | reference | False |
| payments | idx_payments_customer_date | customer_id, payment_date | False |
| payments | idx_payments_status | status | False |
| payments | ix_payments_currency | currency | False |
| payments | ix_payments_customer_date | customer_id, payment_date | False |
| payments | ix_payments_customer_date_completed | customer_id, payment_date | False |
| payments | ix_payments_customer_id | customer_id | False |
| payments | ix_payments_date | payment_date | False |
| payments | ix_payments_date_active | payment_date | False |
| payments | ix_payments_direction | direction | False |
| payments | ix_payments_entity_type | entity_type | False |
| payments | ix_payments_invoice_id | invoice_id | False |
| payments | ix_payments_is_archived | is_archived | False |
| payments | ix_payments_method | method | False |
| payments | ix_payments_partner_date | partner_id, payment_date | False |
| payments | ix_payments_partner_id | partner_id | False |
| payments | ix_payments_payment_number | payment_number | False |
| payments | ix_payments_receipt_number | receipt_number | False |
| payments | ix_payments_sale_id | sale_id | False |
| payments | ix_payments_service_id | service_id | False |
| payments | ix_payments_status | status | False |
| payments | ix_payments_supplier_date | supplier_id, payment_date | False |
| payments | ix_payments_supplier_id | supplier_id | False |
| products | ix_products_brand | brand | False |
| products | ix_products_name | name | False |
| products | ix_products_part_number | part_number | False |
| sale_returns | idx_sale_returns_customer | customer_id | False |
| sale_returns | ix_sale_returns_return_date | return_date | False |
| sales | idx_sales_customer_date | customer_id, sale_date | False |
| sales | ix_sales_customer_date | customer_id, sale_date | False |
| sales | ix_sales_customer_id | customer_id | False |
| sales | ix_sales_date | sale_date | False |
| sales | ix_sales_status | status | False |
| service_requests | idx_services_customer_date | customer_id, completed_at | False |
| service_requests | ix_service_received_active | received_at | False |
| service_requests | ix_service_requests_customer_date | customer_id, received_at | False |
| service_requests | ix_service_requests_customer_id | customer_id | False |
| service_requests | ix_service_requests_customer_status_date | customer_id, status, received_at | False |
| service_requests | ix_service_requests_mechanic_id | mechanic_id | False |
| service_requests | ix_service_requests_mechanic_status | mechanic_id, status | False |
| service_requests | ix_service_requests_priority | priority | False |
| service_requests | ix_service_requests_received_at | received_at | False |
| service_requests | ix_service_requests_received_status | received_at, status | False |
| service_requests | ix_service_requests_status | status | False |
| service_requests | ix_service_requests_status_created_at | status, created_at | False |
| service_requests | ix_service_requests_status_priority | status, priority | False |
| stock_levels | ix_stock_levels_prod | product_id | False |
| stock_levels | ix_stock_levels_wh | warehouse_id | False |
| stock_levels | ix_stock_levels_wh_prod | warehouse_id, product_id | False |
| stock_movements | idx_fk_stock_movements_created_by | created_by | False |
| stock_movements | ix_stock_movements_created_at | created_at | False |
| stock_movements | ix_stock_movements_movement_type | movement_type | False |
| stock_movements | ix_stock_movements_product_id | product_id | False |
| stock_movements | ix_stock_movements_updated_at | updated_at | False |
| stock_movements | ix_stock_movements_warehouse_id | warehouse_id | False |
| suppliers | gin_suppliers_name_trgm | name | False |
| suppliers | ix_suppliers_currency | currency | False |
| suppliers | ix_suppliers_current_balance | current_balance | False |
| suppliers | ix_suppliers_is_archived | is_archived | False |
| suppliers | ix_suppliers_lower_email | <UNKNOWN> | False |
| suppliers | ix_suppliers_name | name | False |
| users | ix_users_is_active | is_active | False |
| users | ix_users_last_login | last_login | False |
| users | ix_users_last_seen | last_seen | False |
| users | ix_users_lower_email | <UNKNOWN> | False |
| users | ix_users_lower_username | <UNKNOWN> | False |
| users | uq_users_email | email | True |
| users | uq_users_username | username | True |