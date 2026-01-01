BEGIN;

CREATE INDEX IF NOT EXISTS ix_customers_opening_balance ON customers (opening_balance);

-- CREATE INDEX ix_customers_total_due ON customers (total_due); -- total_due is a hybrid property, not a column

CREATE INDEX IF NOT EXISTS ix_partner_settle_line_product ON partner_settlement_lines (product_id);

CREATE INDEX IF NOT EXISTS ix_partner_settle_line_warehouse ON partner_settlement_lines (warehouse_id);

CREATE INDEX IF NOT EXISTS ix_partner_settle_closing_balance ON partner_settlements (closing_balance);

CREATE INDEX IF NOT EXISTS ix_partner_settle_opening_balance ON partner_settlements (opening_balance);

CREATE INDEX IF NOT EXISTS ix_partner_settle_total_due ON partner_settlements (total_due);

DROP INDEX IF EXISTS gin_partners_name_trgm;

DROP INDEX IF EXISTS ix_partners_currency_balance;

DROP INDEX IF EXISTS ix_partners_is_archived_balance;

DROP INDEX IF EXISTS ix_partners_name_phone;

DROP INDEX IF EXISTS ix_partners_share_percentage;

CREATE INDEX IF NOT EXISTS ix_partners_opening_balance ON partners (opening_balance);

DROP INDEX IF EXISTS gin_payments_notes_trgm;

DROP INDEX IF EXISTS gin_payments_reference_trgm;

DROP INDEX IF EXISTS idx_payments_customer_date;

DROP INDEX IF EXISTS idx_payments_status;

DROP INDEX IF EXISTS ix_payments_currency;

DROP INDEX IF EXISTS ix_payments_customer_date;

DROP INDEX IF EXISTS ix_payments_customer_date_completed;

DROP INDEX IF EXISTS ix_payments_date;

DROP INDEX IF EXISTS ix_payments_date_active;

DROP INDEX IF EXISTS ix_payments_direction;

DROP INDEX IF EXISTS ix_payments_partner_date;

DROP INDEX IF EXISTS ix_payments_status;

DROP INDEX IF EXISTS ix_payments_supplier_date;

CREATE INDEX IF NOT EXISTS ix_pay_created_by ON payments (created_by);

CREATE INDEX IF NOT EXISTS ix_pay_cust_stat_dir ON payments (customer_id, status, direction);

CREATE INDEX IF NOT EXISTS ix_pay_exp_stat_dir ON payments (expense_id, status, direction);

CREATE INDEX IF NOT EXISTS ix_pay_method_date ON payments (method, payment_date);

CREATE INDEX IF NOT EXISTS ix_pay_shp_stat_dir ON payments (shipment_id, status, direction);

CREATE INDEX IF NOT EXISTS ix_pay_srv_stat_dir ON payments (service_id, status, direction);

CREATE INDEX IF NOT EXISTS ix_pay_total_amount ON payments (total_amount);

CREATE INDEX IF NOT EXISTS ix_preorders_date_status ON preorders (preorder_date, status);

CREATE INDEX IF NOT EXISTS ix_preorders_pay_method ON preorders (payment_method);

CREATE INDEX IF NOT EXISTS ix_preorders_prepaid ON preorders (prepaid_amount);

CREATE INDEX IF NOT EXISTS ix_products_is_published ON products (is_published);

CREATE INDEX IF NOT EXISTS ix_products_supplier ON products (supplier_id);

CREATE INDEX IF NOT EXISTS ix_products_vehicle_type ON products (vehicle_type_id);

CREATE INDEX IF NOT EXISTS ix_products_warehouse ON products (warehouse_id);

DROP INDEX IF EXISTS ix_risk_score;

CREATE INDEX IF NOT EXISTS ix_risk_score ON project_risks (risk_score DESC);

DROP INDEX IF EXISTS idx_sale_returns_customer;

DROP INDEX IF EXISTS idx_sales_customer_date;

DROP INDEX IF EXISTS ix_sales_customer_date;

DROP INDEX IF EXISTS ix_sales_date;

CREATE INDEX IF NOT EXISTS ix_sales_archived ON sales (is_archived, archived_at);

CREATE INDEX IF NOT EXISTS ix_sales_balance_due ON sales (balance_due);

CREATE INDEX IF NOT EXISTS ix_sales_seller_date ON sales (seller_id, sale_date);

CREATE INDEX IF NOT EXISTS ix_sales_total_amount ON sales (total_amount);

DROP INDEX IF EXISTS idx_services_customer_date;

DROP INDEX IF EXISTS ix_service_received_active;

DROP INDEX IF EXISTS ix_service_requests_customer_date;

DROP INDEX IF EXISTS ix_service_requests_customer_status_date;

DROP INDEX IF EXISTS ix_service_requests_mechanic_status;

DROP INDEX IF EXISTS ix_service_requests_received_status;

DROP INDEX IF EXISTS ix_service_requests_status_created_at;

DROP INDEX IF EXISTS ix_service_requests_status_priority;

CREATE INDEX IF NOT EXISTS ix_srv_chassis ON service_requests (chassis_number);

CREATE INDEX IF NOT EXISTS ix_srv_completed_at ON service_requests (completed_at);

CREATE INDEX IF NOT EXISTS ix_srv_cost_center ON service_requests (cost_center_id);

CREATE INDEX IF NOT EXISTS ix_srv_created_status ON service_requests (created_at, status);

CREATE INDEX IF NOT EXISTS ix_srv_cust_status ON service_requests (customer_id, status);

CREATE INDEX IF NOT EXISTS ix_srv_expected_delivery ON service_requests (expected_delivery);

CREATE INDEX IF NOT EXISTS ix_srv_mech_status ON service_requests (mechanic_id, status);

CREATE INDEX IF NOT EXISTS ix_srv_total_amount ON service_requests (total_amount);

CREATE INDEX IF NOT EXISTS ix_srv_vehicle_model ON service_requests (vehicle_model);

CREATE INDEX IF NOT EXISTS ix_srv_vehicle_vrn ON service_requests (vehicle_vrn);

DROP INDEX IF EXISTS ix_stock_levels_prod;

DROP INDEX IF EXISTS ix_stock_levels_wh;

DROP INDEX IF EXISTS ix_stock_levels_wh_prod;

CREATE INDEX IF NOT EXISTS ix_stock_quantity ON stock_levels (quantity);

CREATE INDEX IF NOT EXISTS ix_supplier_settle_line_product ON supplier_settlement_lines (product_id);

DROP INDEX IF EXISTS gin_suppliers_name_trgm;

DROP INDEX IF EXISTS ix_suppliers_currency;

DROP INDEX IF EXISTS ix_suppliers_lower_email;

DROP INDEX IF EXISTS ix_suppliers_name;

CREATE INDEX IF NOT EXISTS ix_supp_contact ON suppliers (contact);

CREATE INDEX IF NOT EXISTS ix_supp_name_active ON suppliers (name, is_archived);

CREATE INDEX IF NOT EXISTS ix_supp_opening_balance ON suppliers (opening_balance);

DROP INDEX IF EXISTS ix_users_is_active;

DROP INDEX IF EXISTS ix_users_last_login;

DROP INDEX IF EXISTS ix_users_last_seen;

DROP INDEX IF EXISTS ix_users_lower_email;

DROP INDEX IF EXISTS ix_users_lower_username;

CREATE INDEX IF NOT EXISTS ix_wps_share_percentage ON warehouse_partner_shares (share_percentage);

CREATE INDEX IF NOT EXISTS ix_warehouses_parent ON warehouses (parent_id);

CREATE INDEX IF NOT EXISTS ix_warehouses_partner ON warehouses (partner_id);

CREATE INDEX IF NOT EXISTS ix_warehouses_share_percent ON warehouses (share_percent);

CREATE INDEX IF NOT EXISTS ix_warehouses_supplier ON warehouses (supplier_id);

UPDATE alembic_version SET version_num='11237fb81943';

COMMIT;
