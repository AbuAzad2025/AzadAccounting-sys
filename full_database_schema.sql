-- Garage Manager System Full Schema Snapshot
-- Generated automatically for disaster recovery

CREATE TABLE system_settings (
	id SERIAL NOT NULL, 
	key VARCHAR(100) NOT NULL, 
	value TEXT, 
	description TEXT, 
	data_type VARCHAR(20), 
	is_public BOOLEAN, 
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	PRIMARY KEY (id)
);

CREATE UNIQUE INDEX ix_system_settings_key ON system_settings (key);

CREATE TABLE currencies (
	code VARCHAR(10) NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	symbol VARCHAR(10), 
	decimals INTEGER DEFAULT 2 NOT NULL, 
	is_active BOOLEAN DEFAULT true NOT NULL, 
	PRIMARY KEY (code)
);

CREATE TABLE permissions (
	id SERIAL NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	code VARCHAR(100), 
	description VARCHAR(255), 
	name_ar VARCHAR(120), 
	module VARCHAR(50), 
	is_protected BOOLEAN DEFAULT false NOT NULL, 
	aliases JSON, 
	PRIMARY KEY (id)
);

CREATE UNIQUE INDEX ix_permissions_code ON permissions (code);

CREATE INDEX ix_permissions_module ON permissions (module);

CREATE UNIQUE INDEX ix_permissions_name ON permissions (name);

CREATE TABLE roles (
	id SERIAL NOT NULL, 
	name VARCHAR(50) NOT NULL, 
	description VARCHAR(200), 
	is_default BOOLEAN NOT NULL, 
	PRIMARY KEY (id)
);

CREATE UNIQUE INDEX ix_roles_name ON roles (name);

CREATE TABLE equipment_types (
	id SERIAL NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	model_number VARCHAR(100), 
	chassis_number VARCHAR(100), 
	notes TEXT, 
	category VARCHAR(50), 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE UNIQUE INDEX ix_equipment_types_name ON equipment_types (name);

CREATE INDEX ix_equipment_types_created_at ON equipment_types (created_at);

CREATE INDEX ix_equipment_types_updated_at ON equipment_types (updated_at);

CREATE TABLE product_categories (
	id SERIAL NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	parent_id INTEGER, 
	description TEXT, 
	image_url VARCHAR(255), 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(parent_id) REFERENCES product_categories (id)
);

CREATE INDEX ix_product_categories_updated_at ON product_categories (updated_at);

CREATE INDEX ix_product_categories_name ON product_categories (name);

CREATE INDEX ix_product_categories_created_at ON product_categories (created_at);

CREATE TABLE utility_accounts (
	id SERIAL NOT NULL, 
	utility_type VARCHAR(20) NOT NULL, 
	provider VARCHAR(120) NOT NULL, 
	account_no VARCHAR(100), 
	meter_no VARCHAR(100), 
	alias VARCHAR(120), 
	is_active BOOLEAN NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_utility_type_allowed CHECK (utility_type IN ('ELECTRICITY','WATER')), 
	CONSTRAINT uq_utility_key UNIQUE (utility_type, provider, account_no)
);

CREATE INDEX ix_utility_accounts_created_at ON utility_accounts (created_at);

CREATE INDEX ix_utility_accounts_alias ON utility_accounts (alias);

CREATE INDEX ix_utility_active_type ON utility_accounts (is_active, utility_type);

CREATE INDEX ix_utility_accounts_utility_type ON utility_accounts (utility_type);

CREATE INDEX ix_utility_accounts_updated_at ON utility_accounts (updated_at);

CREATE INDEX ix_utility_accounts_meter_no ON utility_accounts (meter_no);

CREATE INDEX ix_utility_accounts_account_no ON utility_accounts (account_no);

CREATE TABLE expense_types (
	id SERIAL NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	description TEXT, 
	is_active BOOLEAN NOT NULL, 
	code VARCHAR(50), 
	fields_meta JSON, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE UNIQUE INDEX ix_expense_types_code ON expense_types (code);

CREATE INDEX ix_expense_types_created_at ON expense_types (created_at);

CREATE UNIQUE INDEX ix_expense_types_name ON expense_types (name);

CREATE INDEX ix_expense_types_updated_at ON expense_types (updated_at);

CREATE TABLE accounts (
	id SERIAL NOT NULL, 
	code VARCHAR(50) NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	type VARCHAR(9) NOT NULL, 
	is_active BOOLEAN NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE INDEX ix_accounts_updated_at ON accounts (updated_at);

CREATE INDEX ix_accounts_created_at ON accounts (created_at);

CREATE UNIQUE INDEX ix_accounts_code ON accounts (code);

CREATE TABLE gl_batches (
	id SERIAL NOT NULL, 
	code VARCHAR(50), 
	source_type VARCHAR(30), 
	source_id INTEGER, 
	purpose VARCHAR(30), 
	memo VARCHAR(255), 
	posted_at TIMESTAMP WITHOUT TIME ZONE, 
	currency VARCHAR(10) NOT NULL, 
	entity_type VARCHAR(30), 
	entity_id INTEGER, 
	status VARCHAR(6) NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_gl_source_purpose UNIQUE (source_type, source_id, purpose)
);

CREATE INDEX ix_gl_batches_updated_at ON gl_batches (updated_at);

CREATE INDEX ix_gl_batches_entity_id ON gl_batches (entity_id);

CREATE INDEX ix_gl_batches_source_type ON gl_batches (source_type);

CREATE INDEX ix_gl_batches_purpose ON gl_batches (purpose);

CREATE INDEX ix_gl_status_source ON gl_batches (status, source_type, source_id);

CREATE INDEX ix_gl_batches_entity_type ON gl_batches (entity_type);

CREATE INDEX ix_gl_batches_source_id ON gl_batches (source_id);

CREATE INDEX ix_gl_batches_created_at ON gl_batches (created_at);

CREATE UNIQUE INDEX ix_gl_batches_code ON gl_batches (code);

CREATE INDEX ix_gl_posted_status ON gl_batches (status, posted_at);

CREATE INDEX ix_gl_batches_status ON gl_batches (status);

CREATE INDEX ix_gl_batches_posted_at ON gl_batches (posted_at);

CREATE INDEX ix_gl_entity ON gl_batches (entity_type, entity_id);

CREATE TABLE saas_plans (
	id SERIAL NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	description TEXT, 
	price_monthly NUMERIC(10, 2) NOT NULL, 
	price_yearly NUMERIC(10, 2), 
	currency VARCHAR(10) NOT NULL, 
	max_users INTEGER, 
	max_invoices INTEGER, 
	storage_gb INTEGER, 
	features TEXT, 
	is_active BOOLEAN DEFAULT true NOT NULL, 
	is_popular BOOLEAN DEFAULT false NOT NULL, 
	sort_order INTEGER, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (name)
);

CREATE INDEX ix_saas_plans_created_at ON saas_plans (created_at);

CREATE INDEX ix_saas_plans_updated_at ON saas_plans (updated_at);

CREATE TABLE engineering_skills (
	id SERIAL NOT NULL, 
	code VARCHAR(50) NOT NULL, 
	name VARCHAR(200) NOT NULL, 
	name_ar VARCHAR(200), 
	category VARCHAR(100), 
	description TEXT, 
	is_certification_required BOOLEAN DEFAULT false NOT NULL, 
	certification_validity_months INTEGER, 
	is_active BOOLEAN DEFAULT true NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE INDEX ix_engineering_skills_updated_at ON engineering_skills (updated_at);

CREATE INDEX ix_engineering_skills_is_active ON engineering_skills (is_active);

CREATE UNIQUE INDEX ix_engineering_skills_code ON engineering_skills (code);

CREATE INDEX ix_engineering_skills_created_at ON engineering_skills (created_at);

CREATE INDEX ix_skill_category ON engineering_skills (category);

CREATE INDEX ix_engineering_skills_name ON engineering_skills (name);

CREATE TABLE role_permissions (
	role_id INTEGER NOT NULL, 
	permission_id INTEGER NOT NULL, 
	PRIMARY KEY (role_id, permission_id), 
	FOREIGN KEY(role_id) REFERENCES roles (id), 
	FOREIGN KEY(permission_id) REFERENCES permissions (id)
);

CREATE TABLE exchange_rates (
	id SERIAL NOT NULL, 
	base_code VARCHAR(10) NOT NULL, 
	quote_code VARCHAR(10) NOT NULL, 
	rate NUMERIC(18, 8) NOT NULL, 
	valid_from TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	source VARCHAR(50), 
	is_active BOOLEAN DEFAULT true NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_fx_pair_from UNIQUE (base_code, quote_code, valid_from), 
	FOREIGN KEY(base_code) REFERENCES currencies (code), 
	FOREIGN KEY(quote_code) REFERENCES currencies (code)
);

CREATE INDEX ix_exchange_rates_quote_code ON exchange_rates (quote_code);

CREATE INDEX ix_exchange_rates_valid_from ON exchange_rates (valid_from);

CREATE INDEX ix_exchange_rates_base_code ON exchange_rates (base_code);

CREATE TABLE users (
	id SERIAL NOT NULL, 
	username VARCHAR(50) NOT NULL, 
	email VARCHAR(120) NOT NULL, 
	password_hash VARCHAR(255) NOT NULL, 
	role_id INTEGER, 
	is_active BOOLEAN DEFAULT true NOT NULL, 
	is_system_account BOOLEAN DEFAULT false NOT NULL, 
	last_login TIMESTAMP WITHOUT TIME ZONE, 
	last_seen TIMESTAMP WITHOUT TIME ZONE, 
	last_login_ip VARCHAR(64), 
	login_count INTEGER DEFAULT 0 NOT NULL, 
	avatar_url VARCHAR(500), 
	notes_text TEXT, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(role_id) REFERENCES roles (id)
);

CREATE INDEX ix_users_created_at ON users (created_at);

CREATE INDEX ix_users_is_system_account ON users (is_system_account);

CREATE INDEX ix_users_role_id ON users (role_id);

CREATE UNIQUE INDEX ix_users_email ON users (email);

CREATE INDEX ix_users_updated_at ON users (updated_at);

CREATE UNIQUE INDEX ix_users_username ON users (username);

CREATE TABLE gl_entries (
	id SERIAL NOT NULL, 
	batch_id INTEGER NOT NULL, 
	account VARCHAR(50) NOT NULL, 
	debit NUMERIC(12, 2) NOT NULL, 
	credit NUMERIC(12, 2) NOT NULL, 
	currency VARCHAR(10) NOT NULL, 
	ref VARCHAR(50), 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_gl_debit_ge_0 CHECK (debit >= 0), 
	CONSTRAINT ck_gl_credit_ge_0 CHECK (credit >= 0), 
	CONSTRAINT ck_gl_entry_nonzero CHECK ((debit > 0 OR credit > 0)), 
	CONSTRAINT ck_gl_entry_one_side CHECK ((debit = 0 OR credit = 0)), 
	FOREIGN KEY(batch_id) REFERENCES gl_batches (id) ON DELETE CASCADE, 
	FOREIGN KEY(account) REFERENCES accounts (code) ON DELETE RESTRICT
);

CREATE INDEX ix_gl_entries_created_at ON gl_entries (created_at);

CREATE INDEX ix_gl_entries_batch_account ON gl_entries (batch_id, account);

CREATE INDEX ix_gl_entries_batch_id ON gl_entries (batch_id);

CREATE INDEX ix_gl_entries_account ON gl_entries (account);

CREATE INDEX ix_gl_entries_updated_at ON gl_entries (updated_at);

CREATE INDEX ix_gl_entries_account_currency ON gl_entries (account, currency);

CREATE TABLE fixed_asset_categories (
	id SERIAL NOT NULL, 
	code VARCHAR(20) NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	account_code VARCHAR(50) NOT NULL, 
	depreciation_account_code VARCHAR(50) NOT NULL, 
	useful_life_years INTEGER NOT NULL, 
	depreciation_method VARCHAR(17) NOT NULL, 
	depreciation_rate NUMERIC(5, 2), 
	is_active BOOLEAN DEFAULT true NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_useful_life_gt_0 CHECK (useful_life_years > 0), 
	CONSTRAINT ck_depreciation_rate_range CHECK (depreciation_rate >= 0 AND depreciation_rate <= 100), 
	FOREIGN KEY(account_code) REFERENCES accounts (code) ON DELETE RESTRICT, 
	FOREIGN KEY(depreciation_account_code) REFERENCES accounts (code) ON DELETE RESTRICT
);

CREATE INDEX ix_fixed_asset_categories_created_at ON fixed_asset_categories (created_at);

CREATE INDEX ix_fixed_asset_categories_name ON fixed_asset_categories (name);

CREATE INDEX ix_fixed_asset_categories_updated_at ON fixed_asset_categories (updated_at);

CREATE UNIQUE INDEX ix_fixed_asset_categories_code ON fixed_asset_categories (code);

CREATE INDEX ix_fixed_asset_categories_is_active ON fixed_asset_categories (is_active);

CREATE TABLE archives (
	id SERIAL NOT NULL, 
	record_type VARCHAR(50) NOT NULL, 
	record_id INTEGER NOT NULL, 
	table_name VARCHAR(100) NOT NULL, 
	archived_data TEXT NOT NULL, 
	archive_reason VARCHAR(200), 
	archived_by INTEGER NOT NULL, 
	archived_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	original_created_at TIMESTAMP WITHOUT TIME ZONE, 
	original_updated_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	FOREIGN KEY(archived_by) REFERENCES users (id)
);

CREATE INDEX ix_archives_record_id ON archives (record_id);

CREATE INDEX ix_archives_record_type ON archives (record_type);

CREATE TABLE user_permissions (
	user_id INTEGER NOT NULL, 
	permission_id INTEGER NOT NULL, 
	PRIMARY KEY (user_id, permission_id), 
	FOREIGN KEY(user_id) REFERENCES users (id), 
	FOREIGN KEY(permission_id) REFERENCES permissions (id)
);

CREATE TABLE deletion_logs (
	id SERIAL NOT NULL, 
	deletion_type VARCHAR(20) NOT NULL, 
	entity_id INTEGER NOT NULL, 
	entity_name VARCHAR(200) NOT NULL, 
	status VARCHAR(20) NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	deleted_by INTEGER NOT NULL, 
	deletion_reason TEXT, 
	confirmation_code VARCHAR(50), 
	deleted_data JSON, 
	related_entities JSON, 
	stock_reversals JSON, 
	accounting_reversals JSON, 
	balance_reversals JSON, 
	restored_at TIMESTAMP WITHOUT TIME ZONE, 
	restored_by INTEGER, 
	restoration_notes TEXT, 
	PRIMARY KEY (id), 
	CONSTRAINT chk_deletion_status CHECK (status IN ('PENDING','COMPLETED','FAILED','RESTORED')), 
	FOREIGN KEY(deleted_by) REFERENCES users (id), 
	FOREIGN KEY(restored_by) REFERENCES users (id)
);

CREATE INDEX ix_deletion_logs_status ON deletion_logs (status);

CREATE INDEX ix_deletion_type_status ON deletion_logs (deletion_type, status);

CREATE INDEX ix_deletion_logs_entity_id ON deletion_logs (entity_id);

CREATE UNIQUE INDEX ix_deletion_logs_confirmation_code ON deletion_logs (confirmation_code);

CREATE INDEX ix_deletion_logs_deleted_by ON deletion_logs (deleted_by);

CREATE INDEX ix_deletion_entity ON deletion_logs (deletion_type, entity_id);

CREATE INDEX ix_deletion_logs_deletion_type ON deletion_logs (deletion_type);

CREATE TABLE auth_audit (
	id SERIAL NOT NULL, 
	user_id INTEGER, 
	event VARCHAR(40) NOT NULL, 
	success BOOLEAN DEFAULT true NOT NULL, 
	ip VARCHAR(64), 
	user_agent VARCHAR(255), 
	note VARCHAR(255), 
	metadata JSON, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);

CREATE INDEX ix_auth_audit_event ON auth_audit (event);

CREATE INDEX ix_auth_audit_user_id ON auth_audit (user_id);

CREATE INDEX ix_auth_audit_created_at ON auth_audit (created_at);

CREATE TABLE customers (
	id SERIAL NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	phone VARCHAR(20) NOT NULL, 
	whatsapp VARCHAR(20), 
	email VARCHAR(120), 
	address VARCHAR(200), 
	password_hash VARCHAR(512), 
	category VARCHAR(20), 
	notes TEXT, 
	is_active BOOLEAN DEFAULT true NOT NULL, 
	is_online BOOLEAN DEFAULT false NOT NULL, 
	is_archived BOOLEAN DEFAULT false NOT NULL, 
	archived_at TIMESTAMP WITHOUT TIME ZONE, 
	archived_by INTEGER, 
	archive_reason VARCHAR(200), 
	credit_limit NUMERIC(12, 2) DEFAULT 0 NOT NULL, 
	discount_rate NUMERIC(5, 2) DEFAULT 0 NOT NULL, 
	currency VARCHAR(10) DEFAULT 'ILS' NOT NULL, 
	opening_balance NUMERIC(12, 2) DEFAULT 0 NOT NULL, 
	current_balance NUMERIC(12, 2) DEFAULT 0 NOT NULL, 
	sales_balance NUMERIC(12, 2) DEFAULT 0 NOT NULL, 
	returns_balance NUMERIC(12, 2) DEFAULT 0 NOT NULL, 
	invoices_balance NUMERIC(12, 2) DEFAULT 0 NOT NULL, 
	services_balance NUMERIC(12, 2) DEFAULT 0 NOT NULL, 
	preorders_balance NUMERIC(12, 2) DEFAULT 0 NOT NULL, 
	online_orders_balance NUMERIC(12, 2) DEFAULT 0 NOT NULL, 
	payments_in_balance NUMERIC(12, 2) DEFAULT 0 NOT NULL, 
	payments_out_balance NUMERIC(12, 2) DEFAULT 0 NOT NULL, 
	checks_in_balance NUMERIC(12, 2) DEFAULT 0 NOT NULL, 
	checks_out_balance NUMERIC(12, 2) DEFAULT 0 NOT NULL, 
	returned_checks_in_balance NUMERIC(12, 2) DEFAULT 0 NOT NULL, 
	returned_checks_out_balance NUMERIC(12, 2) DEFAULT 0 NOT NULL, 
	expenses_balance NUMERIC(12, 2) DEFAULT 0 NOT NULL, 
	service_expenses_balance NUMERIC(12, 2) DEFAULT 0 NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_customer_credit_limit_non_negative CHECK (credit_limit >= 0), 
	CONSTRAINT ck_customer_discount_0_100 CHECK (discount_rate >= 0 AND discount_rate <= 100), 
	UNIQUE (phone), 
	UNIQUE (email), 
	FOREIGN KEY(archived_by) REFERENCES users (id)
);

CREATE INDEX ix_customers_online_orders_balance ON customers (online_orders_balance);

CREATE INDEX ix_customers_updated_at ON customers (updated_at);

CREATE INDEX ix_customers_payments_in_balance ON customers (payments_in_balance);

CREATE INDEX ix_customers_payments_out_balance ON customers (payments_out_balance);

CREATE INDEX ix_customers_archived_at ON customers (archived_at);

CREATE INDEX ix_customers_checks_in_balance ON customers (checks_in_balance);

CREATE INDEX ix_customers_active_name ON customers (is_active, name);

CREATE INDEX ix_customers_checks_out_balance ON customers (checks_out_balance);

CREATE INDEX ix_customers_online_active ON customers (is_online, is_active);

CREATE INDEX ix_customers_returned_checks_in_balance ON customers (returned_checks_in_balance);

CREATE INDEX ix_customers_opening_balance ON customers (opening_balance);

CREATE INDEX ix_customers_archived_by ON customers (archived_by);

CREATE INDEX ix_customers_returned_checks_out_balance ON customers (returned_checks_out_balance);

CREATE INDEX ix_customers_credit_limit ON customers (credit_limit);

CREATE INDEX ix_customers_expenses_balance ON customers (expenses_balance);

CREATE INDEX ix_customers_sales_balance ON customers (sales_balance);

CREATE INDEX ix_customers_service_expenses_balance ON customers (service_expenses_balance);

CREATE INDEX ix_customers_returns_balance ON customers (returns_balance);

CREATE INDEX ix_customers_current_balance ON customers (current_balance);

CREATE INDEX ix_customers_invoices_balance ON customers (invoices_balance);

CREATE INDEX ix_customers_services_balance ON customers (services_balance);

CREATE INDEX ix_customers_created_at ON customers (created_at);

CREATE INDEX ix_customers_preorders_balance ON customers (preorders_balance);

COMMENT ON COLUMN customers.opening_balance IS 'الرصيد الافتتاحي (موجب=له رصيد عندنا، سالب=لنا رصيد عنده)';

COMMENT ON COLUMN customers.current_balance IS 'الرصيد الحالي المحدث';

COMMENT ON COLUMN customers.sales_balance IS 'رصيد المبيعات';

COMMENT ON COLUMN customers.returns_balance IS 'رصيد المرتجعات';

COMMENT ON COLUMN customers.invoices_balance IS 'رصيد الفواتير';

COMMENT ON COLUMN customers.services_balance IS 'رصيد الخدمات';

COMMENT ON COLUMN customers.preorders_balance IS 'رصيد الحجوزات المسبقة';

COMMENT ON COLUMN customers.online_orders_balance IS 'رصيد الطلبات الأونلاين';

COMMENT ON COLUMN customers.payments_in_balance IS 'رصيد الدفعات الواردة';

COMMENT ON COLUMN customers.payments_out_balance IS 'رصيد الدفعات الصادرة';

COMMENT ON COLUMN customers.checks_in_balance IS 'رصيد الشيكات الواردة';

COMMENT ON COLUMN customers.checks_out_balance IS 'رصيد الشيكات الصادرة';

COMMENT ON COLUMN customers.returned_checks_in_balance IS 'رصيد الشيكات المرتدة الواردة';

COMMENT ON COLUMN customers.returned_checks_out_balance IS 'رصيد الشيكات المرتدة الصادرة';

COMMENT ON COLUMN customers.expenses_balance IS 'رصيد المصروفات العادية (تُطرح)';

COMMENT ON COLUMN customers.service_expenses_balance IS 'رصيد مصروفات توريد الخدمات (تُضاف)';

CREATE TABLE branches (
	id SERIAL NOT NULL, 
	name VARCHAR(120) NOT NULL, 
	code VARCHAR(32) NOT NULL, 
	is_active BOOLEAN DEFAULT true NOT NULL, 
	address VARCHAR(200), 
	city VARCHAR(100), 
	geo_lat NUMERIC(10, 6), 
	geo_lng NUMERIC(10, 6), 
	phone VARCHAR(32), 
	email VARCHAR(120), 
	manager_user_id INTEGER, 
	manager_employee_id INTEGER, 
	timezone VARCHAR(64), 
	currency VARCHAR(10) DEFAULT 'ILS' NOT NULL, 
	tax_id VARCHAR(64), 
	notes TEXT, 
	is_archived BOOLEAN DEFAULT false NOT NULL, 
	archived_at TIMESTAMP WITHOUT TIME ZONE, 
	archived_by INTEGER, 
	archive_reason VARCHAR(200), 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (code), 
	FOREIGN KEY(manager_user_id) REFERENCES users (id), 
	FOREIGN KEY(archived_by) REFERENCES users (id)
);

CREATE INDEX ix_branches_name ON branches (name);

CREATE INDEX ix_branches_archived_at ON branches (archived_at);

CREATE INDEX ix_branches_created_at ON branches (created_at);

CREATE INDEX ix_branches_updated_at ON branches (updated_at);

CREATE INDEX ix_branches_is_archived ON branches (is_archived);

CREATE INDEX ix_branches_manager_employee_id ON branches (manager_employee_id);

CREATE INDEX ix_branches_manager_user_id ON branches (manager_user_id);

CREATE INDEX ix_branches_is_active ON branches (is_active);

CREATE INDEX ix_branches_archived_by ON branches (archived_by);

CREATE TABLE notes (
	id SERIAL NOT NULL, 
	content TEXT NOT NULL, 
	author_id INTEGER, 
	entity_type VARCHAR(50), 
	entity_id VARCHAR(50), 
	is_pinned BOOLEAN DEFAULT false NOT NULL, 
	priority VARCHAR(6) NOT NULL, 
	target_type VARCHAR(50), 
	target_ids TEXT, 
	notification_type VARCHAR(50), 
	notification_date TIMESTAMP WITHOUT TIME ZONE, 
	is_sent BOOLEAN DEFAULT false NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(author_id) REFERENCES users (id) ON DELETE SET NULL
);

CREATE INDEX ix_notes_author_id ON notes (author_id);

CREATE INDEX ix_notes_updated_at ON notes (updated_at);

CREATE INDEX ix_notes_entity_id ON notes (entity_id);

CREATE INDEX ix_notes_notification_date ON notes (notification_date);

CREATE INDEX ix_notes_entity_type ON notes (entity_type);

CREATE INDEX ix_notes_is_sent ON notes (is_sent);

CREATE INDEX ix_notes_target_type ON notes (target_type);

CREATE INDEX ix_notes_priority ON notes (priority);

CREATE INDEX ix_notes_created_at ON notes (created_at);

CREATE INDEX ix_notes_notification_type ON notes (notification_type);

CREATE INDEX ix_notes_is_pinned ON notes (is_pinned);

CREATE TABLE cost_centers (
	id SERIAL NOT NULL, 
	code VARCHAR(20) NOT NULL, 
	name VARCHAR(200) NOT NULL, 
	parent_id INTEGER, 
	description TEXT, 
	manager_id INTEGER, 
	gl_account_code VARCHAR(50), 
	budget_amount NUMERIC(15, 2), 
	actual_amount NUMERIC(15, 2), 
	is_active BOOLEAN DEFAULT true NOT NULL, 
	created_by INTEGER, 
	updated_by INTEGER, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_cost_center_budget_ge_0 CHECK (budget_amount >= 0), 
	FOREIGN KEY(parent_id) REFERENCES cost_centers (id), 
	FOREIGN KEY(manager_id) REFERENCES users (id), 
	FOREIGN KEY(created_by) REFERENCES users (id), 
	FOREIGN KEY(updated_by) REFERENCES users (id)
);

CREATE INDEX ix_cost_centers_created_at ON cost_centers (created_at);

CREATE INDEX ix_cost_centers_updated_by ON cost_centers (updated_by);

CREATE INDEX ix_cost_center_parent ON cost_centers (parent_id, is_active);

CREATE INDEX ix_cost_centers_created_by ON cost_centers (created_by);

CREATE INDEX ix_cost_centers_is_active ON cost_centers (is_active);

CREATE INDEX ix_cost_centers_manager_id ON cost_centers (manager_id);

CREATE INDEX ix_cost_centers_parent_id ON cost_centers (parent_id);

CREATE INDEX ix_cost_centers_updated_at ON cost_centers (updated_at);

CREATE UNIQUE INDEX ix_cost_centers_code ON cost_centers (code);

CREATE INDEX ix_cost_centers_name ON cost_centers (name);

CREATE TABLE workflow_definitions (
	id SERIAL NOT NULL, 
	workflow_code VARCHAR(50) NOT NULL, 
	workflow_name VARCHAR(200) NOT NULL, 
	workflow_name_ar VARCHAR(200), 
	description TEXT, 
	workflow_type VARCHAR(12) NOT NULL, 
	entity_type VARCHAR(12) NOT NULL, 
	steps_definition JSON NOT NULL, 
	auto_start BOOLEAN NOT NULL, 
	auto_start_condition JSON, 
	is_active BOOLEAN NOT NULL, 
	version INTEGER NOT NULL, 
	timeout_hours INTEGER, 
	escalation_rules JSON, 
	created_by INTEGER, 
	updated_by INTEGER, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(created_by) REFERENCES users (id), 
	FOREIGN KEY(updated_by) REFERENCES users (id)
);

CREATE UNIQUE INDEX ix_workflow_definitions_workflow_code ON workflow_definitions (workflow_code);

CREATE INDEX ix_workflow_def_entity_active ON workflow_definitions (entity_type, is_active);

CREATE INDEX ix_workflow_definitions_updated_at ON workflow_definitions (updated_at);

CREATE INDEX ix_workflow_definitions_workflow_type ON workflow_definitions (workflow_type);

CREATE INDEX ix_workflow_definitions_created_at ON workflow_definitions (created_at);

CREATE INDEX ix_workflow_definitions_entity_type ON workflow_definitions (entity_type);

CREATE INDEX ix_workflow_definitions_updated_by ON workflow_definitions (updated_by);

CREATE INDEX ix_workflow_definitions_created_by ON workflow_definitions (created_by);

CREATE INDEX ix_workflow_definitions_is_active ON workflow_definitions (is_active);

CREATE TABLE notifications (
	id SERIAL NOT NULL, 
	user_id INTEGER, 
	title VARCHAR(255) NOT NULL, 
	message TEXT NOT NULL, 
	type VARCHAR(50) NOT NULL, 
	priority VARCHAR(20) NOT NULL, 
	data JSON, 
	action_url VARCHAR(500), 
	is_read BOOLEAN NOT NULL, 
	read_at TIMESTAMP WITHOUT TIME ZONE, 
	expires_at TIMESTAMP WITHOUT TIME ZONE, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);

CREATE INDEX ix_notifications_created_at ON notifications (created_at);

CREATE INDEX ix_notifications_updated_at ON notifications (updated_at);

CREATE TABLE notification_logs (
	id SERIAL NOT NULL, 
	type VARCHAR(20) NOT NULL, 
	recipient VARCHAR(255) NOT NULL, 
	subject VARCHAR(500), 
	content TEXT, 
	status VARCHAR(20) NOT NULL, 
	provider_id VARCHAR(100), 
	error_message TEXT, 
	extra_data TEXT, 
	sent_at TIMESTAMP WITHOUT TIME ZONE, 
	delivered_at TIMESTAMP WITHOUT TIME ZONE, 
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	customer_id INTEGER, 
	user_id INTEGER, 
	PRIMARY KEY (id), 
	FOREIGN KEY(customer_id) REFERENCES customers (id) ON DELETE SET NULL, 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE SET NULL
);

CREATE INDEX ix_notification_logs_customer_id ON notification_logs (customer_id);

CREATE INDEX ix_notification_logs_recipient ON notification_logs (recipient);

CREATE INDEX ix_notification_logs_sent_at ON notification_logs (sent_at);

CREATE INDEX ix_notification_logs_user_id ON notification_logs (user_id);

CREATE INDEX ix_notification_logs_type ON notification_logs (type);

CREATE INDEX ix_notification_logs_created_at ON notification_logs (created_at);

CREATE INDEX ix_notification_logs_status ON notification_logs (status);

CREATE TABLE suppliers (
	id SERIAL NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	is_local BOOLEAN DEFAULT true NOT NULL, 
	identity_number VARCHAR(100), 
	contact VARCHAR(200), 
	phone VARCHAR(20), 
	email VARCHAR(120), 
	address VARCHAR(200), 
	notes TEXT, 
	payment_terms VARCHAR(50), 
	currency VARCHAR(10) DEFAULT 'ILS' NOT NULL, 
	opening_balance NUMERIC(12, 2) DEFAULT 0 NOT NULL, 
	current_balance NUMERIC(12, 2) DEFAULT 0 NOT NULL, 
	exchange_items_balance NUMERIC(12, 2) DEFAULT 0 NOT NULL, 
	sale_returns_balance NUMERIC(12, 2) DEFAULT 0 NOT NULL, 
	sales_balance NUMERIC(12, 2) DEFAULT 0 NOT NULL, 
	services_balance NUMERIC(12, 2) DEFAULT 0 NOT NULL, 
	preorders_balance NUMERIC(12, 2) DEFAULT 0 NOT NULL, 
	payments_in_balance NUMERIC(12, 2) DEFAULT 0 NOT NULL, 
	payments_out_balance NUMERIC(12, 2) DEFAULT 0 NOT NULL, 
	preorders_prepaid_balance NUMERIC(12, 2) DEFAULT 0 NOT NULL, 
	returns_balance NUMERIC(12, 2) DEFAULT 0 NOT NULL, 
	expenses_balance NUMERIC(12, 2) DEFAULT 0 NOT NULL, 
	service_expenses_balance NUMERIC(12, 2) DEFAULT 0 NOT NULL, 
	returned_checks_in_balance NUMERIC(12, 2) DEFAULT 0 NOT NULL, 
	returned_checks_out_balance NUMERIC(12, 2) DEFAULT 0 NOT NULL, 
	customer_id INTEGER, 
	is_archived BOOLEAN NOT NULL, 
	archived_at TIMESTAMP WITHOUT TIME ZONE, 
	archived_by INTEGER, 
	archive_reason VARCHAR(200), 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (identity_number), 
	FOREIGN KEY(customer_id) REFERENCES customers (id), 
	FOREIGN KEY(archived_by) REFERENCES users (id)
);

CREATE INDEX ix_suppliers_created_at ON suppliers (created_at);

CREATE INDEX ix_suppliers_archived_by ON suppliers (archived_by);

CREATE INDEX ix_supp_name_active ON suppliers (name, is_archived);

CREATE INDEX ix_suppliers_current_balance ON suppliers (current_balance);

CREATE UNIQUE INDEX ix_suppliers_email ON suppliers (email);

CREATE INDEX ix_suppliers_archived_at ON suppliers (archived_at);

CREATE INDEX ix_supp_contact ON suppliers (contact);

CREATE INDEX ix_suppliers_updated_at ON suppliers (updated_at);

CREATE INDEX ix_suppliers_phone ON suppliers (phone);

CREATE INDEX ix_supp_opening_balance ON suppliers (opening_balance);

CREATE INDEX ix_suppliers_is_archived ON suppliers (is_archived);

CREATE INDEX ix_suppliers_customer_id ON suppliers (customer_id);

COMMENT ON COLUMN suppliers.opening_balance IS 'الرصيد الافتتاحي (موجب=له رصيد عندنا، سالب=لنا رصيد عنده)';

COMMENT ON COLUMN suppliers.current_balance IS 'الرصيد الحالي المحدث';

COMMENT ON COLUMN suppliers.exchange_items_balance IS 'رصيد قطع التبادل';

COMMENT ON COLUMN suppliers.sale_returns_balance IS 'رصيد مرتجعات المبيعات';

COMMENT ON COLUMN suppliers.sales_balance IS 'رصيد المبيعات';

COMMENT ON COLUMN suppliers.services_balance IS 'رصيد الخدمات';

COMMENT ON COLUMN suppliers.preorders_balance IS 'رصيد الحجوزات المسبقة';

COMMENT ON COLUMN suppliers.payments_in_balance IS 'رصيد الدفعات الواردة';

COMMENT ON COLUMN suppliers.payments_out_balance IS 'رصيد الدفعات الصادرة';

COMMENT ON COLUMN suppliers.preorders_prepaid_balance IS 'رصيد أرصدة الحجوزات';

COMMENT ON COLUMN suppliers.returns_balance IS 'رصيد المرتجعات Exchange';

COMMENT ON COLUMN suppliers.expenses_balance IS 'رصيد المصروفات العادية (تُطرح)';

COMMENT ON COLUMN suppliers.service_expenses_balance IS 'رصيد مصروفات توريد الخدمة (تُضاف)';

COMMENT ON COLUMN suppliers.returned_checks_in_balance IS 'رصيد الشيكات المرتدة الواردة';

COMMENT ON COLUMN suppliers.returned_checks_out_balance IS 'رصيد الشيكات المرتدة الصادرة';

CREATE TABLE partners (
	id SERIAL NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	contact_info VARCHAR(200), 
	identity_number VARCHAR(100), 
	phone_number VARCHAR(20), 
	email VARCHAR(120), 
	address VARCHAR(200), 
	share_percentage NUMERIC(5, 2) DEFAULT 0 NOT NULL, 
	currency VARCHAR(10) DEFAULT 'ILS' NOT NULL, 
	opening_balance NUMERIC(12, 2) DEFAULT 0 NOT NULL, 
	current_balance NUMERIC(12, 2) DEFAULT 0 NOT NULL, 
	inventory_balance NUMERIC(12, 2) DEFAULT 0 NOT NULL, 
	sales_share_balance NUMERIC(12, 2) DEFAULT 0 NOT NULL, 
	sales_to_partner_balance NUMERIC(12, 2) DEFAULT 0 NOT NULL, 
	service_fees_balance NUMERIC(12, 2) DEFAULT 0 NOT NULL, 
	preorders_to_partner_balance NUMERIC(12, 2) DEFAULT 0 NOT NULL, 
	preorders_prepaid_balance NUMERIC(12, 2) DEFAULT 0 NOT NULL, 
	damaged_items_balance NUMERIC(12, 2) DEFAULT 0 NOT NULL, 
	payments_in_balance NUMERIC(12, 2) DEFAULT 0 NOT NULL, 
	payments_out_balance NUMERIC(12, 2) DEFAULT 0 NOT NULL, 
	returned_checks_in_balance NUMERIC(12, 2) DEFAULT 0 NOT NULL, 
	returned_checks_out_balance NUMERIC(12, 2) DEFAULT 0 NOT NULL, 
	expenses_balance NUMERIC(12, 2) DEFAULT 0 NOT NULL, 
	service_expenses_balance NUMERIC(12, 2) DEFAULT 0 NOT NULL, 
	notes TEXT, 
	customer_id INTEGER, 
	is_archived BOOLEAN NOT NULL, 
	archived_at TIMESTAMP WITHOUT TIME ZONE, 
	archived_by INTEGER, 
	archive_reason VARCHAR(200), 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (identity_number), 
	UNIQUE (phone_number), 
	FOREIGN KEY(customer_id) REFERENCES customers (id), 
	FOREIGN KEY(archived_by) REFERENCES users (id)
);

CREATE INDEX ix_partners_is_archived ON partners (is_archived);

CREATE INDEX ix_partners_opening_balance ON partners (opening_balance);

CREATE INDEX ix_partners_customer_id ON partners (customer_id);

CREATE INDEX ix_partners_created_at ON partners (created_at);

CREATE INDEX ix_partners_archived_by ON partners (archived_by);

CREATE INDEX ix_partners_current_balance ON partners (current_balance);

CREATE INDEX ix_partners_name ON partners (name);

CREATE INDEX ix_partners_archived_at ON partners (archived_at);

CREATE UNIQUE INDEX ix_partners_email ON partners (email);

CREATE INDEX ix_partners_updated_at ON partners (updated_at);

COMMENT ON COLUMN partners.opening_balance IS 'الرصيد الافتتاحي (موجب=له رصيد عندنا، سالب=لنا رصيد عنده)';

COMMENT ON COLUMN partners.current_balance IS 'الرصيد الحالي المحدث';

COMMENT ON COLUMN partners.inventory_balance IS 'رصيد المخزون';

COMMENT ON COLUMN partners.sales_share_balance IS 'رصيد نصيب المبيعات';

COMMENT ON COLUMN partners.sales_to_partner_balance IS 'رصيد المبيعات له';

COMMENT ON COLUMN partners.service_fees_balance IS 'رصيد رسوم الصيانة';

COMMENT ON COLUMN partners.preorders_to_partner_balance IS 'رصيد الحجوزات له';

COMMENT ON COLUMN partners.preorders_prepaid_balance IS 'رصيد العربونات المدفوعة';

COMMENT ON COLUMN partners.damaged_items_balance IS 'رصيد القطع التالفة';

COMMENT ON COLUMN partners.payments_in_balance IS 'رصيد الدفعات الواردة';

COMMENT ON COLUMN partners.payments_out_balance IS 'رصيد الدفعات الصادرة';

COMMENT ON COLUMN partners.returned_checks_in_balance IS 'رصيد الشيكات المرتدة الواردة';

COMMENT ON COLUMN partners.returned_checks_out_balance IS 'رصيد الشيكات المرتدة الصادرة';

COMMENT ON COLUMN partners.expenses_balance IS 'رصيد المصروفات العادية (تُطرح)';

COMMENT ON COLUMN partners.service_expenses_balance IS 'رصيد توريد الخدمة (تُضاف)';

CREATE TABLE sites (
	id SERIAL NOT NULL, 
	branch_id INTEGER NOT NULL, 
	name VARCHAR(120) NOT NULL, 
	code VARCHAR(32) NOT NULL, 
	is_active BOOLEAN DEFAULT true NOT NULL, 
	address VARCHAR(200), 
	city VARCHAR(100), 
	geo_lat NUMERIC(10, 6), 
	geo_lng NUMERIC(10, 6), 
	manager_user_id INTEGER, 
	manager_employee_id INTEGER, 
	notes TEXT, 
	is_archived BOOLEAN DEFAULT false NOT NULL, 
	archived_at TIMESTAMP WITHOUT TIME ZONE, 
	archived_by INTEGER, 
	archive_reason VARCHAR(200), 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(branch_id) REFERENCES branches (id), 
	FOREIGN KEY(manager_user_id) REFERENCES users (id), 
	FOREIGN KEY(archived_by) REFERENCES users (id)
);

CREATE INDEX ix_sites_updated_at ON sites (updated_at);

CREATE INDEX ix_sites_code ON sites (code);

CREATE INDEX ix_sites_is_archived ON sites (is_archived);

CREATE INDEX ix_sites_manager_employee_id ON sites (manager_employee_id);

CREATE INDEX ix_sites_manager_user_id ON sites (manager_user_id);

CREATE INDEX ix_sites_created_at ON sites (created_at);

CREATE INDEX ix_sites_archived_by ON sites (archived_by);

CREATE INDEX ix_sites_branch_id ON sites (branch_id);

CREATE INDEX ix_sites_is_active ON sites (is_active);

CREATE INDEX ix_sites_archived_at ON sites (archived_at);

CREATE INDEX ix_sites_name ON sites (name);

CREATE TABLE user_branches (
	id SERIAL NOT NULL, 
	user_id INTEGER NOT NULL, 
	branch_id INTEGER NOT NULL, 
	is_primary BOOLEAN NOT NULL, 
	can_manage BOOLEAN NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_user_branch UNIQUE (user_id, branch_id), 
	FOREIGN KEY(user_id) REFERENCES users (id), 
	FOREIGN KEY(branch_id) REFERENCES branches (id)
);

CREATE INDEX ix_user_branches_is_primary ON user_branches (is_primary);

CREATE INDEX ix_user_branches_user_id ON user_branches (user_id);

CREATE INDEX ix_user_branches_updated_at ON user_branches (updated_at);

CREATE INDEX ix_user_branches_branch_id ON user_branches (branch_id);

CREATE INDEX ix_user_branches_created_at ON user_branches (created_at);

CREATE TABLE service_requests (
	id SERIAL NOT NULL, 
	service_number VARCHAR(50), 
	customer_id INTEGER NOT NULL, 
	mechanic_id INTEGER, 
	vehicle_type_id INTEGER, 
	status VARCHAR(11) NOT NULL, 
	priority VARCHAR(6) NOT NULL, 
	vehicle_vrn VARCHAR(50), 
	vehicle_model VARCHAR(100), 
	chassis_number VARCHAR(100), 
	engineer_notes TEXT, 
	description TEXT, 
	estimated_duration INTEGER, 
	actual_duration INTEGER, 
	estimated_cost NUMERIC(12, 2), 
	total_cost NUMERIC(12, 2), 
	start_time DATE, 
	end_time DATE, 
	problem_description TEXT, 
	diagnosis TEXT, 
	resolution TEXT, 
	notes TEXT, 
	received_at TIMESTAMP WITHOUT TIME ZONE, 
	started_at TIMESTAMP WITHOUT TIME ZONE, 
	expected_delivery TIMESTAMP WITHOUT TIME ZONE, 
	completed_at TIMESTAMP WITHOUT TIME ZONE, 
	currency VARCHAR(10) NOT NULL, 
	fx_rate_used NUMERIC(10, 6), 
	fx_rate_source VARCHAR(20), 
	fx_rate_timestamp TIMESTAMP WITHOUT TIME ZONE, 
	fx_base_currency VARCHAR(10), 
	fx_quote_currency VARCHAR(10), 
	tax_rate NUMERIC(5, 2), 
	discount_total NUMERIC(12, 2), 
	parts_total NUMERIC(12, 2), 
	labor_total NUMERIC(12, 2), 
	total_amount NUMERIC(12, 2), 
	consume_stock BOOLEAN NOT NULL, 
	warranty_days INTEGER, 
	refunded_total NUMERIC(12, 2) NOT NULL, 
	refund_of_id INTEGER, 
	idempotency_key VARCHAR(64), 
	cancelled_at TIMESTAMP WITHOUT TIME ZONE, 
	cancelled_by INTEGER, 
	cancel_reason VARCHAR(200), 
	is_archived BOOLEAN NOT NULL, 
	archived_at TIMESTAMP WITHOUT TIME ZONE, 
	archived_by INTEGER, 
	archive_reason VARCHAR(200), 
	cost_center_id INTEGER, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(customer_id) REFERENCES customers (id), 
	FOREIGN KEY(mechanic_id) REFERENCES users (id), 
	FOREIGN KEY(vehicle_type_id) REFERENCES equipment_types (id), 
	FOREIGN KEY(refund_of_id) REFERENCES service_requests (id) ON DELETE SET NULL, 
	FOREIGN KEY(cancelled_by) REFERENCES users (id), 
	FOREIGN KEY(archived_by) REFERENCES users (id), 
	FOREIGN KEY(cost_center_id) REFERENCES cost_centers (id)
);

CREATE INDEX ix_service_requests_cost_center_id ON service_requests (cost_center_id);

CREATE INDEX ix_srv_completed_at ON service_requests (completed_at);

CREATE INDEX ix_service_requests_cancelled_at ON service_requests (cancelled_at);

CREATE INDEX ix_srv_total_amount ON service_requests (total_amount);

CREATE INDEX ix_service_requests_vehicle_type_id ON service_requests (vehicle_type_id);

CREATE INDEX ix_service_requests_received_at ON service_requests (received_at);

CREATE INDEX ix_service_requests_cancelled_by ON service_requests (cancelled_by);

CREATE INDEX ix_service_requests_created_at ON service_requests (created_at);

CREATE INDEX ix_service_requests_customer_id ON service_requests (customer_id);

CREATE INDEX ix_service_requests_updated_at ON service_requests (updated_at);

CREATE INDEX ix_srv_vehicle_vrn ON service_requests (vehicle_vrn);

CREATE INDEX ix_service_requests_status ON service_requests (status);

CREATE INDEX ix_service_requests_is_archived ON service_requests (is_archived);

CREATE INDEX ix_srv_chassis ON service_requests (chassis_number);

CREATE UNIQUE INDEX ix_service_requests_service_number ON service_requests (service_number);

CREATE INDEX ix_srv_vehicle_model ON service_requests (vehicle_model);

CREATE INDEX ix_service_requests_archived_at ON service_requests (archived_at);

CREATE INDEX ix_srv_cust_status ON service_requests (customer_id, status);

CREATE INDEX ix_service_requests_refund_of_id ON service_requests (refund_of_id);

CREATE INDEX ix_srv_mech_status ON service_requests (mechanic_id, status);

CREATE INDEX ix_service_requests_archived_by ON service_requests (archived_by);

CREATE INDEX ix_srv_cost_center ON service_requests (cost_center_id);

CREATE INDEX ix_srv_created_status ON service_requests (created_at, status);

CREATE INDEX ix_service_requests_priority ON service_requests (priority);

CREATE UNIQUE INDEX ix_service_requests_idempotency_key ON service_requests (idempotency_key);

CREATE INDEX ix_service_requests_mechanic_id ON service_requests (mechanic_id);

CREATE INDEX ix_srv_expected_delivery ON service_requests (expected_delivery);

CREATE TABLE online_carts (
	id SERIAL NOT NULL, 
	cart_id VARCHAR(50), 
	customer_id INTEGER, 
	session_id VARCHAR(100), 
	status VARCHAR(9) NOT NULL, 
	expires_at TIMESTAMP WITHOUT TIME ZONE, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(customer_id) REFERENCES customers (id) ON DELETE SET NULL
);

CREATE INDEX ix_online_carts_updated_at ON online_carts (updated_at);

CREATE UNIQUE INDEX ix_online_carts_cart_id ON online_carts (cart_id);

CREATE INDEX ix_online_carts_expires_at ON online_carts (expires_at);

CREATE INDEX ix_online_carts_status ON online_carts (status);

CREATE INDEX ix_online_carts_created_at ON online_carts (created_at);

CREATE INDEX ix_online_carts_customer_id ON online_carts (customer_id);

CREATE INDEX ix_online_carts_session_id ON online_carts (session_id);

CREATE TABLE audit_logs (
	id SERIAL NOT NULL, 
	model_name VARCHAR(100) NOT NULL, 
	record_id INTEGER, 
	customer_id INTEGER, 
	user_id INTEGER, 
	action VARCHAR(20) NOT NULL, 
	old_data TEXT, 
	new_data TEXT, 
	ip_address VARCHAR(45), 
	user_agent VARCHAR(255), 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(customer_id) REFERENCES customers (id) ON DELETE SET NULL, 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE SET NULL
);

CREATE INDEX ix_audit_logs_user_id ON audit_logs (user_id);

CREATE INDEX ix_audit_logs_customer_id ON audit_logs (customer_id);

CREATE INDEX ix_audit_logs_action ON audit_logs (action);

CREATE INDEX ix_audit_logs_record_id ON audit_logs (record_id);

CREATE INDEX ix_audit_logs_updated_at ON audit_logs (updated_at);

CREATE INDEX ix_audit_logs_created_at ON audit_logs (created_at);

CREATE INDEX ix_audit_logs_model_name ON audit_logs (model_name);

CREATE TABLE customer_loyalty (
	id SERIAL NOT NULL, 
	customer_id INTEGER NOT NULL, 
	total_points INTEGER NOT NULL, 
	available_points INTEGER NOT NULL, 
	used_points INTEGER NOT NULL, 
	loyalty_tier VARCHAR(50) NOT NULL, 
	total_spent NUMERIC(12, 2) NOT NULL, 
	last_activity TIMESTAMP WITHOUT TIME ZONE, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (customer_id), 
	FOREIGN KEY(customer_id) REFERENCES customers (id)
);

CREATE INDEX ix_customer_loyalty_customer_id ON customer_loyalty (customer_id);

CREATE INDEX ix_customer_loyalty_tier ON customer_loyalty (loyalty_tier);

CREATE INDEX ix_customer_loyalty_updated_at ON customer_loyalty (updated_at);

CREATE INDEX ix_customer_loyalty_created_at ON customer_loyalty (created_at);

CREATE TABLE customer_loyalty_points (
	id SERIAL NOT NULL, 
	customer_id INTEGER NOT NULL, 
	points INTEGER NOT NULL, 
	reason VARCHAR(255) NOT NULL, 
	type VARCHAR(50) NOT NULL, 
	reference_id INTEGER, 
	reference_type VARCHAR(50), 
	expires_at TIMESTAMP WITHOUT TIME ZONE, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(customer_id) REFERENCES customers (id)
);

CREATE INDEX ix_loyalty_points_expires ON customer_loyalty_points (expires_at);

CREATE INDEX ix_customer_loyalty_points_created_at ON customer_loyalty_points (created_at);

CREATE INDEX ix_loyalty_points_customer_id ON customer_loyalty_points (customer_id);

CREATE INDEX ix_loyalty_points_type ON customer_loyalty_points (type);

CREATE INDEX ix_customer_loyalty_points_updated_at ON customer_loyalty_points (updated_at);

CREATE TABLE saas_subscriptions (
	id SERIAL NOT NULL, 
	customer_id INTEGER NOT NULL, 
	plan_id INTEGER NOT NULL, 
	status VARCHAR(20) NOT NULL, 
	start_date TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	end_date TIMESTAMP WITHOUT TIME ZONE, 
	trial_end_date TIMESTAMP WITHOUT TIME ZONE, 
	auto_renew BOOLEAN DEFAULT true NOT NULL, 
	cancelled_at TIMESTAMP WITHOUT TIME ZONE, 
	cancelled_by INTEGER, 
	cancellation_reason TEXT, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(customer_id) REFERENCES customers (id), 
	FOREIGN KEY(plan_id) REFERENCES saas_plans (id), 
	FOREIGN KEY(cancelled_by) REFERENCES users (id)
);

CREATE INDEX ix_saas_subscriptions_updated_at ON saas_subscriptions (updated_at);

CREATE INDEX ix_saas_subscriptions_plan_id ON saas_subscriptions (plan_id);

CREATE INDEX ix_saas_subscriptions_created_at ON saas_subscriptions (created_at);

CREATE INDEX ix_saas_subscriptions_customer_id ON saas_subscriptions (customer_id);

CREATE TABLE bank_accounts (
	id SERIAL NOT NULL, 
	code VARCHAR(20) NOT NULL, 
	name VARCHAR(200) NOT NULL, 
	bank_name VARCHAR(200) NOT NULL, 
	account_number VARCHAR(100) NOT NULL, 
	iban VARCHAR(34), 
	swift_code VARCHAR(11), 
	currency VARCHAR(10) NOT NULL, 
	branch_id INTEGER, 
	gl_account_code VARCHAR(50) NOT NULL, 
	opening_balance NUMERIC(15, 2) NOT NULL, 
	current_balance NUMERIC(15, 2) NOT NULL, 
	last_reconciled_date DATE, 
	notes TEXT, 
	is_active BOOLEAN DEFAULT true NOT NULL, 
	created_by INTEGER, 
	updated_by INTEGER, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_bank_current_balance_not_null CHECK (current_balance IS NOT NULL), 
	FOREIGN KEY(branch_id) REFERENCES branches (id), 
	FOREIGN KEY(gl_account_code) REFERENCES accounts (code) ON DELETE RESTRICT, 
	FOREIGN KEY(created_by) REFERENCES users (id), 
	FOREIGN KEY(updated_by) REFERENCES users (id)
);

CREATE INDEX ix_bank_accounts_last_reconciled_date ON bank_accounts (last_reconciled_date);

CREATE INDEX ix_bank_accounts_currency ON bank_accounts (currency);

CREATE INDEX ix_bank_accounts_created_at ON bank_accounts (created_at);

CREATE INDEX ix_bank_accounts_updated_by ON bank_accounts (updated_by);

CREATE UNIQUE INDEX ix_bank_accounts_code ON bank_accounts (code);

CREATE INDEX ix_bank_accounts_created_by ON bank_accounts (created_by);

CREATE INDEX ix_bank_accounts_name ON bank_accounts (name);

CREATE INDEX ix_bank_accounts_bank_name ON bank_accounts (bank_name);

CREATE INDEX ix_bank_accounts_is_active ON bank_accounts (is_active);

CREATE INDEX ix_bank_accounts_branch_id ON bank_accounts (branch_id);

CREATE INDEX ix_bank_account_code ON bank_accounts (code);

CREATE INDEX ix_bank_accounts_updated_at ON bank_accounts (updated_at);

CREATE TABLE cost_center_allocations (
	id SERIAL NOT NULL, 
	cost_center_id INTEGER NOT NULL, 
	source_type VARCHAR(8) NOT NULL, 
	source_id INTEGER NOT NULL, 
	amount NUMERIC(15, 2) NOT NULL, 
	percentage NUMERIC(5, 2), 
	allocation_date DATE NOT NULL, 
	notes TEXT, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_cost_center_allocation_source UNIQUE (source_type, source_id, cost_center_id), 
	CONSTRAINT ck_cc_alloc_amount_ge_0 CHECK (amount >= 0), 
	CONSTRAINT ck_cc_alloc_percentage_range CHECK (percentage >= 0 AND percentage <= 100), 
	FOREIGN KEY(cost_center_id) REFERENCES cost_centers (id) ON DELETE CASCADE
);

CREATE INDEX ix_cost_center_allocations_updated_at ON cost_center_allocations (updated_at);

CREATE INDEX ix_cost_center_allocations_source_id ON cost_center_allocations (source_id);

CREATE INDEX ix_cost_center_allocations_created_at ON cost_center_allocations (created_at);

CREATE INDEX ix_cost_center_allocations_cost_center_id ON cost_center_allocations (cost_center_id);

CREATE INDEX ix_cost_center_alloc_date ON cost_center_allocations (cost_center_id, allocation_date);

CREATE INDEX ix_cost_center_allocations_allocation_date ON cost_center_allocations (allocation_date);

CREATE INDEX ix_cost_center_allocations_source_type ON cost_center_allocations (source_type);

CREATE TABLE projects (
	id SERIAL NOT NULL, 
	code VARCHAR(20) NOT NULL, 
	name VARCHAR(200) NOT NULL, 
	client_id INTEGER, 
	start_date DATE NOT NULL, 
	end_date DATE, 
	planned_end_date DATE, 
	budget_amount NUMERIC(15, 2), 
	estimated_cost NUMERIC(15, 2), 
	estimated_revenue NUMERIC(15, 2), 
	actual_cost NUMERIC(15, 2), 
	actual_revenue NUMERIC(15, 2), 
	cost_center_id INTEGER, 
	manager_id INTEGER NOT NULL, 
	branch_id INTEGER, 
	status VARCHAR(9) NOT NULL, 
	completion_percentage NUMERIC(5, 2), 
	description TEXT, 
	notes TEXT, 
	is_active BOOLEAN DEFAULT true NOT NULL, 
	created_by INTEGER, 
	updated_by INTEGER, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_project_budget_ge_0 CHECK (budget_amount >= 0), 
	CONSTRAINT ck_project_completion_range CHECK (completion_percentage >= 0 AND completion_percentage <= 100), 
	FOREIGN KEY(client_id) REFERENCES customers (id), 
	FOREIGN KEY(cost_center_id) REFERENCES cost_centers (id), 
	FOREIGN KEY(manager_id) REFERENCES users (id), 
	FOREIGN KEY(branch_id) REFERENCES branches (id), 
	FOREIGN KEY(created_by) REFERENCES users (id), 
	FOREIGN KEY(updated_by) REFERENCES users (id)
);

CREATE INDEX ix_projects_cost_center_id ON projects (cost_center_id);

CREATE INDEX ix_projects_created_by ON projects (created_by);

CREATE INDEX ix_projects_created_at ON projects (created_at);

CREATE INDEX ix_project_status_dates ON projects (status, start_date, end_date);

CREATE INDEX ix_projects_end_date ON projects (end_date);

CREATE INDEX ix_projects_is_active ON projects (is_active);

CREATE INDEX ix_projects_updated_by ON projects (updated_by);

CREATE INDEX ix_projects_updated_at ON projects (updated_at);

CREATE INDEX ix_projects_manager_id ON projects (manager_id);

CREATE UNIQUE INDEX ix_projects_code ON projects (code);

CREATE INDEX ix_projects_client_id ON projects (client_id);

CREATE INDEX ix_projects_start_date ON projects (start_date);

CREATE INDEX ix_projects_status ON projects (status);

CREATE INDEX ix_projects_branch_id ON projects (branch_id);

CREATE INDEX ix_projects_name ON projects (name);

CREATE TABLE cost_center_alerts (
	id SERIAL NOT NULL, 
	cost_center_id INTEGER NOT NULL, 
	alert_type VARCHAR(15) NOT NULL, 
	threshold_type VARCHAR(10) DEFAULT 'PERCENTAGE' NOT NULL, 
	threshold_value NUMERIC(15, 2) NOT NULL, 
	is_active BOOLEAN DEFAULT true NOT NULL, 
	notify_manager BOOLEAN DEFAULT true NOT NULL, 
	notify_emails JSON, 
	notify_users JSON, 
	last_triggered_at TIMESTAMP WITHOUT TIME ZONE, 
	trigger_count INTEGER DEFAULT 0 NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(cost_center_id) REFERENCES cost_centers (id) ON DELETE CASCADE
);

CREATE INDEX ix_cost_center_alerts_updated_at ON cost_center_alerts (updated_at);

CREATE INDEX ix_cost_center_alerts_created_at ON cost_center_alerts (created_at);

CREATE INDEX ix_cc_alert_center_active ON cost_center_alerts (cost_center_id, is_active);

CREATE INDEX ix_cost_center_alerts_cost_center_id ON cost_center_alerts (cost_center_id);

CREATE TABLE cost_allocation_rules (
	id SERIAL NOT NULL, 
	code VARCHAR(20) NOT NULL, 
	name VARCHAR(200) NOT NULL, 
	description TEXT, 
	source_cost_center_id INTEGER, 
	allocation_method VARCHAR(14) NOT NULL, 
	frequency VARCHAR(9), 
	is_active BOOLEAN DEFAULT true NOT NULL, 
	auto_execute BOOLEAN DEFAULT false NOT NULL, 
	last_executed_at TIMESTAMP WITHOUT TIME ZONE, 
	next_execution_at TIMESTAMP WITHOUT TIME ZONE, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(source_cost_center_id) REFERENCES cost_centers (id)
);

CREATE UNIQUE INDEX ix_cost_allocation_rules_code ON cost_allocation_rules (code);

CREATE INDEX ix_cost_allocation_rules_source_cost_center_id ON cost_allocation_rules (source_cost_center_id);

CREATE INDEX ix_cost_allocation_rules_name ON cost_allocation_rules (name);

CREATE INDEX ix_allocation_rule_active ON cost_allocation_rules (is_active);

CREATE INDEX ix_cost_allocation_rules_created_at ON cost_allocation_rules (created_at);

CREATE INDEX ix_cost_allocation_rules_updated_at ON cost_allocation_rules (updated_at);

CREATE TABLE workflow_instances (
	id SERIAL NOT NULL, 
	workflow_definition_id INTEGER NOT NULL, 
	instance_code VARCHAR(50) NOT NULL, 
	entity_type VARCHAR(50) NOT NULL, 
	entity_id INTEGER NOT NULL, 
	status VARCHAR(16) NOT NULL, 
	current_step INTEGER NOT NULL, 
	total_steps INTEGER NOT NULL, 
	started_by INTEGER NOT NULL, 
	started_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	completed_at TIMESTAMP WITHOUT TIME ZONE, 
	completed_by INTEGER, 
	cancelled_at TIMESTAMP WITHOUT TIME ZONE, 
	cancelled_by INTEGER, 
	cancellation_reason TEXT, 
	due_date TIMESTAMP WITHOUT TIME ZONE, 
	context_data JSON, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(workflow_definition_id) REFERENCES workflow_definitions (id) ON DELETE RESTRICT, 
	FOREIGN KEY(started_by) REFERENCES users (id), 
	FOREIGN KEY(completed_by) REFERENCES users (id), 
	FOREIGN KEY(cancelled_by) REFERENCES users (id)
);

CREATE UNIQUE INDEX ix_workflow_instances_instance_code ON workflow_instances (instance_code);

CREATE INDEX ix_workflow_instances_cancelled_by ON workflow_instances (cancelled_by);

CREATE INDEX ix_workflow_instances_entity_id ON workflow_instances (entity_id);

CREATE INDEX ix_workflow_inst_status_date ON workflow_instances (status, started_at);

CREATE INDEX ix_workflow_instances_started_at ON workflow_instances (started_at);

CREATE INDEX ix_workflow_instances_updated_at ON workflow_instances (updated_at);

CREATE INDEX ix_workflow_instances_cancelled_at ON workflow_instances (cancelled_at);

CREATE INDEX ix_workflow_instances_completed_by ON workflow_instances (completed_by);

CREATE INDEX ix_workflow_instances_entity_type ON workflow_instances (entity_type);

CREATE INDEX ix_workflow_instances_created_at ON workflow_instances (created_at);

CREATE INDEX ix_workflow_instances_started_by ON workflow_instances (started_by);

CREATE INDEX ix_workflow_inst_entity ON workflow_instances (entity_type, entity_id);

CREATE INDEX ix_workflow_instances_due_date ON workflow_instances (due_date);

CREATE INDEX ix_workflow_instances_status ON workflow_instances (status);

CREATE INDEX ix_workflow_instances_completed_at ON workflow_instances (completed_at);

CREATE INDEX ix_workflow_instances_workflow_definition_id ON workflow_instances (workflow_definition_id);

CREATE TABLE tax_entries (
	id SERIAL NOT NULL, 
	entry_type VARCHAR(20) NOT NULL, 
	transaction_type VARCHAR(50) NOT NULL, 
	transaction_id INTEGER, 
	transaction_reference VARCHAR(50), 
	tax_rate NUMERIC(5, 2) NOT NULL, 
	base_amount NUMERIC(12, 2) NOT NULL, 
	tax_amount NUMERIC(12, 2) NOT NULL, 
	total_amount NUMERIC(12, 2) NOT NULL, 
	currency VARCHAR(3), 
	debit_account VARCHAR(20), 
	credit_account VARCHAR(20), 
	gl_entry_id INTEGER, 
	fiscal_year INTEGER, 
	fiscal_month INTEGER, 
	tax_period VARCHAR(7), 
	is_reconciled BOOLEAN, 
	is_filed BOOLEAN, 
	filing_reference VARCHAR(100), 
	customer_id INTEGER, 
	supplier_id INTEGER, 
	notes TEXT, 
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	created_by INTEGER, 
	PRIMARY KEY (id), 
	FOREIGN KEY(customer_id) REFERENCES customers (id) ON DELETE SET NULL, 
	FOREIGN KEY(supplier_id) REFERENCES suppliers (id) ON DELETE SET NULL, 
	FOREIGN KEY(created_by) REFERENCES users (id) ON DELETE SET NULL
);

CREATE INDEX ix_tax_entries_is_filed ON tax_entries (is_filed);

CREATE INDEX ix_tax_entries_transaction_reference ON tax_entries (transaction_reference);

CREATE INDEX ix_tax_entries_fiscal_month ON tax_entries (fiscal_month);

CREATE INDEX idx_tax_transaction ON tax_entries (transaction_type, transaction_id);

CREATE INDEX ix_tax_entries_transaction_type ON tax_entries (transaction_type);

CREATE INDEX ix_tax_entries_is_reconciled ON tax_entries (is_reconciled);

CREATE INDEX ix_tax_entries_entry_type ON tax_entries (entry_type);

CREATE INDEX ix_tax_entries_created_at ON tax_entries (created_at);

CREATE INDEX ix_tax_entries_tax_period ON tax_entries (tax_period);

CREATE INDEX ix_tax_entries_supplier_id ON tax_entries (supplier_id);

CREATE INDEX ix_tax_entries_customer_id ON tax_entries (customer_id);

CREATE INDEX idx_tax_period_type ON tax_entries (tax_period, entry_type);

CREATE INDEX ix_tax_entries_transaction_id ON tax_entries (transaction_id);

CREATE INDEX ix_tax_entries_fiscal_year ON tax_entries (fiscal_year);

CREATE TABLE supplier_settlements (
	id SERIAL NOT NULL, 
	code VARCHAR(40), 
	supplier_id INTEGER NOT NULL, 
	from_date TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	to_date TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	currency VARCHAR(10) NOT NULL, 
	fx_rate_used NUMERIC(10, 6), 
	fx_rate_source VARCHAR(20), 
	fx_rate_timestamp TIMESTAMP WITHOUT TIME ZONE, 
	fx_base_currency VARCHAR(10), 
	fx_quote_currency VARCHAR(10), 
	status VARCHAR(9) NOT NULL, 
	mode VARCHAR(10) NOT NULL, 
	notes TEXT, 
	total_gross NUMERIC(12, 2), 
	total_due NUMERIC(12, 2), 
	previous_settlement_id INTEGER, 
	opening_balance NUMERIC(12, 2) DEFAULT 0 NOT NULL, 
	rights_exchange NUMERIC(12, 2) DEFAULT 0 NOT NULL, 
	rights_total NUMERIC(12, 2) DEFAULT 0 NOT NULL, 
	obligations_sales NUMERIC(12, 2) DEFAULT 0 NOT NULL, 
	obligations_services NUMERIC(12, 2) DEFAULT 0 NOT NULL, 
	obligations_preorders NUMERIC(12, 2) DEFAULT 0 NOT NULL, 
	obligations_expenses NUMERIC(12, 2) DEFAULT 0 NOT NULL, 
	obligations_total NUMERIC(12, 2) DEFAULT 0 NOT NULL, 
	payments_out NUMERIC(12, 2) DEFAULT 0 NOT NULL, 
	payments_in NUMERIC(12, 2) DEFAULT 0 NOT NULL, 
	payments_returns NUMERIC(12, 2) DEFAULT 0 NOT NULL, 
	payments_net NUMERIC(12, 2) DEFAULT 0 NOT NULL, 
	closing_balance NUMERIC(12, 2) DEFAULT 0 NOT NULL, 
	is_approved BOOLEAN DEFAULT false NOT NULL, 
	approved_by INTEGER, 
	approved_at TIMESTAMP WITHOUT TIME ZONE, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(supplier_id) REFERENCES suppliers (id), 
	FOREIGN KEY(previous_settlement_id) REFERENCES supplier_settlements (id), 
	FOREIGN KEY(approved_by) REFERENCES users (id)
);

CREATE INDEX ix_supplier_settle_opening_balance ON supplier_settlements (opening_balance);

CREATE INDEX ix_supplier_settlements_updated_at ON supplier_settlements (updated_at);

CREATE INDEX ix_supplier_settlements_from_date ON supplier_settlements (from_date);

CREATE INDEX ix_supplier_settle_closing_balance ON supplier_settlements (closing_balance);

CREATE UNIQUE INDEX ix_supplier_settlements_code ON supplier_settlements (code);

CREATE INDEX ix_supplier_settlements_previous_settlement_id ON supplier_settlements (previous_settlement_id);

CREATE INDEX ix_supplier_settlements_status ON supplier_settlements (status);

CREATE INDEX ix_supplier_settlements_created_at ON supplier_settlements (created_at);

CREATE INDEX ix_supplier_settlements_is_approved ON supplier_settlements (is_approved);

CREATE INDEX ix_supplier_settle_total_due ON supplier_settlements (total_due);

CREATE INDEX ix_supplier_settlements_mode ON supplier_settlements (mode);

CREATE INDEX ix_supplier_settlements_to_date ON supplier_settlements (to_date);

CREATE INDEX ix_supplier_settlements_supplier_id ON supplier_settlements (supplier_id);

CREATE TABLE partner_settlements (
	id SERIAL NOT NULL, 
	code VARCHAR(40), 
	partner_id INTEGER NOT NULL, 
	from_date TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	to_date TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	currency VARCHAR(10) NOT NULL, 
	fx_rate_used NUMERIC(10, 6), 
	fx_rate_source VARCHAR(20), 
	fx_rate_timestamp TIMESTAMP WITHOUT TIME ZONE, 
	fx_base_currency VARCHAR(10), 
	fx_quote_currency VARCHAR(10), 
	status VARCHAR(9) NOT NULL, 
	notes TEXT, 
	total_gross NUMERIC(12, 2) NOT NULL, 
	total_share NUMERIC(12, 2) NOT NULL, 
	total_costs NUMERIC(12, 2) NOT NULL, 
	total_due NUMERIC(12, 2) NOT NULL, 
	previous_settlement_id INTEGER, 
	opening_balance NUMERIC(12, 2) DEFAULT 0 NOT NULL, 
	rights_inventory NUMERIC(12, 2) DEFAULT 0 NOT NULL, 
	rights_sales_share NUMERIC(12, 2) DEFAULT 0 NOT NULL, 
	rights_preorders NUMERIC(12, 2) DEFAULT 0 NOT NULL, 
	rights_total NUMERIC(12, 2) DEFAULT 0 NOT NULL, 
	obligations_sales_to_partner NUMERIC(12, 2) DEFAULT 0 NOT NULL, 
	obligations_services NUMERIC(12, 2) DEFAULT 0 NOT NULL, 
	obligations_damaged NUMERIC(12, 2) DEFAULT 0 NOT NULL, 
	obligations_expenses NUMERIC(12, 2) DEFAULT 0 NOT NULL, 
	obligations_returns NUMERIC(12, 2) DEFAULT 0 NOT NULL, 
	obligations_total NUMERIC(12, 2) DEFAULT 0 NOT NULL, 
	payments_out NUMERIC(12, 2) DEFAULT 0 NOT NULL, 
	payments_in NUMERIC(12, 2) DEFAULT 0 NOT NULL, 
	payments_net NUMERIC(12, 2) DEFAULT 0 NOT NULL, 
	closing_balance NUMERIC(12, 2) DEFAULT 0 NOT NULL, 
	is_approved BOOLEAN DEFAULT false NOT NULL, 
	approved_by INTEGER, 
	approved_at TIMESTAMP WITHOUT TIME ZONE, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(partner_id) REFERENCES partners (id), 
	FOREIGN KEY(previous_settlement_id) REFERENCES partner_settlements (id), 
	FOREIGN KEY(approved_by) REFERENCES users (id)
);

CREATE INDEX ix_partner_settlements_status ON partner_settlements (status);

CREATE INDEX ix_partner_settlements_updated_at ON partner_settlements (updated_at);

CREATE INDEX ix_partner_settle_total_due ON partner_settlements (total_due);

CREATE UNIQUE INDEX ix_partner_settlements_code ON partner_settlements (code);

CREATE INDEX ix_partner_settlements_to_date ON partner_settlements (to_date);

CREATE INDEX ix_partner_settlements_created_at ON partner_settlements (created_at);

CREATE INDEX ix_partner_settlements_is_approved ON partner_settlements (is_approved);

CREATE INDEX ix_partner_settle_opening_balance ON partner_settlements (opening_balance);

CREATE INDEX ix_partner_settlements_partner_id ON partner_settlements (partner_id);

CREATE INDEX ix_partner_settlements_from_date ON partner_settlements (from_date);

CREATE INDEX ix_partner_settle_closing_balance ON partner_settlements (closing_balance);

CREATE INDEX ix_partner_settlements_previous_settlement_id ON partner_settlements (previous_settlement_id);

CREATE TABLE employees (
	id SERIAL NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	position VARCHAR(100), 
	salary NUMERIC(15, 2), 
	phone VARCHAR(20), 
	email VARCHAR(120), 
	hire_date DATE, 
	bank_name VARCHAR(100), 
	account_number VARCHAR(100), 
	notes TEXT, 
	currency VARCHAR(10) DEFAULT 'ILS' NOT NULL, 
	branch_id INTEGER NOT NULL, 
	site_id INTEGER, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(branch_id) REFERENCES branches (id), 
	FOREIGN KEY(site_id) REFERENCES sites (id)
);

CREATE INDEX ix_employees_branch_id ON employees (branch_id);

CREATE INDEX ix_employees_name ON employees (name);

CREATE INDEX ix_employees_hire_date ON employees (hire_date);

CREATE UNIQUE INDEX ix_employees_email ON employees (email);

CREATE INDEX ix_employees_updated_at ON employees (updated_at);

CREATE INDEX ix_employees_created_at ON employees (created_at);

CREATE INDEX ix_employees_site_id ON employees (site_id);

CREATE TABLE warehouses (
	id SERIAL NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	warehouse_type VARCHAR(9) DEFAULT 'MAIN' NOT NULL, 
	location VARCHAR(200), 
	branch_id INTEGER, 
	is_active BOOLEAN DEFAULT true NOT NULL, 
	parent_id INTEGER, 
	supplier_id INTEGER, 
	partner_id INTEGER, 
	share_percent NUMERIC(5, 2) DEFAULT 0, 
	capacity INTEGER, 
	current_occupancy INTEGER DEFAULT 0, 
	notes TEXT, 
	online_slug VARCHAR(150), 
	online_is_default BOOLEAN DEFAULT false NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(branch_id) REFERENCES branches (id), 
	FOREIGN KEY(parent_id) REFERENCES warehouses (id), 
	FOREIGN KEY(supplier_id) REFERENCES suppliers (id), 
	FOREIGN KEY(partner_id) REFERENCES partners (id), 
	UNIQUE (online_slug)
);

CREATE INDEX ix_warehouses_branch_id ON warehouses (branch_id);

CREATE INDEX ix_warehouses_partner ON warehouses (partner_id);

CREATE INDEX ix_warehouses_supplier ON warehouses (supplier_id);

CREATE INDEX ix_warehouses_name ON warehouses (name);

CREATE INDEX ix_warehouses_share_percent ON warehouses (share_percent);

CREATE INDEX ix_warehouses_updated_at ON warehouses (updated_at);

CREATE INDEX ix_warehouses_parent ON warehouses (parent_id);

CREATE INDEX ix_warehouses_warehouse_type ON warehouses (warehouse_type);

CREATE INDEX ix_warehouses_created_at ON warehouses (created_at);

CREATE TABLE service_tasks (
	id SERIAL NOT NULL, 
	service_id INTEGER NOT NULL, 
	partner_id INTEGER, 
	share_percentage NUMERIC(5, 2), 
	description VARCHAR(200) NOT NULL, 
	quantity INTEGER, 
	unit_price NUMERIC(10, 2) NOT NULL, 
	discount NUMERIC(12, 2), 
	tax_rate NUMERIC(5, 2), 
	note VARCHAR(200), 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT chk_service_task_qty_positive CHECK (quantity > 0), 
	CONSTRAINT chk_service_task_price_non_negative CHECK (unit_price >= 0), 
	CONSTRAINT chk_service_task_discount_positive CHECK (discount >= 0), 
	CONSTRAINT chk_service_task_discount_max CHECK (discount <= quantity * unit_price), 
	CONSTRAINT chk_service_task_tax_range CHECK (tax_rate >= 0 AND tax_rate <= 100), 
	CONSTRAINT chk_service_task_share_range CHECK (share_percentage >= 0 AND share_percentage <= 100), 
	FOREIGN KEY(service_id) REFERENCES service_requests (id) ON DELETE CASCADE, 
	FOREIGN KEY(partner_id) REFERENCES partners (id)
);

CREATE INDEX ix_service_task_service ON service_tasks (service_id);

CREATE INDEX ix_service_tasks_updated_at ON service_tasks (updated_at);

CREATE INDEX ix_service_tasks_created_at ON service_tasks (created_at);

CREATE INDEX ix_service_task_partner ON service_tasks (partner_id);

CREATE TABLE saas_invoices (
	id SERIAL NOT NULL, 
	invoice_number VARCHAR(50) NOT NULL, 
	subscription_id INTEGER NOT NULL, 
	amount NUMERIC(10, 2) NOT NULL, 
	currency VARCHAR(10) NOT NULL, 
	status VARCHAR(20) NOT NULL, 
	due_date TIMESTAMP WITHOUT TIME ZONE, 
	paid_at TIMESTAMP WITHOUT TIME ZONE, 
	payment_method VARCHAR(50), 
	notes TEXT, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(subscription_id) REFERENCES saas_subscriptions (id)
);

CREATE INDEX ix_saas_invoices_created_at ON saas_invoices (created_at);

CREATE UNIQUE INDEX ix_saas_invoices_invoice_number ON saas_invoices (invoice_number);

CREATE INDEX ix_saas_invoices_updated_at ON saas_invoices (updated_at);

CREATE INDEX ix_saas_invoices_subscription_id ON saas_invoices (subscription_id);

CREATE TABLE recurring_invoice_templates (
	id SERIAL NOT NULL, 
	template_name VARCHAR(200) NOT NULL, 
	customer_id INTEGER NOT NULL, 
	description TEXT, 
	amount NUMERIC(15, 2) NOT NULL, 
	currency VARCHAR(10) NOT NULL, 
	tax_rate NUMERIC(5, 2), 
	frequency VARCHAR(20) NOT NULL, 
	start_date DATE NOT NULL, 
	end_date DATE, 
	next_invoice_date DATE, 
	is_active BOOLEAN DEFAULT true NOT NULL, 
	branch_id INTEGER NOT NULL, 
	site_id INTEGER, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_recurring_amount_ge_0 CHECK (amount >= 0), 
	CONSTRAINT ck_recurring_frequency CHECK (frequency IN ('DAILY','WEEKLY','MONTHLY','QUARTERLY','YEARLY')), 
	FOREIGN KEY(customer_id) REFERENCES customers (id), 
	FOREIGN KEY(branch_id) REFERENCES branches (id), 
	FOREIGN KEY(site_id) REFERENCES sites (id)
);

CREATE INDEX ix_recurring_invoice_templates_next_invoice_date ON recurring_invoice_templates (next_invoice_date);

CREATE INDEX ix_recurring_invoice_templates_frequency ON recurring_invoice_templates (frequency);

CREATE INDEX ix_recurring_invoice_templates_created_at ON recurring_invoice_templates (created_at);

CREATE INDEX ix_recurring_invoice_templates_site_id ON recurring_invoice_templates (site_id);

CREATE INDEX ix_recurring_invoice_templates_branch_id ON recurring_invoice_templates (branch_id);

CREATE INDEX ix_recurring_invoice_templates_is_active ON recurring_invoice_templates (is_active);

CREATE INDEX ix_recurring_invoice_templates_updated_at ON recurring_invoice_templates (updated_at);

CREATE INDEX ix_recurring_invoice_templates_customer_id ON recurring_invoice_templates (customer_id);

CREATE TABLE budgets (
	id SERIAL NOT NULL, 
	fiscal_year INTEGER NOT NULL, 
	account_code VARCHAR(50) NOT NULL, 
	branch_id INTEGER, 
	site_id INTEGER, 
	allocated_amount NUMERIC(12, 2) NOT NULL, 
	notes TEXT, 
	is_active BOOLEAN DEFAULT true NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_budget_year_account_branch_site UNIQUE (fiscal_year, account_code, branch_id, site_id), 
	CONSTRAINT ck_budget_allocated_ge_0 CHECK (allocated_amount >= 0), 
	FOREIGN KEY(account_code) REFERENCES accounts (code) ON DELETE RESTRICT, 
	FOREIGN KEY(branch_id) REFERENCES branches (id) ON DELETE CASCADE, 
	FOREIGN KEY(site_id) REFERENCES sites (id) ON DELETE CASCADE
);

CREATE INDEX ix_budgets_account_code ON budgets (account_code);

CREATE INDEX ix_budgets_is_active ON budgets (is_active);

CREATE INDEX ix_budgets_site_id ON budgets (site_id);

CREATE INDEX ix_budgets_branch_id ON budgets (branch_id);

CREATE INDEX ix_budgets_updated_at ON budgets (updated_at);

CREATE INDEX ix_budget_year_branch ON budgets (fiscal_year, branch_id);

CREATE INDEX ix_budgets_fiscal_year ON budgets (fiscal_year);

CREATE INDEX ix_budgets_created_at ON budgets (created_at);

CREATE INDEX ix_budget_year_account ON budgets (fiscal_year, account_code);

CREATE TABLE fixed_assets (
	id SERIAL NOT NULL, 
	asset_number VARCHAR(50) NOT NULL, 
	name VARCHAR(200) NOT NULL, 
	category_id INTEGER NOT NULL, 
	branch_id INTEGER, 
	site_id INTEGER, 
	purchase_date DATE NOT NULL, 
	purchase_price NUMERIC(12, 2) NOT NULL, 
	supplier_id INTEGER, 
	serial_number VARCHAR(100), 
	barcode VARCHAR(100), 
	location VARCHAR(200), 
	status VARCHAR(8) NOT NULL, 
	disposal_date DATE, 
	disposal_amount NUMERIC(12, 2), 
	disposal_notes TEXT, 
	notes TEXT, 
	is_archived BOOLEAN DEFAULT false NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_asset_price_ge_0 CHECK (purchase_price >= 0), 
	FOREIGN KEY(category_id) REFERENCES fixed_asset_categories (id) ON DELETE RESTRICT, 
	FOREIGN KEY(branch_id) REFERENCES branches (id) ON DELETE CASCADE, 
	FOREIGN KEY(site_id) REFERENCES sites (id) ON DELETE CASCADE, 
	FOREIGN KEY(supplier_id) REFERENCES partners (id)
);

CREATE INDEX ix_fixed_assets_status ON fixed_assets (status);

CREATE UNIQUE INDEX ix_fixed_assets_asset_number ON fixed_assets (asset_number);

CREATE INDEX ix_fixed_assets_is_archived ON fixed_assets (is_archived);

CREATE INDEX ix_fixed_assets_name ON fixed_assets (name);

CREATE INDEX ix_fixed_assets_purchase_date ON fixed_assets (purchase_date);

CREATE INDEX ix_fixed_assets_site_id ON fixed_assets (site_id);

CREATE INDEX ix_fixed_assets_branch_id ON fixed_assets (branch_id);

CREATE INDEX ix_fixed_assets_category_id ON fixed_assets (category_id);

CREATE INDEX ix_fixed_assets_barcode ON fixed_assets (barcode);

CREATE INDEX ix_fixed_assets_updated_at ON fixed_assets (updated_at);

CREATE INDEX ix_asset_category_branch ON fixed_assets (category_id, branch_id);

CREATE INDEX ix_fixed_assets_created_at ON fixed_assets (created_at);

CREATE INDEX ix_asset_status_date ON fixed_assets (status, purchase_date);

CREATE INDEX ix_fixed_assets_serial_number ON fixed_assets (serial_number);

CREATE INDEX ix_fixed_assets_supplier_id ON fixed_assets (supplier_id);

CREATE INDEX ix_fixed_assets_disposal_date ON fixed_assets (disposal_date);

CREATE TABLE bank_statements (
	id SERIAL NOT NULL, 
	bank_account_id INTEGER NOT NULL, 
	statement_number VARCHAR(50), 
	statement_date DATE NOT NULL, 
	period_start DATE NOT NULL, 
	period_end DATE NOT NULL, 
	opening_balance NUMERIC(15, 2) NOT NULL, 
	closing_balance NUMERIC(15, 2) NOT NULL, 
	total_deposits NUMERIC(15, 2), 
	total_withdrawals NUMERIC(15, 2), 
	file_path VARCHAR(500), 
	imported_at TIMESTAMP WITHOUT TIME ZONE, 
	imported_by INTEGER, 
	status VARCHAR(10) NOT NULL, 
	notes TEXT, 
	created_by INTEGER, 
	updated_by INTEGER, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_statement_balance CHECK (closing_balance = opening_balance + total_deposits - total_withdrawals), 
	FOREIGN KEY(bank_account_id) REFERENCES bank_accounts (id) ON DELETE CASCADE, 
	FOREIGN KEY(imported_by) REFERENCES users (id), 
	FOREIGN KEY(created_by) REFERENCES users (id), 
	FOREIGN KEY(updated_by) REFERENCES users (id)
);

CREATE INDEX ix_bank_statements_imported_at ON bank_statements (imported_at);

CREATE INDEX ix_bank_statements_updated_at ON bank_statements (updated_at);

CREATE INDEX ix_bank_statements_statement_date ON bank_statements (statement_date);

CREATE INDEX ix_statement_account_date ON bank_statements (bank_account_id, statement_date);

CREATE INDEX ix_bank_statements_created_at ON bank_statements (created_at);

CREATE INDEX ix_bank_statements_period_end ON bank_statements (period_end);

CREATE INDEX ix_bank_statements_updated_by ON bank_statements (updated_by);

CREATE INDEX ix_bank_statements_bank_account_id ON bank_statements (bank_account_id);

CREATE INDEX ix_bank_statements_statement_number ON bank_statements (statement_number);

CREATE INDEX ix_bank_statements_period_start ON bank_statements (period_start);

CREATE INDEX ix_bank_statements_created_by ON bank_statements (created_by);

CREATE INDEX ix_bank_statements_status ON bank_statements (status);

CREATE TABLE bank_reconciliations (
	id SERIAL NOT NULL, 
	bank_account_id INTEGER NOT NULL, 
	reconciliation_number VARCHAR(50), 
	period_start DATE NOT NULL, 
	period_end DATE NOT NULL, 
	book_balance NUMERIC(15, 2) NOT NULL, 
	bank_balance NUMERIC(15, 2) NOT NULL, 
	unmatched_book_count INTEGER, 
	unmatched_bank_count INTEGER, 
	unmatched_book_amount NUMERIC(15, 2), 
	unmatched_bank_amount NUMERIC(15, 2), 
	reconciled_by INTEGER NOT NULL, 
	reconciled_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	approved_by INTEGER, 
	approved_at TIMESTAMP WITHOUT TIME ZONE, 
	status VARCHAR(9) NOT NULL, 
	notes TEXT, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_reconciliation_period CHECK (period_end >= period_start), 
	FOREIGN KEY(bank_account_id) REFERENCES bank_accounts (id) ON DELETE CASCADE, 
	FOREIGN KEY(reconciled_by) REFERENCES users (id), 
	FOREIGN KEY(approved_by) REFERENCES users (id)
);

CREATE INDEX ix_bank_reconciliations_status ON bank_reconciliations (status);

CREATE INDEX ix_bank_reconciliations_period_start ON bank_reconciliations (period_start);

CREATE INDEX ix_bank_reconciliations_updated_at ON bank_reconciliations (updated_at);

CREATE INDEX ix_reconciliation_account_period ON bank_reconciliations (bank_account_id, period_start, period_end);

CREATE INDEX ix_bank_reconciliations_bank_account_id ON bank_reconciliations (bank_account_id);

CREATE UNIQUE INDEX ix_bank_reconciliations_reconciliation_number ON bank_reconciliations (reconciliation_number);

CREATE INDEX ix_bank_reconciliations_period_end ON bank_reconciliations (period_end);

CREATE INDEX ix_bank_reconciliations_created_at ON bank_reconciliations (created_at);

CREATE TABLE project_phases (
	id SERIAL NOT NULL, 
	project_id INTEGER NOT NULL, 
	name VARCHAR(200) NOT NULL, 
	"order" INTEGER NOT NULL, 
	start_date DATE, 
	end_date DATE, 
	planned_budget NUMERIC(15, 2), 
	actual_cost NUMERIC(15, 2), 
	status VARCHAR(11) NOT NULL, 
	completion_percentage NUMERIC(5, 2), 
	description TEXT, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_phase_budget_ge_0 CHECK (planned_budget >= 0), 
	CONSTRAINT ck_phase_completion_range CHECK (completion_percentage >= 0 AND completion_percentage <= 100), 
	FOREIGN KEY(project_id) REFERENCES projects (id) ON DELETE CASCADE
);

CREATE INDEX ix_project_phases_project_id ON project_phases (project_id);

CREATE INDEX ix_project_phases_updated_at ON project_phases (updated_at);

CREATE INDEX ix_project_phases_end_date ON project_phases (end_date);

CREATE INDEX ix_project_phase_project_order ON project_phases (project_id, "order");

CREATE INDEX ix_project_phases_start_date ON project_phases (start_date);

CREATE INDEX ix_project_phases_created_at ON project_phases (created_at);

CREATE INDEX ix_project_phases_status ON project_phases (status);

CREATE TABLE project_risks (
	id SERIAL NOT NULL, 
	project_id INTEGER NOT NULL, 
	risk_number VARCHAR(50) NOT NULL, 
	title VARCHAR(300) NOT NULL, 
	description TEXT NOT NULL, 
	category VARCHAR(9) NOT NULL, 
	probability VARCHAR(9) NOT NULL, 
	impact VARCHAR(10) NOT NULL, 
	risk_score NUMERIC(5, 2) NOT NULL, 
	status VARCHAR(10) NOT NULL, 
	mitigation_plan TEXT, 
	contingency_plan TEXT, 
	owner_id INTEGER, 
	identified_date DATE NOT NULL, 
	review_date DATE, 
	closed_date DATE, 
	actual_impact_cost NUMERIC(15, 2), 
	notes TEXT, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_risk_score_range CHECK (risk_score >= 0 AND risk_score <= 25), 
	FOREIGN KEY(project_id) REFERENCES projects (id) ON DELETE CASCADE, 
	FOREIGN KEY(owner_id) REFERENCES users (id)
);

CREATE INDEX ix_project_risks_owner_id ON project_risks (owner_id);

CREATE INDEX ix_project_risks_closed_date ON project_risks (closed_date);

CREATE INDEX ix_project_risks_project_id ON project_risks (project_id);

CREATE INDEX ix_project_risks_risk_number ON project_risks (risk_number);

CREATE INDEX ix_risk_score ON project_risks (risk_score DESC);

CREATE INDEX ix_project_risks_updated_at ON project_risks (updated_at);

CREATE INDEX ix_project_risks_review_date ON project_risks (review_date);

CREATE INDEX ix_risk_project_status ON project_risks (project_id, status);

CREATE INDEX ix_project_risks_status ON project_risks (status);

CREATE INDEX ix_project_risks_probability ON project_risks (probability);

CREATE INDEX ix_project_risks_created_at ON project_risks (created_at);

CREATE INDEX ix_project_risks_category ON project_risks (category);

CREATE INDEX ix_project_risks_identified_date ON project_risks (identified_date);

CREATE INDEX ix_project_risks_impact ON project_risks (impact);

CREATE TABLE project_change_orders (
	id SERIAL NOT NULL, 
	project_id INTEGER NOT NULL, 
	change_number VARCHAR(50) NOT NULL, 
	title VARCHAR(300) NOT NULL, 
	description TEXT NOT NULL, 
	requested_by INTEGER, 
	requested_date DATE NOT NULL, 
	reason TEXT, 
	scope_change TEXT, 
	cost_impact NUMERIC(15, 2), 
	schedule_impact_days INTEGER, 
	status VARCHAR(12) NOT NULL, 
	approved_by INTEGER, 
	approved_date DATE, 
	implemented_date DATE, 
	rejection_reason TEXT, 
	notes TEXT, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_change_cost_not_null CHECK (cost_impact IS NOT NULL), 
	CONSTRAINT ck_change_schedule_ge_0 CHECK (schedule_impact_days >= 0), 
	FOREIGN KEY(project_id) REFERENCES projects (id) ON DELETE CASCADE, 
	FOREIGN KEY(requested_by) REFERENCES users (id), 
	FOREIGN KEY(approved_by) REFERENCES users (id)
);

CREATE INDEX ix_project_change_orders_created_at ON project_change_orders (created_at);

CREATE INDEX ix_project_change_orders_approved_date ON project_change_orders (approved_date);

CREATE INDEX ix_change_order_project_status ON project_change_orders (project_id, status);

CREATE INDEX ix_project_change_orders_project_id ON project_change_orders (project_id);

CREATE INDEX ix_project_change_orders_approved_by ON project_change_orders (approved_by);

CREATE UNIQUE INDEX ix_project_change_orders_change_number ON project_change_orders (change_number);

CREATE INDEX ix_project_change_orders_status ON project_change_orders (status);

CREATE INDEX ix_project_change_orders_implemented_date ON project_change_orders (implemented_date);

CREATE INDEX ix_project_change_orders_updated_at ON project_change_orders (updated_at);

CREATE INDEX ix_project_change_orders_requested_date ON project_change_orders (requested_date);

CREATE INDEX ix_project_change_orders_requested_by ON project_change_orders (requested_by);

CREATE TABLE cost_center_alert_logs (
	id SERIAL NOT NULL, 
	alert_id INTEGER, 
	cost_center_id INTEGER, 
	triggered_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	trigger_value NUMERIC(15, 2), 
	threshold_value NUMERIC(15, 2), 
	message TEXT, 
	severity VARCHAR(8), 
	notified_users JSON, 
	notification_sent BOOLEAN DEFAULT false NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(alert_id) REFERENCES cost_center_alerts (id) ON DELETE CASCADE, 
	FOREIGN KEY(cost_center_id) REFERENCES cost_centers (id)
);

CREATE INDEX ix_cost_center_alert_logs_alert_id ON cost_center_alert_logs (alert_id);

CREATE INDEX ix_cost_center_alert_logs_created_at ON cost_center_alert_logs (created_at);

CREATE INDEX ix_cost_center_alert_logs_updated_at ON cost_center_alert_logs (updated_at);

CREATE INDEX ix_cost_center_alert_logs_cost_center_id ON cost_center_alert_logs (cost_center_id);

CREATE INDEX ix_cc_alert_log_date ON cost_center_alert_logs (triggered_at);

CREATE TABLE cost_allocation_lines (
	id SERIAL NOT NULL, 
	rule_id INTEGER NOT NULL, 
	target_cost_center_id INTEGER NOT NULL, 
	percentage NUMERIC(5, 2), 
	fixed_amount NUMERIC(15, 2), 
	allocation_driver VARCHAR(100), 
	driver_value NUMERIC(15, 2), 
	notes TEXT, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_allocation_line_percentage CHECK (percentage >= 0 AND percentage <= 100), 
	FOREIGN KEY(rule_id) REFERENCES cost_allocation_rules (id) ON DELETE CASCADE, 
	FOREIGN KEY(target_cost_center_id) REFERENCES cost_centers (id)
);

CREATE INDEX ix_cost_allocation_lines_target_cost_center_id ON cost_allocation_lines (target_cost_center_id);

CREATE INDEX ix_allocation_line_rule ON cost_allocation_lines (rule_id);

CREATE TABLE cost_allocation_executions (
	id SERIAL NOT NULL, 
	rule_id INTEGER, 
	execution_date DATE NOT NULL, 
	total_amount NUMERIC(15, 2) NOT NULL, 
	status VARCHAR(8) DEFAULT 'DRAFT' NOT NULL, 
	gl_batch_id INTEGER, 
	notes TEXT, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(rule_id) REFERENCES cost_allocation_rules (id), 
	FOREIGN KEY(gl_batch_id) REFERENCES gl_batches (id)
);

CREATE INDEX ix_cost_allocation_executions_created_at ON cost_allocation_executions (created_at);

CREATE INDEX ix_cost_allocation_executions_rule_id ON cost_allocation_executions (rule_id);

CREATE INDEX ix_cost_allocation_executions_gl_batch_id ON cost_allocation_executions (gl_batch_id);

CREATE INDEX ix_cost_allocation_executions_updated_at ON cost_allocation_executions (updated_at);

CREATE INDEX ix_allocation_exec_date ON cost_allocation_executions (execution_date);

CREATE TABLE workflow_actions (
	id SERIAL NOT NULL, 
	workflow_instance_id INTEGER NOT NULL, 
	step_number INTEGER NOT NULL, 
	step_name VARCHAR(200) NOT NULL, 
	action_type VARCHAR(12) NOT NULL, 
	actor_id INTEGER NOT NULL, 
	action_date TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	decision VARCHAR(50), 
	comments TEXT, 
	attachments JSON, 
	delegated_to INTEGER, 
	delegated_at TIMESTAMP WITHOUT TIME ZONE, 
	duration_hours NUMERIC(8, 2), 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(workflow_instance_id) REFERENCES workflow_instances (id) ON DELETE CASCADE, 
	FOREIGN KEY(actor_id) REFERENCES users (id), 
	FOREIGN KEY(delegated_to) REFERENCES users (id)
);

CREATE INDEX ix_workflow_actions_workflow_instance_id ON workflow_actions (workflow_instance_id);

CREATE INDEX ix_workflow_actions_action_date ON workflow_actions (action_date);

CREATE INDEX ix_workflow_actions_updated_at ON workflow_actions (updated_at);

CREATE INDEX ix_workflow_action_instance_step ON workflow_actions (workflow_instance_id, step_number);

CREATE INDEX ix_workflow_actions_actor_id ON workflow_actions (actor_id);

CREATE INDEX ix_workflow_actions_action_type ON workflow_actions (action_type);

CREATE INDEX ix_workflow_action_actor_date ON workflow_actions (actor_id, action_date);

CREATE INDEX ix_workflow_actions_created_at ON workflow_actions (created_at);

CREATE INDEX ix_workflow_actions_delegated_to ON workflow_actions (delegated_to);

CREATE TABLE products (
	id SERIAL NOT NULL, 
	sku VARCHAR(50), 
	name VARCHAR(255) NOT NULL, 
	description TEXT, 
	part_number VARCHAR(100), 
	brand VARCHAR(100), 
	commercial_name VARCHAR(100), 
	chassis_number VARCHAR(100), 
	serial_no VARCHAR(100), 
	barcode VARCHAR(100), 
	unit VARCHAR(50), 
	category_name VARCHAR(100), 
	purchase_price NUMERIC(12, 2) DEFAULT 0 NOT NULL, 
	selling_price NUMERIC(12, 2) DEFAULT 0 NOT NULL, 
	cost_before_shipping NUMERIC(12, 2) DEFAULT 0 NOT NULL, 
	cost_after_shipping NUMERIC(12, 2) DEFAULT 0 NOT NULL, 
	unit_price_before_tax NUMERIC(12, 2) DEFAULT 0 NOT NULL, 
	price NUMERIC(12, 2) DEFAULT 0 NOT NULL, 
	min_price NUMERIC(12, 2), 
	max_price NUMERIC(12, 2), 
	tax_rate NUMERIC(5, 2) DEFAULT 0 NOT NULL, 
	min_qty INTEGER DEFAULT 0 NOT NULL, 
	reorder_point INTEGER, 
	image VARCHAR(255), 
	notes TEXT, 
	condition VARCHAR(11) DEFAULT 'NEW' NOT NULL, 
	origin_country VARCHAR(50), 
	warranty_period INTEGER, 
	weight NUMERIC(10, 2), 
	dimensions VARCHAR(50), 
	is_active BOOLEAN DEFAULT true NOT NULL, 
	is_digital BOOLEAN DEFAULT false NOT NULL, 
	is_exchange BOOLEAN DEFAULT false NOT NULL, 
	is_published BOOLEAN DEFAULT true NOT NULL, 
	vehicle_type_id INTEGER, 
	category_id INTEGER, 
	supplier_id INTEGER, 
	supplier_international_id INTEGER, 
	supplier_local_id INTEGER, 
	online_name VARCHAR(255), 
	online_price NUMERIC(12, 2) DEFAULT 0, 
	online_image VARCHAR(255), 
	warehouse_id INTEGER, 
	currency VARCHAR(10) DEFAULT 'ILS' NOT NULL, 
	fx_rate_used NUMERIC(10, 6), 
	fx_rate_source VARCHAR(20), 
	fx_rate_timestamp TIMESTAMP WITHOUT TIME ZONE, 
	fx_base_currency VARCHAR(10), 
	fx_quote_currency VARCHAR(10), 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_product_price_ge_0 CHECK (price >= 0), 
	CONSTRAINT ck_product_purchase_ge_0 CHECK (purchase_price >= 0), 
	CONSTRAINT ck_product_selling_ge_0 CHECK (selling_price >= 0), 
	CONSTRAINT ck_product_cost_before_ge_0 CHECK (cost_before_shipping >= 0), 
	CONSTRAINT ck_product_cost_after_ge_0 CHECK (cost_after_shipping >= 0), 
	CONSTRAINT ck_product_unit_before_tax_ge_0 CHECK (unit_price_before_tax >= 0), 
	CONSTRAINT ck_product_min_price_ge_0 CHECK (min_price IS NULL OR min_price >= 0), 
	CONSTRAINT ck_product_max_price_ge_0 CHECK (max_price IS NULL OR max_price >= 0), 
	CONSTRAINT ck_product_tax_rate_0_100 CHECK (tax_rate >= 0 AND tax_rate <= 100), 
	CONSTRAINT ck_product_min_qty_ge_0 CHECK (min_qty >= 0), 
	CONSTRAINT ck_product_reorder_ge_0 CHECK (reorder_point IS NULL OR reorder_point >= 0), 
	CONSTRAINT ck_product_weight_ge_0 CHECK (weight IS NULL OR weight >= 0), 
	CONSTRAINT ck_product_online_price_ge_0 CHECK (online_price IS NULL OR online_price >= 0), 
	FOREIGN KEY(vehicle_type_id) REFERENCES equipment_types (id), 
	FOREIGN KEY(category_id) REFERENCES product_categories (id), 
	FOREIGN KEY(supplier_id) REFERENCES suppliers (id), 
	FOREIGN KEY(supplier_international_id) REFERENCES suppliers (id), 
	FOREIGN KEY(supplier_local_id) REFERENCES suppliers (id), 
	FOREIGN KEY(warehouse_id) REFERENCES warehouses (id)
);

CREATE UNIQUE INDEX uq_products_serial_ci ON products (lower(serial_no)) WHERE serial_no IS NOT NULL;

CREATE INDEX ix_products_warehouse ON products (warehouse_id);

CREATE INDEX ix_products_part_number ON products (part_number);

CREATE INDEX ix_products_category_active ON products (category_id, is_active);

CREATE UNIQUE INDEX uq_products_name_wh_ci ON products (lower(name), warehouse_id) WHERE warehouse_id IS NOT NULL;

CREATE UNIQUE INDEX uq_products_sku_ci ON products (lower(sku)) WHERE sku IS NOT NULL;

CREATE INDEX ix_products_name ON products (name);

CREATE INDEX ix_products_is_published ON products (is_published);

CREATE INDEX ix_products_vehicle_type ON products (vehicle_type_id);

CREATE INDEX ix_products_updated_at ON products (updated_at);

CREATE UNIQUE INDEX uq_products_name_global_ci ON products (lower(name)) WHERE warehouse_id IS NULL;

CREATE UNIQUE INDEX uq_products_barcode ON products (barcode) WHERE barcode IS NOT NULL;

CREATE INDEX ix_products_brand_part ON products (brand, part_number);

CREATE INDEX ix_products_created_at ON products (created_at);

CREATE INDEX ix_products_supplier ON products (supplier_id);

CREATE INDEX ix_products_brand ON products (brand);

CREATE TABLE import_runs (
	id SERIAL NOT NULL, 
	warehouse_id INTEGER, 
	user_id INTEGER, 
	filename VARCHAR(255), 
	file_sha256 VARCHAR(64), 
	dry_run BOOLEAN DEFAULT false NOT NULL, 
	inserted INTEGER DEFAULT 0 NOT NULL, 
	updated INTEGER DEFAULT 0 NOT NULL, 
	skipped INTEGER DEFAULT 0 NOT NULL, 
	errors INTEGER DEFAULT 0 NOT NULL, 
	duration_ms INTEGER DEFAULT 0 NOT NULL, 
	report_path VARCHAR(255), 
	notes VARCHAR(255), 
	meta JSON, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(warehouse_id) REFERENCES warehouses (id) ON DELETE SET NULL, 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE SET NULL
);

CREATE INDEX ix_import_runs_user_id ON import_runs (user_id);

CREATE INDEX ix_import_runs_dry_run ON import_runs (dry_run);

CREATE INDEX ix_import_runs_updated_at ON import_runs (updated_at);

CREATE INDEX ix_import_runs_warehouse_id ON import_runs (warehouse_id);

CREATE INDEX ix_import_runs_created_at ON import_runs (created_at);

CREATE TABLE online_preorders (
	id SERIAL NOT NULL, 
	order_number VARCHAR(50), 
	customer_id INTEGER NOT NULL, 
	cart_id INTEGER, 
	warehouse_id INTEGER, 
	prepaid_amount NUMERIC(12, 2), 
	total_amount NUMERIC(12, 2), 
	base_amount NUMERIC(12, 2), 
	tax_rate NUMERIC(5, 2), 
	tax_amount NUMERIC(12, 2), 
	currency VARCHAR(10) NOT NULL, 
	fx_rate_used NUMERIC(10, 6), 
	fx_rate_source VARCHAR(20), 
	fx_rate_timestamp TIMESTAMP WITHOUT TIME ZONE, 
	fx_base_currency VARCHAR(10), 
	fx_quote_currency VARCHAR(10), 
	expected_fulfillment TIMESTAMP WITHOUT TIME ZONE, 
	actual_fulfillment TIMESTAMP WITHOUT TIME ZONE, 
	status VARCHAR(9) NOT NULL, 
	payment_status VARCHAR(7) NOT NULL, 
	payment_method VARCHAR(50), 
	notes TEXT, 
	shipping_address TEXT, 
	billing_address TEXT, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT chk_online_prepaid_non_negative CHECK (prepaid_amount >= 0), 
	CONSTRAINT chk_online_total_non_negative CHECK (total_amount  >= 0), 
	CONSTRAINT chk_online_base_non_negative CHECK (base_amount >= 0), 
	CONSTRAINT chk_online_tax_rate_0_100 CHECK (tax_rate >= 0 AND tax_rate <= 100), 
	CONSTRAINT chk_online_tax_non_negative CHECK (tax_amount >= 0), 
	FOREIGN KEY(customer_id) REFERENCES customers (id) ON DELETE CASCADE, 
	FOREIGN KEY(cart_id) REFERENCES online_carts (id) ON DELETE SET NULL, 
	FOREIGN KEY(warehouse_id) REFERENCES warehouses (id) ON DELETE SET NULL
);

CREATE INDEX ix_online_preorders_status ON online_preorders (status);

CREATE INDEX ix_online_preorders_updated_at ON online_preorders (updated_at);

CREATE INDEX ix_online_preorders_warehouse_id ON online_preorders (warehouse_id);

CREATE INDEX ix_online_preorders_created_at ON online_preorders (created_at);

CREATE INDEX ix_online_preorders_status_paystatus ON online_preorders (status, payment_status);

CREATE UNIQUE INDEX ix_online_preorders_order_number ON online_preorders (order_number);

CREATE INDEX ix_online_preorders_customer_status ON online_preorders (customer_id, status);

CREATE INDEX ix_online_preorders_customer_id ON online_preorders (customer_id);

CREATE INDEX ix_online_preorders_payment_status ON online_preorders (payment_status);

CREATE TABLE stock_adjustments (
	id SERIAL NOT NULL, 
	date TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	warehouse_id INTEGER, 
	reason VARCHAR(20) NOT NULL, 
	notes TEXT, 
	total_cost NUMERIC(12, 2) NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_stock_adjustment_reason_allowed CHECK (reason IN ('DAMAGED','STORE_USE')), 
	CONSTRAINT ck_stock_adjustment_total_cost_non_negative CHECK (total_cost >= 0), 
	FOREIGN KEY(warehouse_id) REFERENCES warehouses (id) ON DELETE SET NULL
);

CREATE INDEX ix_stock_adjustments_updated_at ON stock_adjustments (updated_at);

CREATE INDEX ix_stock_adjust_wh_reason_date ON stock_adjustments (warehouse_id, reason, date);

CREATE INDEX ix_stock_adjustments_date ON stock_adjustments (date);

CREATE INDEX ix_stock_adjustments_created_at ON stock_adjustments (created_at);

CREATE INDEX ix_stock_adjustments_warehouse_id ON stock_adjustments (warehouse_id);

CREATE INDEX ix_stock_adjustments_reason ON stock_adjustments (reason);

CREATE TABLE budget_commitments (
	id SERIAL NOT NULL, 
	budget_id INTEGER NOT NULL, 
	source_type VARCHAR(8) NOT NULL, 
	source_id INTEGER NOT NULL, 
	committed_amount NUMERIC(12, 2) NOT NULL, 
	commitment_date DATE NOT NULL, 
	status VARCHAR(9) NOT NULL, 
	notes TEXT, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_commitment_source UNIQUE (source_type, source_id), 
	CONSTRAINT ck_commitment_amount_ge_0 CHECK (committed_amount >= 0), 
	FOREIGN KEY(budget_id) REFERENCES budgets (id) ON DELETE CASCADE
);

CREATE INDEX ix_budget_commitments_status ON budget_commitments (status);

CREATE INDEX ix_budget_commitments_source_id ON budget_commitments (source_id);

CREATE INDEX ix_budget_commitments_budget_id ON budget_commitments (budget_id);

CREATE INDEX ix_budget_commitments_commitment_date ON budget_commitments (commitment_date);

CREATE INDEX ix_commitment_budget_status ON budget_commitments (budget_id, status);

CREATE INDEX ix_budget_commitments_updated_at ON budget_commitments (updated_at);

CREATE INDEX ix_budget_commitments_created_at ON budget_commitments (created_at);

CREATE INDEX ix_budget_commitments_source_type ON budget_commitments (source_type);

CREATE TABLE asset_depreciations (
	id SERIAL NOT NULL, 
	asset_id INTEGER NOT NULL, 
	fiscal_year INTEGER NOT NULL, 
	fiscal_month INTEGER, 
	depreciation_date DATE NOT NULL, 
	depreciation_amount NUMERIC(12, 2) NOT NULL, 
	accumulated_depreciation NUMERIC(12, 2) NOT NULL, 
	book_value NUMERIC(12, 2) NOT NULL, 
	gl_batch_id INTEGER, 
	notes TEXT, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_depreciation_asset_period UNIQUE (asset_id, fiscal_year, fiscal_month), 
	CONSTRAINT ck_depreciation_amount_ge_0 CHECK (depreciation_amount >= 0), 
	CONSTRAINT ck_fiscal_month_range CHECK (fiscal_month >= 1 AND fiscal_month <= 12), 
	FOREIGN KEY(asset_id) REFERENCES fixed_assets (id) ON DELETE CASCADE, 
	FOREIGN KEY(gl_batch_id) REFERENCES gl_batches (id)
);

CREATE INDEX ix_asset_depreciations_fiscal_month ON asset_depreciations (fiscal_month);

CREATE INDEX ix_depreciation_year_month ON asset_depreciations (fiscal_year, fiscal_month);

CREATE INDEX ix_asset_depreciations_fiscal_year ON asset_depreciations (fiscal_year);

CREATE INDEX ix_asset_depreciations_created_at ON asset_depreciations (created_at);

CREATE INDEX ix_asset_depreciations_gl_batch_id ON asset_depreciations (gl_batch_id);

CREATE INDEX ix_asset_depreciations_depreciation_date ON asset_depreciations (depreciation_date);

CREATE INDEX ix_asset_depreciations_asset_id ON asset_depreciations (asset_id);

CREATE INDEX ix_asset_depreciations_updated_at ON asset_depreciations (updated_at);

CREATE TABLE project_costs (
	id SERIAL NOT NULL, 
	project_id INTEGER NOT NULL, 
	phase_id INTEGER, 
	cost_type VARCHAR(8) NOT NULL, 
	source_id INTEGER, 
	amount NUMERIC(15, 2) NOT NULL, 
	cost_date DATE NOT NULL, 
	description TEXT, 
	gl_batch_id INTEGER, 
	notes TEXT, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_project_cost_amount_ge_0 CHECK (amount >= 0), 
	FOREIGN KEY(project_id) REFERENCES projects (id) ON DELETE CASCADE, 
	FOREIGN KEY(phase_id) REFERENCES project_phases (id) ON DELETE SET NULL, 
	FOREIGN KEY(gl_batch_id) REFERENCES gl_batches (id)
);

CREATE INDEX ix_project_costs_created_at ON project_costs (created_at);

CREATE INDEX ix_project_costs_gl_batch_id ON project_costs (gl_batch_id);

CREATE INDEX ix_project_costs_project_id ON project_costs (project_id);

CREATE INDEX ix_project_costs_source_id ON project_costs (source_id);

CREATE INDEX ix_project_costs_cost_type ON project_costs (cost_type);

CREATE INDEX ix_project_costs_phase_id ON project_costs (phase_id);

CREATE INDEX ix_project_costs_cost_date ON project_costs (cost_date);

CREATE INDEX ix_project_cost_date ON project_costs (project_id, cost_date);

CREATE INDEX ix_project_costs_updated_at ON project_costs (updated_at);

CREATE TABLE project_revenues (
	id SERIAL NOT NULL, 
	project_id INTEGER NOT NULL, 
	phase_id INTEGER, 
	revenue_type VARCHAR(9) NOT NULL, 
	source_id INTEGER, 
	amount NUMERIC(15, 2) NOT NULL, 
	revenue_date DATE NOT NULL, 
	description TEXT, 
	gl_batch_id INTEGER, 
	notes TEXT, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_project_revenue_amount_ge_0 CHECK (amount >= 0), 
	FOREIGN KEY(project_id) REFERENCES projects (id) ON DELETE CASCADE, 
	FOREIGN KEY(phase_id) REFERENCES project_phases (id) ON DELETE SET NULL, 
	FOREIGN KEY(gl_batch_id) REFERENCES gl_batches (id)
);

CREATE INDEX ix_project_revenues_phase_id ON project_revenues (phase_id);

CREATE INDEX ix_project_revenues_created_at ON project_revenues (created_at);

CREATE INDEX ix_project_revenues_gl_batch_id ON project_revenues (gl_batch_id);

CREATE INDEX ix_project_revenues_source_id ON project_revenues (source_id);

CREATE INDEX ix_project_revenues_revenue_type ON project_revenues (revenue_type);

CREATE INDEX ix_project_revenues_revenue_date ON project_revenues (revenue_date);

CREATE INDEX ix_project_revenues_project_id ON project_revenues (project_id);

CREATE INDEX ix_project_revenue_date ON project_revenues (project_id, revenue_date);

CREATE INDEX ix_project_revenues_updated_at ON project_revenues (updated_at);

CREATE TABLE project_tasks (
	id SERIAL NOT NULL, 
	project_id INTEGER NOT NULL, 
	phase_id INTEGER, 
	task_number VARCHAR(50) NOT NULL, 
	name VARCHAR(300) NOT NULL, 
	description TEXT, 
	assigned_to INTEGER, 
	priority VARCHAR(8) NOT NULL, 
	status VARCHAR(11) NOT NULL, 
	start_date DATE NOT NULL, 
	due_date DATE NOT NULL, 
	completed_date DATE, 
	estimated_hours NUMERIC(8, 2), 
	actual_hours NUMERIC(8, 2), 
	completion_percentage NUMERIC(5, 2), 
	depends_on JSON, 
	blocked_reason TEXT, 
	notes TEXT, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_task_est_hours_ge_0 CHECK (estimated_hours >= 0), 
	CONSTRAINT ck_task_actual_hours_ge_0 CHECK (actual_hours >= 0), 
	CONSTRAINT ck_task_completion_range CHECK (completion_percentage >= 0 AND completion_percentage <= 100), 
	FOREIGN KEY(project_id) REFERENCES projects (id) ON DELETE CASCADE, 
	FOREIGN KEY(phase_id) REFERENCES project_phases (id) ON DELETE SET NULL, 
	FOREIGN KEY(assigned_to) REFERENCES users (id)
);

CREATE INDEX ix_project_tasks_status ON project_tasks (status);

CREATE INDEX ix_project_tasks_updated_at ON project_tasks (updated_at);

CREATE INDEX ix_project_tasks_project_id ON project_tasks (project_id);

CREATE INDEX ix_project_task_project_status ON project_tasks (project_id, status);

CREATE INDEX ix_project_tasks_phase_id ON project_tasks (phase_id);

CREATE INDEX ix_project_tasks_priority ON project_tasks (priority);

CREATE INDEX ix_project_tasks_assigned_to ON project_tasks (assigned_to);

CREATE INDEX ix_project_tasks_due_date ON project_tasks (due_date);

CREATE INDEX ix_project_tasks_start_date ON project_tasks (start_date);

CREATE INDEX ix_project_task_assigned_status ON project_tasks (assigned_to, status);

CREATE INDEX ix_project_tasks_created_at ON project_tasks (created_at);

CREATE INDEX ix_project_tasks_name ON project_tasks (name);

CREATE INDEX ix_project_tasks_completed_date ON project_tasks (completed_date);

CREATE INDEX ix_project_tasks_task_number ON project_tasks (task_number);

CREATE TABLE cost_allocation_execution_lines (
	id SERIAL NOT NULL, 
	execution_id INTEGER NOT NULL, 
	source_cost_center_id INTEGER, 
	target_cost_center_id INTEGER, 
	amount NUMERIC(15, 2) NOT NULL, 
	percentage NUMERIC(5, 2), 
	gl_batch_id INTEGER, 
	PRIMARY KEY (id), 
	FOREIGN KEY(execution_id) REFERENCES cost_allocation_executions (id) ON DELETE CASCADE, 
	FOREIGN KEY(source_cost_center_id) REFERENCES cost_centers (id), 
	FOREIGN KEY(target_cost_center_id) REFERENCES cost_centers (id), 
	FOREIGN KEY(gl_batch_id) REFERENCES gl_batches (id)
);

CREATE INDEX ix_cost_allocation_execution_lines_execution_id ON cost_allocation_execution_lines (execution_id);

CREATE INDEX ix_cost_allocation_execution_lines_target_cost_center_id ON cost_allocation_execution_lines (target_cost_center_id);

CREATE INDEX ix_cost_allocation_execution_lines_source_cost_center_id ON cost_allocation_execution_lines (source_cost_center_id);

CREATE TABLE engineering_teams (
	id SERIAL NOT NULL, 
	code VARCHAR(20) NOT NULL, 
	name VARCHAR(200) NOT NULL, 
	team_leader_id INTEGER, 
	specialty VARCHAR(11) NOT NULL, 
	cost_center_id INTEGER, 
	branch_id INTEGER, 
	max_concurrent_tasks INTEGER DEFAULT 5 NOT NULL, 
	is_active BOOLEAN DEFAULT true NOT NULL, 
	description TEXT, 
	equipment_inventory JSON, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(team_leader_id) REFERENCES employees (id), 
	FOREIGN KEY(cost_center_id) REFERENCES cost_centers (id), 
	FOREIGN KEY(branch_id) REFERENCES branches (id)
);

CREATE INDEX ix_engineering_teams_cost_center_id ON engineering_teams (cost_center_id);

CREATE INDEX ix_eng_team_active ON engineering_teams (is_active);

CREATE INDEX ix_engineering_teams_updated_at ON engineering_teams (updated_at);

CREATE INDEX ix_eng_team_specialty ON engineering_teams (specialty);

CREATE UNIQUE INDEX ix_engineering_teams_code ON engineering_teams (code);

CREATE INDEX ix_engineering_teams_created_at ON engineering_teams (created_at);

CREATE INDEX ix_engineering_teams_branch_id ON engineering_teams (branch_id);

CREATE INDEX ix_engineering_teams_team_leader_id ON engineering_teams (team_leader_id);

CREATE INDEX ix_engineering_teams_name ON engineering_teams (name);

CREATE TABLE employee_skills (
	id SERIAL NOT NULL, 
	employee_id INTEGER NOT NULL, 
	skill_id INTEGER NOT NULL, 
	proficiency_level VARCHAR(12) NOT NULL, 
	years_experience INTEGER DEFAULT 0 NOT NULL, 
	certification_number VARCHAR(100), 
	certification_authority VARCHAR(200), 
	certification_date DATE, 
	expiry_date DATE, 
	verified_by INTEGER, 
	verification_date DATE, 
	notes TEXT, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_employee_skill UNIQUE (employee_id, skill_id), 
	FOREIGN KEY(employee_id) REFERENCES employees (id) ON DELETE CASCADE, 
	FOREIGN KEY(skill_id) REFERENCES engineering_skills (id), 
	FOREIGN KEY(verified_by) REFERENCES users (id)
);

CREATE INDEX ix_employee_skills_skill_id ON employee_skills (skill_id);

CREATE INDEX ix_employee_skill_expiry ON employee_skills (expiry_date);

CREATE INDEX ix_employee_skills_updated_at ON employee_skills (updated_at);

CREATE INDEX ix_employee_skills_created_at ON employee_skills (created_at);

CREATE INDEX ix_employee_skills_employee_id ON employee_skills (employee_id);

CREATE TABLE supplier_settlement_lines (
	id SERIAL NOT NULL, 
	settlement_id INTEGER NOT NULL, 
	source_type VARCHAR(30) NOT NULL, 
	source_id INTEGER, 
	description VARCHAR(255), 
	product_id INTEGER, 
	quantity NUMERIC(12, 3), 
	unit_price NUMERIC(12, 2), 
	gross_amount NUMERIC(12, 2), 
	needs_pricing BOOLEAN NOT NULL, 
	cost_source VARCHAR(20), 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(settlement_id) REFERENCES supplier_settlements (id) ON DELETE CASCADE, 
	FOREIGN KEY(product_id) REFERENCES products (id)
);

CREATE INDEX ix_supplier_settlement_lines_updated_at ON supplier_settlement_lines (updated_at);

CREATE INDEX ix_supplier_settlement_lines_settlement_id ON supplier_settlement_lines (settlement_id);

CREATE INDEX ix_supplier_settlement_lines_source_id ON supplier_settlement_lines (source_id);

CREATE INDEX ix_supplier_settlement_lines_created_at ON supplier_settlement_lines (created_at);

CREATE INDEX ix_supplier_settle_line_product ON supplier_settlement_lines (product_id);

CREATE INDEX ix_supplier_settlement_lines_needs_pricing ON supplier_settlement_lines (needs_pricing);

CREATE TABLE partner_settlement_lines (
	id SERIAL NOT NULL, 
	settlement_id INTEGER NOT NULL, 
	source_type VARCHAR(30) NOT NULL, 
	source_id INTEGER, 
	description VARCHAR(255), 
	product_id INTEGER, 
	warehouse_id INTEGER, 
	quantity NUMERIC(12, 3), 
	unit_price NUMERIC(12, 2), 
	gross_amount NUMERIC(12, 2), 
	share_percent NUMERIC(6, 3), 
	share_amount NUMERIC(12, 2), 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(settlement_id) REFERENCES partner_settlements (id) ON DELETE CASCADE, 
	FOREIGN KEY(product_id) REFERENCES products (id), 
	FOREIGN KEY(warehouse_id) REFERENCES warehouses (id)
);

CREATE INDEX ix_partner_settle_line_product ON partner_settlement_lines (product_id);

CREATE INDEX ix_partner_settlement_lines_created_at ON partner_settlement_lines (created_at);

CREATE INDEX ix_partner_settle_line_warehouse ON partner_settlement_lines (warehouse_id);

CREATE INDEX ix_partner_settlement_lines_settlement_id ON partner_settlement_lines (settlement_id);

CREATE INDEX ix_partner_settlement_lines_updated_at ON partner_settlement_lines (updated_at);

CREATE INDEX ix_partner_settlement_lines_source_id ON partner_settlement_lines (source_id);

CREATE INDEX ix_partner_settlement_lines_source_type ON partner_settlement_lines (source_type);

CREATE TABLE stock_levels (
	id SERIAL NOT NULL, 
	product_id INTEGER NOT NULL, 
	warehouse_id INTEGER NOT NULL, 
	quantity INTEGER DEFAULT 0 NOT NULL, 
	reserved_quantity INTEGER DEFAULT 0 NOT NULL, 
	min_stock INTEGER, 
	max_stock INTEGER, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_stock_non_negative CHECK (quantity >= 0), 
	CONSTRAINT ck_reserved_non_negative CHECK (reserved_quantity >= 0), 
	CONSTRAINT ck_min_non_negative CHECK ((min_stock IS NULL OR min_stock >= 0)), 
	CONSTRAINT ck_max_non_negative CHECK ((max_stock IS NULL OR max_stock >= 0)), 
	CONSTRAINT ck_max_ge_min CHECK ((min_stock IS NULL OR max_stock IS NULL OR max_stock >= min_stock)), 
	CONSTRAINT uq_stock_product_wh UNIQUE (product_id, warehouse_id), 
	FOREIGN KEY(product_id) REFERENCES products (id), 
	FOREIGN KEY(warehouse_id) REFERENCES warehouses (id)
);

CREATE INDEX ix_stock_levels_warehouse_id ON stock_levels (warehouse_id);

CREATE INDEX ix_stock_levels_created_at ON stock_levels (created_at);

CREATE INDEX ix_stock_product_wh ON stock_levels (product_id, warehouse_id);

CREATE INDEX ix_stock_levels_product_id ON stock_levels (product_id);

CREATE INDEX ix_stock_levels_updated_at ON stock_levels (updated_at);

CREATE INDEX ix_stock_quantity ON stock_levels (quantity);

CREATE TABLE transfers (
	id SERIAL NOT NULL, 
	reference VARCHAR(50), 
	product_id INTEGER NOT NULL, 
	source_id INTEGER NOT NULL, 
	destination_id INTEGER NOT NULL, 
	quantity INTEGER NOT NULL, 
	direction VARCHAR(10) NOT NULL, 
	transfer_date TIMESTAMP WITHOUT TIME ZONE, 
	notes TEXT, 
	user_id INTEGER, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT chk_transfer_qty_positive CHECK (quantity > 0), 
	CONSTRAINT chk_transfer_diff_wh CHECK (source_id <> destination_id), 
	UNIQUE (reference), 
	FOREIGN KEY(product_id) REFERENCES products (id), 
	FOREIGN KEY(source_id) REFERENCES warehouses (id), 
	FOREIGN KEY(destination_id) REFERENCES warehouses (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);

CREATE INDEX ix_transfers_created_at ON transfers (created_at);

CREATE INDEX ix_transfers_transfer_date ON transfers (transfer_date);

CREATE INDEX ix_transfers_updated_at ON transfers (updated_at);

CREATE TABLE exchange_transactions (
	id SERIAL NOT NULL, 
	product_id INTEGER NOT NULL, 
	warehouse_id INTEGER NOT NULL, 
	supplier_id INTEGER, 
	partner_id INTEGER, 
	quantity INTEGER NOT NULL, 
	direction VARCHAR(10) DEFAULT 'IN' NOT NULL, 
	unit_cost NUMERIC(12, 2), 
	is_priced BOOLEAN DEFAULT false NOT NULL, 
	notes TEXT, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT chk_exchange_qty_positive CHECK (quantity > 0), 
	CONSTRAINT ck_exchange_unit_cost_non_negative CHECK (unit_cost IS NULL OR unit_cost >= 0), 
	FOREIGN KEY(product_id) REFERENCES products (id), 
	FOREIGN KEY(warehouse_id) REFERENCES warehouses (id), 
	FOREIGN KEY(supplier_id) REFERENCES suppliers (id), 
	FOREIGN KEY(partner_id) REFERENCES partners (id)
);

CREATE INDEX ix_exchange_prod_wh ON exchange_transactions (product_id, warehouse_id);

CREATE INDEX ix_exchange_transactions_created_at ON exchange_transactions (created_at);

CREATE INDEX ix_exchange_transactions_warehouse_id ON exchange_transactions (warehouse_id);

CREATE INDEX ix_exchange_transactions_direction ON exchange_transactions (direction);

CREATE INDEX ix_exchange_supplier_dir_created_at ON exchange_transactions (supplier_id, direction, created_at);

CREATE INDEX ix_exchange_transactions_updated_at ON exchange_transactions (updated_at);

CREATE INDEX ix_exchange_partner_dir_created_at ON exchange_transactions (partner_id, direction, created_at);

CREATE INDEX ix_exchange_supplier ON exchange_transactions (supplier_id);

CREATE INDEX ix_exchange_transactions_product_id ON exchange_transactions (product_id);

CREATE TABLE warehouse_partner_shares (
	id SERIAL NOT NULL, 
	partner_id INTEGER NOT NULL, 
	warehouse_id INTEGER, 
	product_id INTEGER, 
	share_percentage FLOAT NOT NULL, 
	share_amount NUMERIC(12, 2), 
	notes TEXT, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_wps_partner_wh_prod UNIQUE (partner_id, warehouse_id, product_id), 
	CONSTRAINT ck_wps_share_percentage_range CHECK (share_percentage >= 0 AND share_percentage <= 100), 
	CONSTRAINT ck_wps_share_amount_non_negative CHECK (share_amount >= 0), 
	FOREIGN KEY(partner_id) REFERENCES partners (id), 
	FOREIGN KEY(warehouse_id) REFERENCES warehouses (id), 
	FOREIGN KEY(product_id) REFERENCES products (id)
);

CREATE INDEX ix_warehouse_partner_shares_created_at ON warehouse_partner_shares (created_at);

CREATE INDEX ix_wps_partner_wh_prod ON warehouse_partner_shares (partner_id, warehouse_id, product_id);

CREATE INDEX ix_warehouse_partner_shares_product_id ON warehouse_partner_shares (product_id);

CREATE INDEX ix_warehouse_partner_shares_partner_id ON warehouse_partner_shares (partner_id);

CREATE INDEX ix_wps_share_percentage ON warehouse_partner_shares (share_percentage);

CREATE INDEX ix_warehouse_partner_shares_warehouse_id ON warehouse_partner_shares (warehouse_id);

CREATE INDEX ix_warehouse_partner_shares_updated_at ON warehouse_partner_shares (updated_at);

CREATE TABLE product_partners (
	id SERIAL NOT NULL, 
	product_id INTEGER NOT NULL, 
	partner_id INTEGER NOT NULL, 
	share_percent FLOAT NOT NULL, 
	share_amount NUMERIC(12, 2), 
	notes TEXT, 
	PRIMARY KEY (id), 
	CONSTRAINT chk_partner_share CHECK (share_percent >= 0 AND share_percent <= 100), 
	CONSTRAINT ck_product_partner_share_amount_non_negative CHECK (share_amount >= 0), 
	FOREIGN KEY(product_id) REFERENCES products (id), 
	FOREIGN KEY(partner_id) REFERENCES partners (id)
);

CREATE INDEX ix_product_partner_pair ON product_partners (product_id, partner_id);

CREATE TABLE preorders (
	id SERIAL NOT NULL, 
	reference VARCHAR(50), 
	preorder_date TIMESTAMP WITHOUT TIME ZONE, 
	expected_date TIMESTAMP WITHOUT TIME ZONE, 
	customer_id INTEGER, 
	supplier_id INTEGER, 
	partner_id INTEGER, 
	product_id INTEGER NOT NULL, 
	warehouse_id INTEGER NOT NULL, 
	quantity INTEGER NOT NULL, 
	prepaid_amount NUMERIC(12, 2) DEFAULT 0, 
	tax_rate NUMERIC(5, 2) DEFAULT 0, 
	status VARCHAR(9) DEFAULT 'PENDING' NOT NULL, 
	notes TEXT, 
	payment_method VARCHAR(6) DEFAULT 'cash' NOT NULL, 
	currency VARCHAR(10) DEFAULT 'ILS' NOT NULL, 
	fx_rate_used NUMERIC(10, 6), 
	fx_rate_source VARCHAR(20), 
	fx_rate_timestamp TIMESTAMP WITHOUT TIME ZONE, 
	fx_base_currency VARCHAR(10), 
	fx_quote_currency VARCHAR(10), 
	refunded_total NUMERIC(12, 2) DEFAULT 0 NOT NULL, 
	refund_of_id INTEGER, 
	idempotency_key VARCHAR(64), 
	cancelled_at TIMESTAMP WITHOUT TIME ZONE, 
	cancelled_by INTEGER, 
	cancel_reason VARCHAR(200), 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT chk_preorder_quantity_positive CHECK (quantity > 0), 
	CONSTRAINT chk_preorder_prepaid_non_negative CHECK (prepaid_amount >= 0), 
	CONSTRAINT chk_preorder_tax_rate CHECK (tax_rate >= 0 AND tax_rate <= 100), 
	CONSTRAINT chk_preorder_refunded_total_non_negative CHECK (refunded_total >= 0), 
	FOREIGN KEY(customer_id) REFERENCES customers (id), 
	FOREIGN KEY(supplier_id) REFERENCES suppliers (id), 
	FOREIGN KEY(partner_id) REFERENCES partners (id), 
	FOREIGN KEY(product_id) REFERENCES products (id), 
	FOREIGN KEY(warehouse_id) REFERENCES warehouses (id), 
	FOREIGN KEY(refund_of_id) REFERENCES preorders (id) ON DELETE SET NULL, 
	FOREIGN KEY(cancelled_by) REFERENCES users (id)
);

CREATE UNIQUE INDEX ix_preorders_reference ON preorders (reference);

CREATE INDEX ix_preorders_created_at ON preorders (created_at);

CREATE INDEX ix_preorders_warehouse_id ON preorders (warehouse_id);

CREATE INDEX ix_preorders_updated_at ON preorders (updated_at);

CREATE INDEX ix_preorders_cust_status ON preorders (customer_id, status);

CREATE INDEX ix_preorders_partner_status ON preorders (partner_id, status);

CREATE INDEX ix_preorders_status ON preorders (status);

CREATE INDEX ix_preorders_supplier_status ON preorders (supplier_id, status);

CREATE INDEX ix_preorders_prod_wh ON preorders (product_id, warehouse_id);

CREATE UNIQUE INDEX ix_preorders_idempotency_key ON preorders (idempotency_key);

CREATE INDEX ix_preorders_customer_id ON preorders (customer_id);

CREATE INDEX ix_preorders_supplier_id ON preorders (supplier_id);

CREATE INDEX ix_preorders_date_status ON preorders (preorder_date, status);

CREATE INDEX ix_preorders_pay_method ON preorders (payment_method);

CREATE INDEX ix_preorders_cancelled_at ON preorders (cancelled_at);

CREATE INDEX ix_preorders_prepaid ON preorders (prepaid_amount);

CREATE INDEX ix_preorders_refund_of_id ON preorders (refund_of_id);

CREATE INDEX ix_preorders_cancelled_by ON preorders (cancelled_by);

CREATE INDEX ix_preorders_preorder_date ON preorders (preorder_date);

CREATE INDEX ix_preorders_product_id ON preorders (product_id);

CREATE TABLE product_supplier_loans (
	id SERIAL NOT NULL, 
	product_id INTEGER NOT NULL, 
	supplier_id INTEGER NOT NULL, 
	loan_value NUMERIC(12, 2) NOT NULL, 
	deferred_price NUMERIC(12, 2), 
	is_settled BOOLEAN, 
	partner_share_quantity INTEGER NOT NULL, 
	partner_share_value NUMERIC(12, 2) NOT NULL, 
	notes TEXT, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_psl_loan_value_ge_0 CHECK (loan_value >= 0), 
	CONSTRAINT ck_psl_deferred_price_ge_0 CHECK (deferred_price IS NULL OR deferred_price >= 0), 
	CONSTRAINT ck_psl_share_qty_ge_0 CHECK (partner_share_quantity >= 0), 
	CONSTRAINT ck_psl_share_val_ge_0 CHECK (partner_share_value >= 0), 
	FOREIGN KEY(product_id) REFERENCES products (id), 
	FOREIGN KEY(supplier_id) REFERENCES suppliers (id)
);

CREATE INDEX ix_product_supplier_loans_updated_at ON product_supplier_loans (updated_at);

CREATE INDEX ix_product_supplier_loans_product_id ON product_supplier_loans (product_id);

CREATE INDEX ix_product_supplier_loans_created_at ON product_supplier_loans (created_at);

CREATE INDEX ix_psl_product_supplier ON product_supplier_loans (product_id, supplier_id);

CREATE INDEX ix_product_supplier_loans_supplier_id ON product_supplier_loans (supplier_id);

CREATE INDEX ix_product_supplier_loans_is_settled ON product_supplier_loans (is_settled);

CREATE INDEX ix_psl_supplier_settled ON product_supplier_loans (supplier_id, is_settled);

CREATE TABLE service_parts (
	id SERIAL NOT NULL, 
	service_id INTEGER NOT NULL, 
	part_id INTEGER NOT NULL, 
	warehouse_id INTEGER NOT NULL, 
	quantity INTEGER NOT NULL, 
	unit_price NUMERIC(10, 2) NOT NULL, 
	discount NUMERIC(12, 2), 
	tax_rate NUMERIC(5, 2), 
	note VARCHAR(200), 
	notes TEXT, 
	partner_id INTEGER, 
	share_percentage NUMERIC(5, 2), 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT chk_service_part_qty_positive CHECK (quantity > 0), 
	CONSTRAINT chk_service_part_price_non_negative CHECK (unit_price >= 0), 
	CONSTRAINT chk_service_part_discount_positive CHECK (discount >= 0), 
	CONSTRAINT chk_service_part_discount_max CHECK (discount <= quantity * unit_price), 
	CONSTRAINT chk_service_part_tax_range CHECK (tax_rate >= 0 AND tax_rate <= 100), 
	CONSTRAINT chk_service_part_share_range CHECK (share_percentage >= 0 AND share_percentage <= 100), 
	CONSTRAINT uq_service_part_unique UNIQUE (service_id, part_id, warehouse_id), 
	FOREIGN KEY(service_id) REFERENCES service_requests (id) ON DELETE CASCADE, 
	FOREIGN KEY(part_id) REFERENCES products (id), 
	FOREIGN KEY(warehouse_id) REFERENCES warehouses (id), 
	FOREIGN KEY(partner_id) REFERENCES partners (id)
);

CREATE INDEX ix_service_parts_warehouse_id ON service_parts (warehouse_id);

CREATE INDEX ix_service_parts_created_at ON service_parts (created_at);

CREATE INDEX ix_service_part_pair ON service_parts (service_id, part_id);

CREATE INDEX ix_service_parts_part_id ON service_parts (part_id);

CREATE INDEX ix_service_part_partner ON service_parts (partner_id);

CREATE INDEX ix_service_parts_updated_at ON service_parts (updated_at);

CREATE TABLE online_cart_items (
	id SERIAL NOT NULL, 
	cart_id INTEGER NOT NULL, 
	product_id INTEGER NOT NULL, 
	quantity INTEGER NOT NULL, 
	price NUMERIC(12, 2) NOT NULL, 
	added_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	CONSTRAINT chk_cart_item_qty_positive CHECK (quantity > 0), 
	CONSTRAINT chk_cart_item_price_non_negative CHECK (price >= 0), 
	CONSTRAINT uq_cart_item_cart_product UNIQUE (cart_id, product_id), 
	FOREIGN KEY(cart_id) REFERENCES online_carts (id) ON DELETE CASCADE, 
	FOREIGN KEY(product_id) REFERENCES products (id) ON DELETE RESTRICT
);

CREATE INDEX ix_online_cart_items_product_id ON online_cart_items (product_id);

CREATE INDEX ix_cart_item_cart_product ON online_cart_items (cart_id, product_id);

CREATE INDEX ix_online_cart_items_cart_id ON online_cart_items (cart_id);

CREATE INDEX ix_online_cart_items_added_at ON online_cart_items (added_at);

CREATE TABLE online_preorder_items (
	id SERIAL NOT NULL, 
	order_id INTEGER NOT NULL, 
	product_id INTEGER NOT NULL, 
	quantity INTEGER NOT NULL, 
	price NUMERIC(12, 2) NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT chk_online_item_qty_positive CHECK (quantity > 0), 
	CONSTRAINT chk_online_item_price_non_negative CHECK (price >= 0), 
	CONSTRAINT uq_online_item_order_product UNIQUE (order_id, product_id), 
	FOREIGN KEY(order_id) REFERENCES online_preorders (id) ON DELETE CASCADE, 
	FOREIGN KEY(product_id) REFERENCES products (id) ON DELETE RESTRICT
);

CREATE INDEX ix_online_preorder_items_product_id ON online_preorder_items (product_id);

CREATE INDEX ix_online_item_order_product ON online_preorder_items (order_id, product_id);

CREATE INDEX ix_online_preorder_items_order_id ON online_preorder_items (order_id);

CREATE TABLE stock_adjustment_items (
	id SERIAL NOT NULL, 
	adjustment_id INTEGER NOT NULL, 
	product_id INTEGER NOT NULL, 
	warehouse_id INTEGER, 
	quantity INTEGER NOT NULL, 
	unit_cost NUMERIC(12, 2) NOT NULL, 
	notes VARCHAR(200), 
	PRIMARY KEY (id), 
	CONSTRAINT ck_stock_adjustment_item_qty_positive CHECK (quantity > 0), 
	CONSTRAINT ck_stock_adjustment_item_cost_non_negative CHECK (unit_cost >= 0), 
	FOREIGN KEY(adjustment_id) REFERENCES stock_adjustments (id) ON DELETE CASCADE, 
	FOREIGN KEY(product_id) REFERENCES products (id), 
	FOREIGN KEY(warehouse_id) REFERENCES warehouses (id) ON DELETE SET NULL
);

CREATE INDEX ix_sai_prod_wh ON stock_adjustment_items (product_id, warehouse_id);

CREATE INDEX ix_stock_adjustment_items_adjustment_id ON stock_adjustment_items (adjustment_id);

CREATE INDEX ix_stock_adjustment_items_warehouse_id ON stock_adjustment_items (warehouse_id);

CREATE INDEX ix_stock_adjustment_items_product_id ON stock_adjustment_items (product_id);

CREATE TABLE product_ratings (
	id SERIAL NOT NULL, 
	product_id INTEGER NOT NULL, 
	customer_id INTEGER, 
	rating INTEGER NOT NULL, 
	title VARCHAR(255), 
	comment TEXT, 
	is_verified_purchase BOOLEAN NOT NULL, 
	is_approved BOOLEAN NOT NULL, 
	helpful_count INTEGER NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_rating_range CHECK (rating >= 1 AND rating <= 5), 
	FOREIGN KEY(product_id) REFERENCES products (id), 
	FOREIGN KEY(customer_id) REFERENCES customers (id)
);

CREATE INDEX ix_product_ratings_product_id ON product_ratings (product_id);

CREATE INDEX ix_product_ratings_created_at ON product_ratings (created_at);

CREATE INDEX ix_product_ratings_rating ON product_ratings (rating);

CREATE INDEX ix_product_ratings_updated_at ON product_ratings (updated_at);

CREATE INDEX ix_product_ratings_customer_id ON product_ratings (customer_id);

CREATE TABLE project_resources (
	id SERIAL NOT NULL, 
	project_id INTEGER NOT NULL, 
	task_id INTEGER, 
	resource_type VARCHAR(13) NOT NULL, 
	employee_id INTEGER, 
	product_id INTEGER, 
	resource_name VARCHAR(200), 
	quantity NUMERIC(10, 2) NOT NULL, 
	unit_cost NUMERIC(12, 2) NOT NULL, 
	total_cost NUMERIC(15, 2) NOT NULL, 
	allocation_date DATE NOT NULL, 
	start_date DATE, 
	end_date DATE, 
	hours_allocated NUMERIC(8, 2), 
	hours_used NUMERIC(8, 2), 
	status VARCHAR(9) NOT NULL, 
	notes TEXT, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_resource_quantity_gt_0 CHECK (quantity > 0), 
	CONSTRAINT ck_resource_unit_cost_ge_0 CHECK (unit_cost >= 0), 
	CONSTRAINT ck_resource_hours_alloc_ge_0 CHECK (hours_allocated >= 0), 
	CONSTRAINT ck_resource_hours_used_ge_0 CHECK (hours_used >= 0), 
	FOREIGN KEY(project_id) REFERENCES projects (id) ON DELETE CASCADE, 
	FOREIGN KEY(task_id) REFERENCES project_tasks (id) ON DELETE CASCADE, 
	FOREIGN KEY(employee_id) REFERENCES employees (id), 
	FOREIGN KEY(product_id) REFERENCES products (id)
);

CREATE INDEX ix_project_resources_status ON project_resources (status);

CREATE INDEX ix_project_resources_allocation_date ON project_resources (allocation_date);

CREATE INDEX ix_project_resources_product_id ON project_resources (product_id);

CREATE INDEX ix_project_resource_project_type ON project_resources (project_id, resource_type);

CREATE INDEX ix_project_resources_end_date ON project_resources (end_date);

CREATE INDEX ix_project_resources_updated_at ON project_resources (updated_at);

CREATE INDEX ix_project_resources_start_date ON project_resources (start_date);

CREATE INDEX ix_project_resources_employee_id ON project_resources (employee_id);

CREATE INDEX ix_project_resources_created_at ON project_resources (created_at);

CREATE INDEX ix_project_resources_resource_type ON project_resources (resource_type);

CREATE INDEX ix_project_resources_project_id ON project_resources (project_id);

CREATE INDEX ix_project_resources_task_id ON project_resources (task_id);

CREATE TABLE project_issues (
	id SERIAL NOT NULL, 
	project_id INTEGER NOT NULL, 
	task_id INTEGER, 
	issue_number VARCHAR(50) NOT NULL, 
	title VARCHAR(300) NOT NULL, 
	description TEXT NOT NULL, 
	category VARCHAR(8) NOT NULL, 
	severity VARCHAR(8) NOT NULL, 
	priority VARCHAR(6) NOT NULL, 
	status VARCHAR(11) NOT NULL, 
	reported_by INTEGER, 
	assigned_to INTEGER, 
	reported_date DATE NOT NULL, 
	resolved_date DATE, 
	resolution TEXT, 
	cost_impact NUMERIC(15, 2), 
	schedule_impact_days INTEGER, 
	root_cause TEXT, 
	preventive_action TEXT, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(project_id) REFERENCES projects (id) ON DELETE CASCADE, 
	FOREIGN KEY(task_id) REFERENCES project_tasks (id) ON DELETE SET NULL, 
	FOREIGN KEY(reported_by) REFERENCES users (id), 
	FOREIGN KEY(assigned_to) REFERENCES users (id)
);

CREATE INDEX ix_project_issues_created_at ON project_issues (created_at);

CREATE INDEX ix_project_issues_updated_at ON project_issues (updated_at);

CREATE INDEX ix_issue_project_status ON project_issues (project_id, status);

CREATE INDEX ix_project_issues_issue_number ON project_issues (issue_number);

CREATE INDEX ix_project_issues_project_id ON project_issues (project_id);

CREATE INDEX ix_issue_severity_priority ON project_issues (severity, priority);

CREATE INDEX ix_project_issues_resolved_date ON project_issues (resolved_date);

CREATE INDEX ix_project_issues_reported_by ON project_issues (reported_by);

CREATE INDEX ix_project_issues_status ON project_issues (status);

CREATE INDEX ix_project_issues_task_id ON project_issues (task_id);

CREATE INDEX ix_project_issues_reported_date ON project_issues (reported_date);

CREATE INDEX ix_project_issues_severity ON project_issues (severity);

CREATE INDEX ix_project_issues_category ON project_issues (category);

CREATE INDEX ix_project_issues_assigned_to ON project_issues (assigned_to);

CREATE INDEX ix_project_issues_priority ON project_issues (priority);

CREATE TABLE engineering_team_members (
	id SERIAL NOT NULL, 
	team_id INTEGER NOT NULL, 
	employee_id INTEGER NOT NULL, 
	role VARCHAR(10) NOT NULL, 
	join_date DATE DEFAULT CURRENT_DATE NOT NULL, 
	leave_date DATE, 
	hourly_rate NUMERIC(10, 2), 
	is_active BOOLEAN DEFAULT true NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_team_member UNIQUE (team_id, employee_id), 
	FOREIGN KEY(team_id) REFERENCES engineering_teams (id) ON DELETE CASCADE, 
	FOREIGN KEY(employee_id) REFERENCES employees (id)
);

CREATE INDEX ix_engineering_team_members_team_id ON engineering_team_members (team_id);

CREATE INDEX ix_team_member_active ON engineering_team_members (is_active);

CREATE INDEX ix_engineering_team_members_created_at ON engineering_team_members (created_at);

CREATE INDEX ix_engineering_team_members_updated_at ON engineering_team_members (updated_at);

CREATE INDEX ix_engineering_team_members_employee_id ON engineering_team_members (employee_id);

CREATE TABLE engineering_tasks (
	id SERIAL NOT NULL, 
	task_number VARCHAR(50) NOT NULL, 
	title VARCHAR(300) NOT NULL, 
	description TEXT, 
	task_type VARCHAR(12) NOT NULL, 
	priority VARCHAR(8) DEFAULT 'MEDIUM' NOT NULL, 
	status VARCHAR(11) DEFAULT 'PENDING' NOT NULL, 
	assigned_team_id INTEGER, 
	assigned_to_id INTEGER, 
	required_skills JSON, 
	estimated_hours NUMERIC(8, 2), 
	actual_hours NUMERIC(8, 2) DEFAULT 0 NOT NULL, 
	estimated_cost NUMERIC(15, 2), 
	actual_cost NUMERIC(15, 2) DEFAULT 0 NOT NULL, 
	scheduled_start TIMESTAMP WITHOUT TIME ZONE, 
	scheduled_end TIMESTAMP WITHOUT TIME ZONE, 
	actual_start TIMESTAMP WITHOUT TIME ZONE, 
	actual_end TIMESTAMP WITHOUT TIME ZONE, 
	customer_id INTEGER, 
	location VARCHAR(300), 
	equipment_needed TEXT, 
	tools_needed TEXT, 
	materials_needed JSON, 
	safety_requirements TEXT, 
	quality_standards TEXT, 
	completion_notes TEXT, 
	completion_photos JSON, 
	customer_satisfaction_rating INTEGER, 
	customer_feedback TEXT, 
	cost_center_id INTEGER, 
	project_id INTEGER, 
	service_request_id INTEGER, 
	parent_task_id INTEGER, 
	gl_batch_id INTEGER, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_task_rating_range CHECK (customer_satisfaction_rating >= 1 AND customer_satisfaction_rating <= 5), 
	FOREIGN KEY(assigned_team_id) REFERENCES engineering_teams (id), 
	FOREIGN KEY(assigned_to_id) REFERENCES employees (id), 
	FOREIGN KEY(customer_id) REFERENCES customers (id), 
	FOREIGN KEY(cost_center_id) REFERENCES cost_centers (id), 
	FOREIGN KEY(project_id) REFERENCES projects (id), 
	FOREIGN KEY(service_request_id) REFERENCES service_requests (id), 
	FOREIGN KEY(parent_task_id) REFERENCES engineering_tasks (id), 
	FOREIGN KEY(gl_batch_id) REFERENCES gl_batches (id)
);

CREATE UNIQUE INDEX ix_engineering_tasks_task_number ON engineering_tasks (task_number);

CREATE INDEX ix_engineering_tasks_project_id ON engineering_tasks (project_id);

CREATE INDEX ix_engineering_tasks_cost_center_id ON engineering_tasks (cost_center_id);

CREATE INDEX ix_engineering_tasks_customer_id ON engineering_tasks (customer_id);

CREATE INDEX ix_engineering_tasks_created_at ON engineering_tasks (created_at);

CREATE INDEX ix_eng_task_scheduled ON engineering_tasks (scheduled_start, scheduled_end);

CREATE INDEX ix_engineering_tasks_parent_task_id ON engineering_tasks (parent_task_id);

CREATE INDEX ix_eng_task_status ON engineering_tasks (status);

CREATE INDEX ix_engineering_tasks_assigned_to_id ON engineering_tasks (assigned_to_id);

CREATE INDEX ix_engineering_tasks_scheduled_end ON engineering_tasks (scheduled_end);

CREATE INDEX ix_engineering_tasks_service_request_id ON engineering_tasks (service_request_id);

CREATE INDEX ix_eng_task_priority ON engineering_tasks (priority);

CREATE INDEX ix_engineering_tasks_updated_at ON engineering_tasks (updated_at);

CREATE INDEX ix_eng_task_assigned ON engineering_tasks (assigned_to_id, status);

CREATE INDEX ix_engineering_tasks_scheduled_start ON engineering_tasks (scheduled_start);

CREATE INDEX ix_engineering_tasks_assigned_team_id ON engineering_tasks (assigned_team_id);

CREATE TABLE supplier_loan_settlements (
	id SERIAL NOT NULL, 
	loan_id INTEGER, 
	supplier_id INTEGER, 
	settled_price NUMERIC(12, 2) NOT NULL, 
	settlement_date TIMESTAMP WITHOUT TIME ZONE, 
	notes TEXT, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT chk_settlement_price_non_negative CHECK (settled_price >= 0), 
	FOREIGN KEY(loan_id) REFERENCES product_supplier_loans (id) ON DELETE CASCADE, 
	FOREIGN KEY(supplier_id) REFERENCES suppliers (id) ON DELETE SET NULL
);

CREATE INDEX ix_supplier_loan_settlements_updated_at ON supplier_loan_settlements (updated_at);

CREATE INDEX ix_supplier_loan_settlements_supplier_id ON supplier_loan_settlements (supplier_id);

CREATE INDEX ix_supplier_loan_settlements_created_at ON supplier_loan_settlements (created_at);

CREATE INDEX ix_supplier_loan_settlements_loan_id ON supplier_loan_settlements (loan_id);

CREATE TABLE sales (
	id SERIAL NOT NULL, 
	sale_number VARCHAR(50), 
	sale_date TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	customer_id INTEGER NOT NULL, 
	seller_id INTEGER NOT NULL, 
	seller_employee_id INTEGER, 
	preorder_id INTEGER, 
	tax_rate NUMERIC(5, 2) NOT NULL, 
	discount_total NUMERIC(12, 2) NOT NULL, 
	notes TEXT, 
	receiver_name VARCHAR(200), 
	status VARCHAR(9) NOT NULL, 
	payment_status VARCHAR(8) NOT NULL, 
	currency VARCHAR(10) NOT NULL, 
	fx_rate_used NUMERIC(10, 6), 
	fx_rate_source VARCHAR(20), 
	fx_rate_timestamp TIMESTAMP WITHOUT TIME ZONE, 
	fx_base_currency VARCHAR(10), 
	fx_quote_currency VARCHAR(10), 
	shipping_address TEXT, 
	billing_address TEXT, 
	shipping_cost NUMERIC(10, 2) NOT NULL, 
	total_amount NUMERIC(12, 2) NOT NULL, 
	total_paid NUMERIC(12, 2) NOT NULL, 
	balance_due NUMERIC(12, 2) NOT NULL, 
	refunded_total NUMERIC(12, 2) NOT NULL, 
	refund_of_id INTEGER, 
	idempotency_key VARCHAR(64), 
	cancelled_at TIMESTAMP WITHOUT TIME ZONE, 
	cancelled_by INTEGER, 
	cancel_reason VARCHAR(200), 
	is_archived BOOLEAN NOT NULL, 
	archived_at TIMESTAMP WITHOUT TIME ZONE, 
	archived_by INTEGER, 
	archive_reason VARCHAR(200), 
	cost_center_id INTEGER, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_sale_discount_non_negative CHECK (discount_total >= 0), 
	CONSTRAINT ck_sale_shipping_cost_non_negative CHECK (shipping_cost >= 0), 
	CONSTRAINT ck_sale_total_amount_non_negative CHECK (total_amount >= 0), 
	CONSTRAINT ck_sale_total_paid_non_negative CHECK (total_paid >= 0), 
	CONSTRAINT ck_sale_refunded_total_non_negative CHECK (refunded_total >= 0), 
	FOREIGN KEY(customer_id) REFERENCES customers (id), 
	FOREIGN KEY(seller_id) REFERENCES users (id), 
	FOREIGN KEY(seller_employee_id) REFERENCES employees (id) ON DELETE SET NULL, 
	FOREIGN KEY(preorder_id) REFERENCES preorders (id), 
	FOREIGN KEY(refund_of_id) REFERENCES sales (id) ON DELETE SET NULL, 
	FOREIGN KEY(cancelled_by) REFERENCES users (id), 
	FOREIGN KEY(archived_by) REFERENCES users (id), 
	FOREIGN KEY(cost_center_id) REFERENCES cost_centers (id)
);

CREATE INDEX ix_sales_cost_center_id ON sales (cost_center_id);

CREATE INDEX ix_sales_payment_status ON sales (payment_status);

CREATE INDEX ix_sales_cancelled_at ON sales (cancelled_at);

CREATE INDEX ix_sales_seller_employee_id ON sales (seller_employee_id);

CREATE INDEX ix_sales_sale_date ON sales (sale_date);

CREATE INDEX ix_sales_cancelled_by ON sales (cancelled_by);

CREATE INDEX ix_sales_created_at ON sales (created_at);

CREATE INDEX ix_sales_payment_status_date ON sales (payment_status, sale_date);

CREATE UNIQUE INDEX ix_sales_sale_number ON sales (sale_number);

CREATE INDEX ix_sales_preorder_id ON sales (preorder_id);

CREATE INDEX ix_sales_customer_status_date ON sales (customer_id, status, sale_date);

CREATE INDEX ix_sales_refund_of_id ON sales (refund_of_id);

CREATE INDEX ix_sales_updated_at ON sales (updated_at);

CREATE INDEX ix_sales_seller_date ON sales (seller_id, sale_date);

CREATE INDEX ix_sales_is_archived ON sales (is_archived);

CREATE INDEX ix_sales_archived ON sales (is_archived, archived_at);

CREATE INDEX ix_sales_status ON sales (status);

CREATE INDEX ix_sales_total_amount ON sales (total_amount);

CREATE INDEX ix_sales_archived_at ON sales (archived_at);

CREATE INDEX ix_sales_balance_due ON sales (balance_due);

CREATE INDEX ix_sales_archived_by ON sales (archived_by);

CREATE INDEX ix_sales_customer_id ON sales (customer_id);

CREATE INDEX ix_sales_seller_id ON sales (seller_id);

CREATE UNIQUE INDEX ix_sales_idempotency_key ON sales (idempotency_key);

CREATE TABLE product_rating_helpful (
	id SERIAL NOT NULL, 
	rating_id INTEGER NOT NULL, 
	customer_id INTEGER, 
	ip_address VARCHAR(45), 
	is_helpful BOOLEAN NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(rating_id) REFERENCES product_ratings (id), 
	FOREIGN KEY(customer_id) REFERENCES customers (id)
);

CREATE INDEX ix_rating_helpful_rating_id ON product_rating_helpful (rating_id);

CREATE INDEX ix_rating_helpful_customer_id ON product_rating_helpful (customer_id);

CREATE INDEX ix_rating_helpful_ip ON product_rating_helpful (ip_address);

CREATE INDEX ix_product_rating_helpful_updated_at ON product_rating_helpful (updated_at);

CREATE INDEX ix_product_rating_helpful_created_at ON product_rating_helpful (created_at);

CREATE TABLE resource_time_logs (
	id SERIAL NOT NULL, 
	project_id INTEGER NOT NULL, 
	task_id INTEGER, 
	resource_id INTEGER, 
	employee_id INTEGER NOT NULL, 
	log_date DATE NOT NULL, 
	hours_worked NUMERIC(8, 2) NOT NULL, 
	hourly_rate NUMERIC(10, 2) NOT NULL, 
	total_cost NUMERIC(12, 2) NOT NULL, 
	description TEXT, 
	approved BOOLEAN, 
	approved_by INTEGER, 
	approved_at TIMESTAMP WITHOUT TIME ZONE, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_hours_worked_range CHECK (hours_worked > 0 AND hours_worked <= 24), 
	CONSTRAINT ck_hourly_rate_ge_0 CHECK (hourly_rate >= 0), 
	FOREIGN KEY(project_id) REFERENCES projects (id) ON DELETE CASCADE, 
	FOREIGN KEY(task_id) REFERENCES project_tasks (id) ON DELETE CASCADE, 
	FOREIGN KEY(resource_id) REFERENCES project_resources (id) ON DELETE CASCADE, 
	FOREIGN KEY(employee_id) REFERENCES employees (id), 
	FOREIGN KEY(approved_by) REFERENCES users (id)
);

CREATE INDEX ix_resource_time_logs_approved ON resource_time_logs (approved);

CREATE INDEX ix_resource_time_logs_updated_at ON resource_time_logs (updated_at);

CREATE INDEX ix_resource_time_logs_log_date ON resource_time_logs (log_date);

CREATE INDEX ix_resource_time_logs_employee_id ON resource_time_logs (employee_id);

CREATE INDEX ix_time_log_project_date ON resource_time_logs (project_id, log_date);

CREATE INDEX ix_resource_time_logs_resource_id ON resource_time_logs (resource_id);

CREATE INDEX ix_resource_time_logs_created_at ON resource_time_logs (created_at);

CREATE INDEX ix_resource_time_logs_project_id ON resource_time_logs (project_id);

CREATE INDEX ix_resource_time_logs_approved_by ON resource_time_logs (approved_by);

CREATE INDEX ix_time_log_employee_date ON resource_time_logs (employee_id, log_date);

CREATE INDEX ix_resource_time_logs_task_id ON resource_time_logs (task_id);

CREATE TABLE engineering_timesheets (
	id SERIAL NOT NULL, 
	employee_id INTEGER NOT NULL, 
	task_id INTEGER, 
	work_date DATE NOT NULL, 
	start_time TIME WITHOUT TIME ZONE NOT NULL, 
	end_time TIME WITHOUT TIME ZONE NOT NULL, 
	break_duration_minutes INTEGER DEFAULT 0 NOT NULL, 
	actual_work_hours NUMERIC(5, 2) NOT NULL, 
	billable_hours NUMERIC(5, 2), 
	hourly_rate NUMERIC(10, 2), 
	total_cost NUMERIC(15, 2), 
	productivity_rating VARCHAR(9), 
	work_description TEXT, 
	issues_encountered TEXT, 
	materials_used JSON, 
	location VARCHAR(300), 
	status VARCHAR(9) DEFAULT 'DRAFT' NOT NULL, 
	approved_by INTEGER, 
	approval_date TIMESTAMP WITHOUT TIME ZONE, 
	approval_notes TEXT, 
	cost_center_id INTEGER, 
	gl_batch_id INTEGER, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_timesheet_hours_positive CHECK (actual_work_hours > 0), 
	CONSTRAINT ck_timesheet_break_positive CHECK (break_duration_minutes >= 0), 
	FOREIGN KEY(employee_id) REFERENCES employees (id) ON DELETE CASCADE, 
	FOREIGN KEY(task_id) REFERENCES engineering_tasks (id), 
	FOREIGN KEY(approved_by) REFERENCES users (id), 
	FOREIGN KEY(cost_center_id) REFERENCES cost_centers (id), 
	FOREIGN KEY(gl_batch_id) REFERENCES gl_batches (id)
);

CREATE INDEX ix_timesheet_task ON engineering_timesheets (task_id);

CREATE INDEX ix_engineering_timesheets_employee_id ON engineering_timesheets (employee_id);

CREATE INDEX ix_timesheet_employee_date ON engineering_timesheets (employee_id, work_date);

CREATE INDEX ix_engineering_timesheets_work_date ON engineering_timesheets (work_date);

CREATE INDEX ix_engineering_timesheets_updated_at ON engineering_timesheets (updated_at);

CREATE INDEX ix_timesheet_status ON engineering_timesheets (status);

CREATE INDEX ix_engineering_timesheets_cost_center_id ON engineering_timesheets (cost_center_id);

CREATE INDEX ix_engineering_timesheets_created_at ON engineering_timesheets (created_at);

CREATE TABLE sale_lines (
	id SERIAL NOT NULL, 
	sale_id INTEGER NOT NULL, 
	product_id INTEGER NOT NULL, 
	warehouse_id INTEGER NOT NULL, 
	quantity INTEGER NOT NULL, 
	unit_price NUMERIC(12, 2) NOT NULL, 
	discount_rate NUMERIC(5, 2) NOT NULL, 
	tax_rate NUMERIC(5, 2) NOT NULL, 
	line_receiver VARCHAR(200), 
	note VARCHAR(200), 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT chk_sale_line_qty_positive CHECK (quantity > 0), 
	CONSTRAINT chk_sale_line_unit_price_non_negative CHECK (unit_price >= 0), 
	CONSTRAINT chk_sale_line_discount_rate_range CHECK (discount_rate >= 0 AND discount_rate <= 100), 
	CONSTRAINT chk_sale_line_tax_rate_range CHECK (tax_rate >= 0 AND tax_rate <= 100), 
	FOREIGN KEY(sale_id) REFERENCES sales (id), 
	FOREIGN KEY(product_id) REFERENCES products (id), 
	FOREIGN KEY(warehouse_id) REFERENCES warehouses (id)
);

CREATE INDEX ix_sale_line_sale ON sale_lines (sale_id);

CREATE INDEX ix_sale_lines_product_id ON sale_lines (product_id);

CREATE INDEX ix_sale_lines_updated_at ON sale_lines (updated_at);

CREATE INDEX ix_sale_lines_created_at ON sale_lines (created_at);

CREATE INDEX ix_sale_lines_warehouse_id ON sale_lines (warehouse_id);

CREATE TABLE invoices (
	id SERIAL NOT NULL, 
	invoice_number VARCHAR(50) NOT NULL, 
	invoice_date TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	due_date TIMESTAMP WITHOUT TIME ZONE, 
	customer_id INTEGER NOT NULL, 
	supplier_id INTEGER, 
	partner_id INTEGER, 
	sale_id INTEGER, 
	service_id INTEGER, 
	preorder_id INTEGER, 
	source VARCHAR(8) NOT NULL, 
	kind VARCHAR(11) NOT NULL, 
	credit_for_id INTEGER, 
	refund_of_id INTEGER, 
	currency VARCHAR(10) NOT NULL, 
	fx_rate_used NUMERIC(10, 6), 
	fx_rate_source VARCHAR(20), 
	fx_rate_timestamp TIMESTAMP WITHOUT TIME ZONE, 
	fx_base_currency VARCHAR(10), 
	fx_quote_currency VARCHAR(10), 
	total_amount NUMERIC(12, 2) NOT NULL, 
	tax_amount NUMERIC(12, 2) NOT NULL, 
	discount_amount NUMERIC(12, 2) NOT NULL, 
	notes TEXT, 
	terms TEXT, 
	refunded_total NUMERIC(12, 2) NOT NULL, 
	idempotency_key VARCHAR(64), 
	cancelled_at TIMESTAMP WITHOUT TIME ZONE, 
	cancelled_by INTEGER, 
	cancel_reason VARCHAR(200), 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(customer_id) REFERENCES customers (id), 
	FOREIGN KEY(supplier_id) REFERENCES suppliers (id), 
	FOREIGN KEY(partner_id) REFERENCES partners (id), 
	FOREIGN KEY(sale_id) REFERENCES sales (id), 
	FOREIGN KEY(service_id) REFERENCES service_requests (id), 
	FOREIGN KEY(preorder_id) REFERENCES preorders (id), 
	FOREIGN KEY(credit_for_id) REFERENCES invoices (id) ON DELETE SET NULL, 
	FOREIGN KEY(refund_of_id) REFERENCES invoices (id) ON DELETE SET NULL, 
	FOREIGN KEY(cancelled_by) REFERENCES users (id)
);

CREATE UNIQUE INDEX ix_invoices_invoice_number ON invoices (invoice_number);

CREATE INDEX ix_invoices_updated_at ON invoices (updated_at);

CREATE INDEX ix_invoices_sale_id ON invoices (sale_id);

CREATE INDEX ix_invoices_refund_of_id ON invoices (refund_of_id);

CREATE INDEX ix_inv_customer_date ON invoices (customer_id, invoice_date);

CREATE INDEX ix_invoices_due_date ON invoices (due_date);

CREATE INDEX ix_invoices_kind ON invoices (kind);

CREATE INDEX ix_inv_kind_date ON invoices (kind, invoice_date);

CREATE INDEX ix_invoices_service_id ON invoices (service_id);

CREATE UNIQUE INDEX ix_invoices_idempotency_key ON invoices (idempotency_key);

CREATE INDEX ix_inv_cust_cancelled ON invoices (customer_id, cancelled_at);

CREATE INDEX ix_invoices_customer_id ON invoices (customer_id);

CREATE INDEX ix_inv_total_amount ON invoices (total_amount);

CREATE INDEX ix_invoices_cancelled_at ON invoices (cancelled_at);

CREATE INDEX ix_invoices_preorder_id ON invoices (preorder_id);

CREATE INDEX ix_invoices_credit_for_id ON invoices (credit_for_id);

CREATE INDEX ix_invoices_supplier_id ON invoices (supplier_id);

CREATE INDEX ix_invoices_cancelled_by ON invoices (cancelled_by);

CREATE INDEX ix_invoices_invoice_date ON invoices (invoice_date);

CREATE INDEX ix_invoices_source ON invoices (source);

CREATE INDEX ix_invoices_partner_id ON invoices (partner_id);

CREATE INDEX ix_invoices_created_at ON invoices (created_at);

CREATE TABLE shipments (
	id SERIAL NOT NULL, 
	number VARCHAR(50), 
	shipment_number VARCHAR(50), 
	date TIMESTAMP WITHOUT TIME ZONE, 
	shipment_date TIMESTAMP WITHOUT TIME ZONE, 
	expected_arrival TIMESTAMP WITHOUT TIME ZONE, 
	actual_arrival TIMESTAMP WITHOUT TIME ZONE, 
	delivered_date TIMESTAMP WITHOUT TIME ZONE, 
	origin VARCHAR(100), 
	destination VARCHAR(100), 
	destination_id INTEGER, 
	status VARCHAR(20) DEFAULT 'DRAFT' NOT NULL, 
	value_before NUMERIC(12, 2), 
	shipping_cost NUMERIC(12, 2), 
	customs NUMERIC(12, 2), 
	vat NUMERIC(12, 2), 
	insurance NUMERIC(12, 2), 
	total_cost NUMERIC(12, 2), 
	carrier VARCHAR(100), 
	tracking_number VARCHAR(100), 
	notes TEXT, 
	currency VARCHAR(10) NOT NULL, 
	fx_rate_used NUMERIC(10, 6), 
	fx_rate_source VARCHAR(20), 
	fx_rate_timestamp TIMESTAMP WITHOUT TIME ZONE, 
	fx_base_currency VARCHAR(10), 
	fx_quote_currency VARCHAR(10), 
	sale_id INTEGER, 
	weight NUMERIC(10, 3), 
	dimensions VARCHAR(100), 
	package_count INTEGER, 
	priority VARCHAR(20), 
	delivery_method VARCHAR(50), 
	delivery_instructions TEXT, 
	customs_declaration VARCHAR(100), 
	customs_cleared_date TIMESTAMP WITHOUT TIME ZONE, 
	delivery_attempts INTEGER, 
	last_delivery_attempt TIMESTAMP WITHOUT TIME ZONE, 
	return_reason TEXT, 
	is_archived BOOLEAN NOT NULL, 
	archived_at TIMESTAMP WITHOUT TIME ZONE, 
	archived_by INTEGER, 
	archive_reason VARCHAR(200), 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT chk_shipment_status_allowed CHECK (status IN ('DRAFT','PENDING','IN_TRANSIT','IN_CUSTOMS','ARRIVED','DELIVERED','CANCELLED','RETURNED','CREATED')), 
	CONSTRAINT ck_shipment_value_before_non_negative CHECK (value_before >= 0), 
	CONSTRAINT ck_shipment_shipping_cost_non_negative CHECK (shipping_cost >= 0), 
	CONSTRAINT ck_shipment_customs_non_negative CHECK (customs >= 0), 
	CONSTRAINT ck_shipment_vat_non_negative CHECK (vat >= 0), 
	CONSTRAINT ck_shipment_insurance_non_negative CHECK (insurance >= 0), 
	FOREIGN KEY(destination_id) REFERENCES warehouses (id) ON DELETE SET NULL, 
	FOREIGN KEY(sale_id) REFERENCES sales (id), 
	FOREIGN KEY(archived_by) REFERENCES users (id)
);

CREATE INDEX ix_shipments_shipment_date ON shipments (shipment_date);

CREATE INDEX ix_shipments_archived_by ON shipments (archived_by);

CREATE UNIQUE INDEX ix_shipments_number ON shipments (number);

CREATE INDEX ix_shipments_tracking_number ON shipments (tracking_number);

CREATE INDEX ix_shipments_date ON shipments (date);

CREATE INDEX ix_shipments_archived_at ON shipments (archived_at);

CREATE INDEX ix_shipments_dest_status ON shipments (destination_id, status);

CREATE UNIQUE INDEX ix_shipments_shipment_number ON shipments (shipment_number);

CREATE INDEX ix_shipments_status ON shipments (status);

CREATE INDEX ix_shipments_updated_at ON shipments (updated_at);

CREATE INDEX ix_shipments_destination_id ON shipments (destination_id);

CREATE INDEX ix_shipments_is_archived ON shipments (is_archived);

CREATE INDEX ix_shipments_sale_id ON shipments (sale_id);

CREATE INDEX ix_shipments_created_at ON shipments (created_at);

CREATE TABLE sale_returns (
	id SERIAL NOT NULL, 
	sale_id INTEGER, 
	customer_id INTEGER, 
	warehouse_id INTEGER, 
	reason VARCHAR(200), 
	status VARCHAR(9) NOT NULL, 
	notes TEXT, 
	total_amount NUMERIC(12, 2) NOT NULL, 
	tax_rate NUMERIC(5, 2), 
	tax_amount NUMERIC(12, 2), 
	currency VARCHAR(10) NOT NULL, 
	fx_rate_used NUMERIC(10, 6), 
	fx_rate_source VARCHAR(20), 
	fx_rate_timestamp TIMESTAMP WITHOUT TIME ZONE, 
	fx_base_currency VARCHAR(10), 
	fx_quote_currency VARCHAR(10), 
	credit_note_id INTEGER, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_sale_return_tax_rate_0_100 CHECK (tax_rate >= 0 AND tax_rate <= 100), 
	CONSTRAINT ck_sale_return_tax_non_negative CHECK (tax_amount >= 0), 
	FOREIGN KEY(sale_id) REFERENCES sales (id) ON DELETE SET NULL, 
	FOREIGN KEY(customer_id) REFERENCES customers (id) ON DELETE SET NULL, 
	FOREIGN KEY(warehouse_id) REFERENCES warehouses (id) ON DELETE SET NULL, 
	FOREIGN KEY(credit_note_id) REFERENCES invoices (id) ON DELETE SET NULL
);

CREATE INDEX ix_sale_returns_credit_note_id ON sale_returns (credit_note_id);

CREATE INDEX ix_sale_returns_status ON sale_returns (status);

CREATE INDEX ix_sale_returns_warehouse_id ON sale_returns (warehouse_id);

CREATE INDEX ix_sale_returns_updated_at ON sale_returns (updated_at);

CREATE INDEX ix_sale_returns_sale_id ON sale_returns (sale_id);

CREATE INDEX ix_sale_returns_customer_id ON sale_returns (customer_id);

CREATE INDEX ix_sale_returns_created_at ON sale_returns (created_at);

CREATE TABLE invoice_lines (
	id SERIAL NOT NULL, 
	invoice_id INTEGER NOT NULL, 
	description VARCHAR(200) NOT NULL, 
	quantity FLOAT NOT NULL, 
	unit_price NUMERIC(12, 2) NOT NULL, 
	tax_rate NUMERIC(5, 2) NOT NULL, 
	discount NUMERIC(5, 2) NOT NULL, 
	product_id INTEGER, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_invoice_line_quantity_non_negative CHECK (quantity >= 0), 
	CONSTRAINT ck_invoice_line_unit_price_non_negative CHECK (unit_price >= 0), 
	CONSTRAINT ck_invoice_line_tax_rate_range CHECK (tax_rate >= 0 AND tax_rate <= 100), 
	CONSTRAINT ck_invoice_line_discount_range CHECK (discount >= 0 AND discount <= 100), 
	FOREIGN KEY(invoice_id) REFERENCES invoices (id), 
	FOREIGN KEY(product_id) REFERENCES products (id)
);

CREATE INDEX ix_invoice_lines_product_id ON invoice_lines (product_id);

CREATE INDEX ix_invoice_lines_invoice_id ON invoice_lines (invoice_id);

CREATE TABLE shipment_items (
	id SERIAL NOT NULL, 
	shipment_id INTEGER NOT NULL, 
	product_id INTEGER NOT NULL, 
	warehouse_id INTEGER, 
	quantity INTEGER NOT NULL, 
	unit_cost NUMERIC(12, 2) NOT NULL, 
	declared_value NUMERIC(12, 2), 
	landed_extra_share NUMERIC(12, 2), 
	landed_unit_cost NUMERIC(12, 2), 
	notes VARCHAR(200), 
	PRIMARY KEY (id), 
	CONSTRAINT chk_shipment_item_qty_positive CHECK (quantity > 0), 
	CONSTRAINT uq_shipment_item_unique UNIQUE (shipment_id, product_id, warehouse_id), 
	CONSTRAINT ck_shipment_item_unit_cost_non_negative CHECK (unit_cost >= 0), 
	CONSTRAINT ck_shipment_item_declared_value_non_negative CHECK (declared_value >= 0), 
	CONSTRAINT ck_shipment_item_landed_extra_share_non_negative CHECK (landed_extra_share >= 0), 
	CONSTRAINT ck_shipment_item_landed_unit_cost_non_negative CHECK (landed_unit_cost >= 0), 
	FOREIGN KEY(shipment_id) REFERENCES shipments (id) ON DELETE CASCADE, 
	FOREIGN KEY(product_id) REFERENCES products (id), 
	FOREIGN KEY(warehouse_id) REFERENCES warehouses (id) ON DELETE SET NULL
);

CREATE INDEX ix_shipment_items_product_id ON shipment_items (product_id);

CREATE INDEX ix_shipment_items_prod_wh ON shipment_items (product_id, warehouse_id);

CREATE INDEX ix_shipment_items_shipment_id ON shipment_items (shipment_id);

CREATE INDEX ix_shipment_items_warehouse_id ON shipment_items (warehouse_id);

CREATE TABLE shipment_partners (
	id SERIAL NOT NULL, 
	shipment_id INTEGER NOT NULL, 
	partner_id INTEGER NOT NULL, 
	identity_number VARCHAR(100), 
	phone_number VARCHAR(20), 
	address VARCHAR(200), 
	unit_price_before_tax NUMERIC(12, 2), 
	expiry_date DATE, 
	share_percentage NUMERIC(5, 2), 
	share_amount NUMERIC(12, 2), 
	notes TEXT, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT chk_shipment_partner_share CHECK (share_percentage >= 0 AND share_percentage <= 100), 
	CONSTRAINT uq_shipment_partner_unique UNIQUE (shipment_id, partner_id), 
	CONSTRAINT ck_shipment_partner_unit_price_non_negative CHECK (unit_price_before_tax >= 0), 
	CONSTRAINT ck_shipment_partner_share_amount_non_negative CHECK (share_amount >= 0), 
	FOREIGN KEY(shipment_id) REFERENCES shipments (id) ON DELETE CASCADE, 
	FOREIGN KEY(partner_id) REFERENCES partners (id) ON DELETE CASCADE
);

CREATE INDEX ix_shipment_partner_pair ON shipment_partners (shipment_id, partner_id);

CREATE INDEX ix_shipment_partners_partner_id ON shipment_partners (partner_id);

CREATE INDEX ix_shipment_partners_updated_at ON shipment_partners (updated_at);

CREATE INDEX ix_shipment_partners_created_at ON shipment_partners (created_at);

CREATE INDEX ix_shipment_partners_shipment_id ON shipment_partners (shipment_id);

CREATE TABLE expenses (
	id SERIAL NOT NULL, 
	date TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	amount NUMERIC(12, 2) NOT NULL, 
	currency VARCHAR(10) NOT NULL, 
	fx_rate_used NUMERIC(10, 6), 
	fx_rate_source VARCHAR(20), 
	fx_rate_timestamp TIMESTAMP WITHOUT TIME ZONE, 
	fx_base_currency VARCHAR(10), 
	fx_quote_currency VARCHAR(10), 
	type_id INTEGER NOT NULL, 
	branch_id INTEGER NOT NULL, 
	site_id INTEGER, 
	employee_id INTEGER, 
	customer_id INTEGER, 
	warehouse_id INTEGER, 
	partner_id INTEGER, 
	supplier_id INTEGER, 
	shipment_id INTEGER, 
	utility_account_id INTEGER, 
	stock_adjustment_id INTEGER, 
	payee_type VARCHAR(20) NOT NULL, 
	payee_entity_id INTEGER, 
	payee_name VARCHAR(200), 
	beneficiary_name VARCHAR(200), 
	paid_to VARCHAR(200), 
	disbursed_by VARCHAR(200), 
	period_start DATE, 
	period_end DATE, 
	payment_method VARCHAR(20) NOT NULL, 
	payment_details TEXT, 
	description VARCHAR(200), 
	notes TEXT, 
	tax_invoice_number VARCHAR(100), 
	check_number VARCHAR(100), 
	check_bank VARCHAR(100), 
	check_due_date DATE, 
	check_payee VARCHAR(200), 
	bank_transfer_ref VARCHAR(100), 
	bank_name VARCHAR(100), 
	account_number VARCHAR(100), 
	account_holder VARCHAR(200), 
	card_number VARCHAR(8), 
	card_holder VARCHAR(120), 
	card_expiry VARCHAR(10), 
	online_gateway VARCHAR(50), 
	online_ref VARCHAR(100), 
	telecom_phone_number VARCHAR(30), 
	telecom_service_type VARCHAR(20), 
	insurance_company_name VARCHAR(200), 
	insurance_company_address VARCHAR(200), 
	insurance_company_phone VARCHAR(30), 
	marketing_company_name VARCHAR(200), 
	marketing_company_address VARCHAR(200), 
	marketing_coverage_details VARCHAR(200), 
	bank_fee_bank_name VARCHAR(200), 
	bank_fee_notes TEXT, 
	gov_fee_entity_name VARCHAR(200), 
	gov_fee_entity_address VARCHAR(200), 
	gov_fee_notes TEXT, 
	port_fee_port_name VARCHAR(200), 
	port_fee_notes TEXT, 
	travel_destination VARCHAR(200), 
	travel_reason VARCHAR(200), 
	travel_notes TEXT, 
	shipping_company_name VARCHAR(200), 
	shipping_notes TEXT, 
	maintenance_provider_name VARCHAR(200), 
	maintenance_provider_address VARCHAR(200), 
	maintenance_notes TEXT, 
	rent_property_address VARCHAR(200), 
	rent_property_notes TEXT, 
	tech_provider_name VARCHAR(200), 
	tech_provider_phone VARCHAR(30), 
	tech_provider_address VARCHAR(200), 
	tech_subscription_id VARCHAR(100), 
	storage_property_address VARCHAR(200), 
	storage_expected_days INTEGER, 
	storage_start_date DATE, 
	storage_notes TEXT, 
	customs_arrival_date DATE, 
	customs_departure_date DATE, 
	customs_origin VARCHAR(200), 
	customs_port_name VARCHAR(200), 
	customs_notes TEXT, 
	training_company_name VARCHAR(200), 
	training_location VARCHAR(200), 
	training_duration_days INTEGER, 
	training_participants_count INTEGER, 
	training_notes TEXT, 
	training_participants_names TEXT, 
	training_topics TEXT, 
	entertainment_duration_days INTEGER, 
	entertainment_notes TEXT, 
	bank_fee_reference VARCHAR(100), 
	bank_fee_contact_name VARCHAR(200), 
	bank_fee_contact_phone VARCHAR(30), 
	gov_fee_reference VARCHAR(100), 
	port_fee_reference VARCHAR(100), 
	port_fee_agent_name VARCHAR(200), 
	port_fee_agent_phone VARCHAR(30), 
	salary_notes TEXT, 
	salary_reference VARCHAR(100), 
	travel_duration_days INTEGER, 
	travel_start_date DATE, 
	travel_companions TEXT, 
	travel_cost_center VARCHAR(100), 
	employee_advance_period VARCHAR(100), 
	employee_advance_reason VARCHAR(200), 
	employee_advance_notes TEXT, 
	shipping_date DATE, 
	shipping_reference VARCHAR(100), 
	shipping_mode VARCHAR(50), 
	shipping_tracking_number VARCHAR(100), 
	maintenance_details TEXT, 
	maintenance_completion_date DATE, 
	maintenance_technician_name VARCHAR(200), 
	import_tax_reference VARCHAR(100), 
	import_tax_notes TEXT, 
	hospitality_type VARCHAR(20), 
	hospitality_notes TEXT, 
	hospitality_attendees TEXT, 
	hospitality_location VARCHAR(200), 
	telecom_notes TEXT, 
	office_supplier_name VARCHAR(200), 
	office_notes TEXT, 
	office_items_list TEXT, 
	office_purchase_reference VARCHAR(100), 
	home_relation_to_company VARCHAR(100), 
	home_address VARCHAR(200), 
	home_owner_name VARCHAR(200), 
	home_notes TEXT, 
	home_cost_share NUMERIC(12, 2), 
	partner_expense_reason VARCHAR(200), 
	partner_expense_notes TEXT, 
	partner_expense_reference VARCHAR(100), 
	supplier_expense_reason VARCHAR(200), 
	supplier_expense_notes TEXT, 
	supplier_expense_reference VARCHAR(100), 
	handling_notes TEXT, 
	handling_quantity NUMERIC(12, 2), 
	handling_unit VARCHAR(50), 
	handling_reference VARCHAR(100), 
	fuel_vehicle_number VARCHAR(50), 
	fuel_driver_name VARCHAR(100), 
	fuel_usage_type VARCHAR(20), 
	fuel_volume NUMERIC(12, 3), 
	fuel_notes TEXT, 
	fuel_station_name VARCHAR(200), 
	fuel_odometer_start INTEGER, 
	fuel_odometer_end INTEGER, 
	transport_beneficiary_name VARCHAR(200), 
	transport_reason VARCHAR(200), 
	transport_usage_type VARCHAR(20), 
	transport_notes TEXT, 
	transport_route_details TEXT, 
	insurance_policy_number VARCHAR(100), 
	insurance_notes TEXT, 
	legal_company_name VARCHAR(200), 
	legal_company_address VARCHAR(200), 
	legal_case_notes TEXT, 
	legal_case_number VARCHAR(100), 
	legal_case_type VARCHAR(100), 
	is_archived BOOLEAN NOT NULL, 
	archived_at TIMESTAMP WITHOUT TIME ZONE, 
	archived_by INTEGER, 
	archive_reason VARCHAR(200), 
	cost_center_id INTEGER, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT chk_expense_amount_non_negative CHECK (amount >= 0), 
	CONSTRAINT chk_expense_payment_method_allowed CHECK (payment_method IN ('cash','cheque','bank','card','online','other')), 
	CONSTRAINT ck_expense_payee_type_allowed CHECK (payee_type IN ('EMPLOYEE','SUPPLIER','CUSTOMER','PARTNER','WAREHOUSE','SHIPMENT','UTILITY','OTHER')), 
	CONSTRAINT uq_expenses_stock_adjustment_id UNIQUE (stock_adjustment_id), 
	FOREIGN KEY(type_id) REFERENCES expense_types (id) ON DELETE RESTRICT, 
	FOREIGN KEY(branch_id) REFERENCES branches (id), 
	FOREIGN KEY(site_id) REFERENCES sites (id), 
	FOREIGN KEY(employee_id) REFERENCES employees (id) ON DELETE SET NULL, 
	FOREIGN KEY(customer_id) REFERENCES customers (id) ON DELETE SET NULL, 
	FOREIGN KEY(warehouse_id) REFERENCES warehouses (id) ON DELETE SET NULL, 
	FOREIGN KEY(partner_id) REFERENCES partners (id) ON DELETE SET NULL, 
	FOREIGN KEY(supplier_id) REFERENCES suppliers (id) ON DELETE SET NULL, 
	FOREIGN KEY(shipment_id) REFERENCES shipments (id) ON DELETE SET NULL, 
	FOREIGN KEY(utility_account_id) REFERENCES utility_accounts (id) ON DELETE SET NULL, 
	FOREIGN KEY(stock_adjustment_id) REFERENCES stock_adjustments (id) ON DELETE SET NULL, 
	FOREIGN KEY(archived_by) REFERENCES users (id), 
	FOREIGN KEY(cost_center_id) REFERENCES cost_centers (id)
);

CREATE INDEX ix_expenses_date ON expenses (date);

CREATE INDEX ix_expenses_shipment_id ON expenses (shipment_id);

CREATE INDEX ix_expenses_payee_name ON expenses (payee_name);

CREATE INDEX ix_expense_type_date ON expenses (type_id, date);

CREATE INDEX ix_expenses_customer_id ON expenses (customer_id);

CREATE INDEX ix_expense_supplier_date ON expenses (supplier_id, date);

CREATE INDEX ix_expenses_archived_by ON expenses (archived_by);

CREATE INDEX ix_expenses_paid_to ON expenses (paid_to);

CREATE INDEX ix_expense_shipment_date ON expenses (shipment_id, date);

CREATE INDEX ix_expenses_utility_account_id ON expenses (utility_account_id);

CREATE INDEX ix_expense_customer_date ON expenses (customer_id, date);

CREATE INDEX ix_expenses_warehouse_id ON expenses (warehouse_id);

CREATE INDEX ix_expenses_period_start ON expenses (period_start);

CREATE INDEX ix_expense_payee_type_entity_date ON expenses (payee_type, payee_entity_id, date);

CREATE INDEX ix_expenses_cost_center_id ON expenses (cost_center_id);

CREATE INDEX ix_expenses_branch_id ON expenses (branch_id);

CREATE INDEX ix_expense_amount ON expenses (amount);

CREATE INDEX ix_expenses_stock_adjustment_id ON expenses (stock_adjustment_id);

CREATE INDEX ix_expenses_period_end ON expenses (period_end);

CREATE INDEX ix_expenses_partner_id ON expenses (partner_id);

CREATE INDEX ix_expenses_created_at ON expenses (created_at);

CREATE INDEX ix_expenses_site_id ON expenses (site_id);

CREATE INDEX ix_expenses_tax_invoice_number ON expenses (tax_invoice_number);

CREATE INDEX ix_expenses_payee_type ON expenses (payee_type);

CREATE INDEX ix_expenses_updated_at ON expenses (updated_at);

CREATE INDEX ix_expenses_supplier_id ON expenses (supplier_id);

CREATE INDEX ix_expenses_is_archived ON expenses (is_archived);

CREATE INDEX ix_expenses_type_id ON expenses (type_id);

CREATE INDEX ix_expenses_employee_id ON expenses (employee_id);

CREATE INDEX ix_expenses_payee_entity_id ON expenses (payee_entity_id);

CREATE INDEX ix_expense_partner_date ON expenses (partner_id, date);

CREATE INDEX ix_expenses_archived_at ON expenses (archived_at);

CREATE TABLE recurring_invoice_schedules (
	id SERIAL NOT NULL, 
	template_id INTEGER NOT NULL, 
	invoice_id INTEGER, 
	scheduled_date DATE NOT NULL, 
	generated_at TIMESTAMP WITHOUT TIME ZONE, 
	status VARCHAR(20) NOT NULL, 
	error_message TEXT, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_schedule_status CHECK (status IN ('PENDING','GENERATED','FAILED','SKIPPED')), 
	FOREIGN KEY(template_id) REFERENCES recurring_invoice_templates (id) ON DELETE CASCADE, 
	FOREIGN KEY(invoice_id) REFERENCES invoices (id)
);

CREATE INDEX ix_recurring_invoice_schedules_template_id ON recurring_invoice_schedules (template_id);

CREATE INDEX ix_recurring_invoice_schedules_updated_at ON recurring_invoice_schedules (updated_at);

CREATE INDEX ix_recurring_invoice_schedules_scheduled_date ON recurring_invoice_schedules (scheduled_date);

CREATE INDEX ix_recurring_invoice_schedules_invoice_id ON recurring_invoice_schedules (invoice_id);

CREATE INDEX ix_recurring_invoice_schedules_created_at ON recurring_invoice_schedules (created_at);

CREATE INDEX ix_recurring_invoice_schedules_status ON recurring_invoice_schedules (status);

CREATE TABLE project_milestones (
	id SERIAL NOT NULL, 
	project_id INTEGER NOT NULL, 
	phase_id INTEGER, 
	milestone_number VARCHAR(50) NOT NULL, 
	name VARCHAR(300) NOT NULL, 
	description TEXT, 
	due_date DATE NOT NULL, 
	completed_date DATE, 
	billing_amount NUMERIC(15, 2), 
	tax_rate NUMERIC(5, 2), 
	tax_amount NUMERIC(12, 2), 
	billing_percentage NUMERIC(5, 2), 
	invoice_id INTEGER, 
	payment_terms_days INTEGER, 
	status VARCHAR(11) NOT NULL, 
	completion_criteria TEXT, 
	deliverables JSON, 
	approval_required BOOLEAN, 
	approved_by INTEGER, 
	approved_at TIMESTAMP WITHOUT TIME ZONE, 
	notes TEXT, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_milestone_billing_ge_0 CHECK (billing_amount >= 0), 
	CONSTRAINT ck_milestone_tax_rate_0_100 CHECK (tax_rate >= 0 AND tax_rate <= 100), 
	CONSTRAINT ck_milestone_tax_non_negative CHECK (tax_amount >= 0), 
	CONSTRAINT ck_milestone_billing_pct CHECK (billing_percentage >= 0 AND billing_percentage <= 100), 
	FOREIGN KEY(project_id) REFERENCES projects (id) ON DELETE CASCADE, 
	FOREIGN KEY(phase_id) REFERENCES project_phases (id) ON DELETE SET NULL, 
	FOREIGN KEY(invoice_id) REFERENCES invoices (id), 
	FOREIGN KEY(approved_by) REFERENCES users (id)
);

CREATE INDEX ix_project_milestones_approved_at ON project_milestones (approved_at);

CREATE INDEX ix_project_milestones_phase_id ON project_milestones (phase_id);

CREATE INDEX ix_project_milestones_updated_at ON project_milestones (updated_at);

CREATE INDEX ix_project_milestones_due_date ON project_milestones (due_date);

CREATE INDEX ix_project_milestones_approved_by ON project_milestones (approved_by);

CREATE INDEX ix_project_milestones_status ON project_milestones (status);

CREATE INDEX ix_project_milestones_invoice_id ON project_milestones (invoice_id);

CREATE INDEX ix_project_milestones_created_at ON project_milestones (created_at);

CREATE INDEX ix_project_milestones_milestone_number ON project_milestones (milestone_number);

CREATE INDEX ix_milestone_project_status ON project_milestones (project_id, status);

CREATE INDEX ix_project_milestones_project_id ON project_milestones (project_id);

CREATE INDEX ix_project_milestones_completed_date ON project_milestones (completed_date);

CREATE TABLE employee_deductions (
	id SERIAL NOT NULL, 
	employee_id INTEGER NOT NULL, 
	deduction_type VARCHAR(50) NOT NULL, 
	amount NUMERIC(12, 2) NOT NULL, 
	currency VARCHAR(10) NOT NULL, 
	start_date DATE NOT NULL, 
	end_date DATE, 
	is_active BOOLEAN NOT NULL, 
	notes TEXT, 
	expense_id INTEGER, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(employee_id) REFERENCES employees (id), 
	FOREIGN KEY(expense_id) REFERENCES expenses (id)
);

CREATE INDEX ix_employee_deductions_deduction_type ON employee_deductions (deduction_type);

CREATE INDEX ix_employee_deductions_created_at ON employee_deductions (created_at);

CREATE INDEX ix_employee_deductions_expense_id ON employee_deductions (expense_id);

CREATE INDEX ix_employee_deductions_start_date ON employee_deductions (start_date);

CREATE INDEX ix_employee_deductions_is_active ON employee_deductions (is_active);

CREATE INDEX ix_employee_deductions_employee_id ON employee_deductions (employee_id);

CREATE INDEX ix_employee_deductions_updated_at ON employee_deductions (updated_at);

CREATE INDEX ix_employee_deductions_end_date ON employee_deductions (end_date);

CREATE TABLE employee_advances (
	id SERIAL NOT NULL, 
	employee_id INTEGER NOT NULL, 
	amount NUMERIC(12, 2) NOT NULL, 
	currency VARCHAR(10) NOT NULL, 
	advance_date DATE NOT NULL, 
	reason TEXT, 
	total_installments INTEGER NOT NULL, 
	installments_paid INTEGER NOT NULL, 
	fully_paid BOOLEAN NOT NULL, 
	notes TEXT, 
	expense_id INTEGER, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(employee_id) REFERENCES employees (id), 
	FOREIGN KEY(expense_id) REFERENCES expenses (id)
);

CREATE INDEX ix_employee_advances_fully_paid ON employee_advances (fully_paid);

CREATE INDEX ix_employee_advances_updated_at ON employee_advances (updated_at);

CREATE INDEX ix_employee_advances_employee_id ON employee_advances (employee_id);

CREATE INDEX ix_employee_advances_created_at ON employee_advances (created_at);

CREATE INDEX ix_employee_advances_expense_id ON employee_advances (expense_id);

CREATE INDEX ix_employee_advances_advance_date ON employee_advances (advance_date);

CREATE TABLE employee_advance_installments (
	id SERIAL NOT NULL, 
	employee_id INTEGER NOT NULL, 
	advance_expense_id INTEGER NOT NULL, 
	installment_number INTEGER NOT NULL, 
	total_installments INTEGER NOT NULL, 
	amount NUMERIC(12, 2) NOT NULL, 
	currency VARCHAR(10) NOT NULL, 
	due_date DATE NOT NULL, 
	paid BOOLEAN NOT NULL, 
	paid_date DATE, 
	paid_in_salary_expense_id INTEGER, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(employee_id) REFERENCES employees (id), 
	FOREIGN KEY(advance_expense_id) REFERENCES expenses (id), 
	FOREIGN KEY(paid_in_salary_expense_id) REFERENCES expenses (id)
);

CREATE INDEX ix_employee_advance_installments_created_at ON employee_advance_installments (created_at);

CREATE INDEX ix_employee_advance_installments_paid_in_salary_expense_id ON employee_advance_installments (paid_in_salary_expense_id);

CREATE INDEX ix_employee_advance_installments_due_date ON employee_advance_installments (due_date);

CREATE INDEX ix_employee_advance_installments_employee_id ON employee_advance_installments (employee_id);

CREATE INDEX ix_employee_advance_installments_paid_date ON employee_advance_installments (paid_date);

CREATE INDEX ix_employee_advance_installments_updated_at ON employee_advance_installments (updated_at);

CREATE INDEX ix_employee_advance_installments_advance_expense_id ON employee_advance_installments (advance_expense_id);

CREATE INDEX ix_employee_advance_installments_paid ON employee_advance_installments (paid);

CREATE TABLE sale_return_lines (
	id SERIAL NOT NULL, 
	sale_return_id INTEGER NOT NULL, 
	product_id INTEGER NOT NULL, 
	warehouse_id INTEGER, 
	quantity INTEGER NOT NULL, 
	unit_price NUMERIC(12, 2) NOT NULL, 
	notes VARCHAR(200), 
	condition VARCHAR(10) NOT NULL, 
	liability_party VARCHAR(8), 
	PRIMARY KEY (id), 
	CONSTRAINT ck_sale_return_qty_pos CHECK (quantity > 0), 
	CONSTRAINT ck_sale_return_price_ge0 CHECK (unit_price >= 0), 
	FOREIGN KEY(sale_return_id) REFERENCES sale_returns (id) ON DELETE CASCADE, 
	FOREIGN KEY(product_id) REFERENCES products (id), 
	FOREIGN KEY(warehouse_id) REFERENCES warehouses (id) ON DELETE SET NULL
);

CREATE INDEX ix_sale_return_lines_warehouse_id ON sale_return_lines (warehouse_id);

CREATE INDEX ix_sale_return_lines_sale_return_id ON sale_return_lines (sale_return_id);

CREATE INDEX ix_sale_return_lines_liability_party ON sale_return_lines (liability_party);

CREATE INDEX ix_sale_return_line_prod_wh ON sale_return_lines (product_id, warehouse_id);

CREATE INDEX ix_sale_return_lines_product_id ON sale_return_lines (product_id);

CREATE INDEX ix_sale_return_lines_condition ON sale_return_lines (condition);

CREATE TABLE payments (
	id SERIAL NOT NULL, 
	payment_number VARCHAR(50) NOT NULL, 
	payment_date TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	subtotal NUMERIC(12, 2), 
	tax_rate NUMERIC(5, 2), 
	tax_amount NUMERIC(12, 2), 
	total_amount NUMERIC(12, 2) NOT NULL, 
	currency VARCHAR(10) NOT NULL, 
	fx_rate_used NUMERIC(10, 6), 
	fx_rate_source VARCHAR(20), 
	fx_rate_timestamp TIMESTAMP WITHOUT TIME ZONE, 
	fx_base_currency VARCHAR(10), 
	fx_quote_currency VARCHAR(10), 
	method VARCHAR(6) NOT NULL, 
	status VARCHAR(9) NOT NULL, 
	direction VARCHAR(3) NOT NULL, 
	entity_type VARCHAR(13) NOT NULL, 
	reference VARCHAR(100), 
	receipt_number VARCHAR(50), 
	notes TEXT, 
	receiver_name VARCHAR(200), 
	deliverer_name VARCHAR(200), 
	check_number VARCHAR(100), 
	check_bank VARCHAR(100), 
	check_due_date TIMESTAMP WITHOUT TIME ZONE, 
	card_holder VARCHAR(100), 
	card_expiry VARCHAR(10), 
	card_last4 VARCHAR(4), 
	bank_transfer_ref VARCHAR(100), 
	created_by INTEGER, 
	customer_id INTEGER, 
	supplier_id INTEGER, 
	partner_id INTEGER, 
	shipment_id INTEGER, 
	expense_id INTEGER, 
	loan_settlement_id INTEGER, 
	sale_id INTEGER, 
	invoice_id INTEGER, 
	preorder_id INTEGER, 
	service_id INTEGER, 
	refund_of_id INTEGER, 
	idempotency_key VARCHAR(64), 
	is_archived BOOLEAN NOT NULL, 
	archived_at TIMESTAMP WITHOUT TIME ZONE, 
	archived_by INTEGER, 
	archive_reason VARCHAR(200), 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_payment_total_positive CHECK (total_amount > 0), 
	CONSTRAINT ck_payment_one_target CHECK ((
            (CASE WHEN customer_id IS NOT NULL THEN 1 ELSE 0 END) +
            (CASE WHEN supplier_id IS NOT NULL THEN 1 ELSE 0 END) +
            (CASE WHEN partner_id IS NOT NULL THEN 1 ELSE 0 END) +
            (CASE WHEN shipment_id IS NOT NULL THEN 1 ELSE 0 END) +
            (CASE WHEN expense_id IS NOT NULL THEN 1 ELSE 0 END) +
            (CASE WHEN loan_settlement_id IS NOT NULL THEN 1 ELSE 0 END) +
            (CASE WHEN sale_id IS NOT NULL THEN 1 ELSE 0 END) +
            (CASE WHEN invoice_id IS NOT NULL THEN 1 ELSE 0 END) +
            (CASE WHEN preorder_id IS NOT NULL THEN 1 ELSE 0 END) +
            (CASE WHEN service_id IS NOT NULL THEN 1 ELSE 0 END)
        ) <= 1), 
	FOREIGN KEY(created_by) REFERENCES users (id), 
	FOREIGN KEY(customer_id) REFERENCES customers (id) ON DELETE CASCADE, 
	FOREIGN KEY(supplier_id) REFERENCES suppliers (id) ON DELETE CASCADE, 
	FOREIGN KEY(partner_id) REFERENCES partners (id) ON DELETE CASCADE, 
	FOREIGN KEY(shipment_id) REFERENCES shipments (id) ON DELETE CASCADE, 
	FOREIGN KEY(expense_id) REFERENCES expenses (id) ON DELETE CASCADE, 
	FOREIGN KEY(loan_settlement_id) REFERENCES supplier_loan_settlements (id) ON DELETE CASCADE, 
	FOREIGN KEY(sale_id) REFERENCES sales (id) ON DELETE CASCADE, 
	FOREIGN KEY(invoice_id) REFERENCES invoices (id) ON DELETE CASCADE, 
	FOREIGN KEY(preorder_id) REFERENCES preorders (id) ON DELETE CASCADE, 
	FOREIGN KEY(service_id) REFERENCES service_requests (id) ON DELETE CASCADE, 
	FOREIGN KEY(refund_of_id) REFERENCES payments (id) ON DELETE SET NULL, 
	FOREIGN KEY(archived_by) REFERENCES users (id)
);

CREATE INDEX ix_payments_created_at ON payments (created_at);

CREATE INDEX ix_pay_sale_status_dir ON payments (sale_id, status, direction);

CREATE INDEX ix_pay_created_at ON payments (payment_date);

CREATE INDEX ix_payments_loan_settlement_id ON payments (loan_settlement_id);

CREATE INDEX ix_pay_inv_status_dir ON payments (invoice_id, status, direction);

CREATE INDEX ix_pay_cust_stat_dir ON payments (customer_id, status, direction);

CREATE INDEX ix_payments_supplier_id ON payments (supplier_id);

CREATE UNIQUE INDEX ix_payments_receipt_number ON payments (receipt_number);

CREATE INDEX ix_payments_updated_at ON payments (updated_at);

CREATE INDEX ix_pay_supplier_status_dir ON payments (supplier_id, status, direction);

CREATE INDEX ix_pay_srv_stat_dir ON payments (service_id, status, direction);

CREATE INDEX ix_payments_entity_type ON payments (entity_type);

CREATE INDEX ix_pay_partner_status_dir ON payments (partner_id, status, direction);

CREATE INDEX ix_pay_shp_stat_dir ON payments (shipment_id, status, direction);

CREATE INDEX ix_payments_sale_id ON payments (sale_id);

CREATE UNIQUE INDEX ix_payments_idempotency_key ON payments (idempotency_key);

CREATE INDEX ix_pay_preorder_status_dir ON payments (preorder_id, status, direction);

CREATE INDEX ix_pay_exp_stat_dir ON payments (expense_id, status, direction);

CREATE INDEX ix_payments_partner_id ON payments (partner_id);

CREATE INDEX ix_pay_supplier_dir_status_date ON payments (supplier_id, direction, status, payment_date);

CREATE INDEX ix_pay_method_date ON payments (method, payment_date);

CREATE INDEX ix_payments_method ON payments (method);

CREATE INDEX ix_payments_is_archived ON payments (is_archived);

CREATE INDEX ix_pay_partner_dir_status_date ON payments (partner_id, direction, status, payment_date);

CREATE INDEX ix_pay_created_by ON payments (created_by);

CREATE INDEX ix_payments_invoice_id ON payments (invoice_id);

CREATE INDEX ix_pay_customer_dir_status_date ON payments (customer_id, direction, status, payment_date);

CREATE INDEX ix_pay_total_amount ON payments (total_amount);

CREATE UNIQUE INDEX ix_payments_payment_number ON payments (payment_number);

CREATE INDEX ix_payments_shipment_id ON payments (shipment_id);

CREATE INDEX ix_payments_created_by ON payments (created_by);

CREATE INDEX ix_payments_archived_at ON payments (archived_at);

CREATE INDEX ix_pay_reversal ON payments (refund_of_id);

CREATE INDEX ix_pay_dir_stat_type ON payments (direction, status, entity_type);

CREATE INDEX ix_payments_preorder_id ON payments (preorder_id);

CREATE INDEX ix_payments_archived_by ON payments (archived_by);

CREATE INDEX ix_pay_status ON payments (status);

CREATE INDEX ix_payments_expense_id ON payments (expense_id);

CREATE INDEX ix_payments_customer_id ON payments (customer_id);

CREATE INDEX ix_pay_direction ON payments (direction);

CREATE INDEX ix_pay_currency ON payments (currency);

CREATE INDEX ix_payments_service_id ON payments (service_id);

CREATE TABLE asset_maintenance (
	id SERIAL NOT NULL, 
	asset_id INTEGER NOT NULL, 
	maintenance_date DATE NOT NULL, 
	maintenance_type VARCHAR(100), 
	cost NUMERIC(12, 2) NOT NULL, 
	expense_id INTEGER, 
	description TEXT, 
	next_maintenance_date DATE, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_maintenance_cost_ge_0 CHECK (cost >= 0), 
	FOREIGN KEY(asset_id) REFERENCES fixed_assets (id) ON DELETE CASCADE, 
	FOREIGN KEY(expense_id) REFERENCES expenses (id)
);

CREATE INDEX ix_asset_maintenance_asset_id ON asset_maintenance (asset_id);

CREATE INDEX ix_asset_maintenance_next_maintenance_date ON asset_maintenance (next_maintenance_date);

CREATE INDEX ix_asset_maintenance_expense_id ON asset_maintenance (expense_id);

CREATE INDEX ix_maintenance_asset_date ON asset_maintenance (asset_id, maintenance_date);

CREATE INDEX ix_asset_maintenance_maintenance_date ON asset_maintenance (maintenance_date);

CREATE INDEX ix_asset_maintenance_updated_at ON asset_maintenance (updated_at);

CREATE INDEX ix_asset_maintenance_maintenance_type ON asset_maintenance (maintenance_type);

CREATE INDEX ix_asset_maintenance_created_at ON asset_maintenance (created_at);

CREATE TABLE payment_splits (
	id SERIAL NOT NULL, 
	payment_id INTEGER NOT NULL, 
	method VARCHAR(6) NOT NULL, 
	amount NUMERIC(12, 2) NOT NULL, 
	details JSON NOT NULL, 
	currency VARCHAR(10) NOT NULL, 
	converted_amount NUMERIC(12, 2) NOT NULL, 
	converted_currency VARCHAR(10) NOT NULL, 
	fx_rate_used NUMERIC(10, 6), 
	fx_rate_source VARCHAR(20), 
	fx_rate_timestamp TIMESTAMP WITHOUT TIME ZONE, 
	fx_base_currency VARCHAR(10), 
	fx_quote_currency VARCHAR(10), 
	PRIMARY KEY (id), 
	CONSTRAINT chk_split_amount_positive CHECK (amount > 0), 
	FOREIGN KEY(payment_id) REFERENCES payments (id) ON DELETE CASCADE
);

CREATE INDEX ix_payment_splits_payment_id ON payment_splits (payment_id);

CREATE INDEX ix_payment_splits_method ON payment_splits (method);

CREATE TABLE online_payments (
	id SERIAL NOT NULL, 
	payment_ref VARCHAR(100), 
	order_id INTEGER NOT NULL, 
	amount NUMERIC(12, 2) NOT NULL, 
	currency VARCHAR(10) NOT NULL, 
	fx_rate_used NUMERIC(10, 6), 
	fx_rate_source VARCHAR(20), 
	fx_rate_timestamp TIMESTAMP WITHOUT TIME ZONE, 
	fx_base_currency VARCHAR(10), 
	fx_quote_currency VARCHAR(10), 
	method VARCHAR(50), 
	gateway VARCHAR(50), 
	status VARCHAR(8) NOT NULL, 
	transaction_data JSON, 
	processed_at TIMESTAMP WITHOUT TIME ZONE, 
	card_last4 VARCHAR(4), 
	card_encrypted BYTEA, 
	card_expiry VARCHAR(5), 
	cardholder_name VARCHAR(128), 
	card_brand VARCHAR(20), 
	card_fingerprint VARCHAR(64), 
	payment_id INTEGER, 
	idempotency_key VARCHAR(64), 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT chk_online_payment_amount_positive CHECK (amount > 0), 
	FOREIGN KEY(order_id) REFERENCES online_preorders (id) ON DELETE CASCADE, 
	FOREIGN KEY(payment_id) REFERENCES payments (id) ON DELETE SET NULL
);

CREATE INDEX ix_online_payments_updated_at ON online_payments (updated_at);

CREATE INDEX ix_online_payments_status ON online_payments (status);

CREATE INDEX ix_online_payments_order_id ON online_payments (order_id);

CREATE INDEX ix_online_payments_gateway_status ON online_payments (gateway, status);

CREATE INDEX ix_online_payments_card_fingerprint ON online_payments (card_fingerprint);

CREATE INDEX ix_online_payments_created_at ON online_payments (created_at);

CREATE INDEX ix_online_payments_order_status ON online_payments (order_id, status);

CREATE UNIQUE INDEX ix_online_payments_payment_ref ON online_payments (payment_ref);

CREATE UNIQUE INDEX ix_online_payments_idempotency_key ON online_payments (idempotency_key);

CREATE INDEX ix_online_payments_payment_id ON online_payments (payment_id);

CREATE INDEX ix_online_payments_card_last4 ON online_payments (card_last4);

CREATE TABLE checks (
	id SERIAL NOT NULL, 
	check_number VARCHAR(100) NOT NULL, 
	check_bank VARCHAR(200) NOT NULL, 
	check_date TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	check_due_date TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	amount NUMERIC(12, 2) NOT NULL, 
	currency VARCHAR(10) NOT NULL, 
	fx_rate_issue NUMERIC(10, 6), 
	fx_rate_issue_source VARCHAR(20), 
	fx_rate_issue_timestamp TIMESTAMP WITHOUT TIME ZONE, 
	fx_rate_issue_base VARCHAR(10), 
	fx_rate_issue_quote VARCHAR(10), 
	fx_rate_cash NUMERIC(10, 6), 
	fx_rate_cash_source VARCHAR(20), 
	fx_rate_cash_timestamp TIMESTAMP WITHOUT TIME ZONE, 
	fx_rate_cash_base VARCHAR(10), 
	fx_rate_cash_quote VARCHAR(10), 
	direction VARCHAR(3) NOT NULL, 
	status VARCHAR(11) NOT NULL, 
	drawer_name VARCHAR(200), 
	drawer_phone VARCHAR(20), 
	drawer_id_number VARCHAR(50), 
	drawer_address TEXT, 
	payee_name VARCHAR(200), 
	payee_phone VARCHAR(20), 
	payee_account VARCHAR(50), 
	notes TEXT, 
	internal_notes TEXT, 
	reference_number VARCHAR(100), 
	status_history TEXT, 
	customer_id INTEGER, 
	supplier_id INTEGER, 
	partner_id INTEGER, 
	payment_id INTEGER, 
	created_by_id INTEGER NOT NULL, 
	is_archived BOOLEAN NOT NULL, 
	archived_at TIMESTAMP WITHOUT TIME ZONE, 
	archived_by INTEGER, 
	archive_reason VARCHAR(200), 
	resubmit_allowed_count INTEGER NOT NULL, 
	legal_return_allowed_count INTEGER NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_check_amount_positive CHECK (amount > 0), 
	FOREIGN KEY(customer_id) REFERENCES customers (id) ON DELETE SET NULL, 
	FOREIGN KEY(supplier_id) REFERENCES suppliers (id) ON DELETE SET NULL, 
	FOREIGN KEY(partner_id) REFERENCES partners (id) ON DELETE SET NULL, 
	FOREIGN KEY(payment_id) REFERENCES payments (id) ON DELETE SET NULL, 
	FOREIGN KEY(created_by_id) REFERENCES users (id), 
	FOREIGN KEY(archived_by) REFERENCES users (id)
);

CREATE INDEX ix_checks_supplier_id ON checks (supplier_id);

CREATE INDEX ix_checks_check_due_date ON checks (check_due_date);

CREATE INDEX ix_checks_created_at ON checks (created_at);

CREATE INDEX ix_checks_created_by_id ON checks (created_by_id);

CREATE INDEX ix_checks_archived_by ON checks (archived_by);

CREATE INDEX ix_checks_direction_status ON checks (direction, status);

CREATE INDEX ix_checks_archived_at ON checks (archived_at);

CREATE INDEX ix_checks_check_number ON checks (check_number);

CREATE INDEX ix_checks_status_due_date ON checks (status, check_due_date);

CREATE INDEX ix_checks_direction ON checks (direction);

CREATE INDEX ix_checks_status ON checks (status);

CREATE INDEX ix_checks_updated_at ON checks (updated_at);

CREATE INDEX ix_checks_is_archived ON checks (is_archived);

CREATE INDEX ix_checks_customer_id ON checks (customer_id);

CREATE INDEX ix_checks_payment_id ON checks (payment_id);

CREATE INDEX ix_checks_partner_id ON checks (partner_id);

CREATE TABLE bank_transactions (
	id SERIAL NOT NULL, 
	bank_account_id INTEGER NOT NULL, 
	statement_id INTEGER, 
	transaction_date DATE NOT NULL, 
	value_date DATE, 
	reference VARCHAR(100), 
	description TEXT, 
	debit NUMERIC(15, 2), 
	credit NUMERIC(15, 2), 
	balance NUMERIC(15, 2), 
	matched BOOLEAN NOT NULL, 
	payment_id INTEGER, 
	gl_batch_id INTEGER, 
	reconciliation_id INTEGER, 
	notes TEXT, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_bank_tx_debit_credit CHECK ((debit = 0 AND credit > 0) OR (credit = 0 AND debit > 0) OR (debit = 0 AND credit = 0)), 
	FOREIGN KEY(bank_account_id) REFERENCES bank_accounts (id) ON DELETE CASCADE, 
	FOREIGN KEY(statement_id) REFERENCES bank_statements (id) ON DELETE CASCADE, 
	FOREIGN KEY(payment_id) REFERENCES payments (id), 
	FOREIGN KEY(gl_batch_id) REFERENCES gl_batches (id), 
	FOREIGN KEY(reconciliation_id) REFERENCES bank_reconciliations (id)
);

CREATE INDEX ix_bank_transactions_reconciliation_id ON bank_transactions (reconciliation_id);

CREATE INDEX ix_bank_transactions_gl_batch_id ON bank_transactions (gl_batch_id);

CREATE INDEX ix_bank_transactions_created_at ON bank_transactions (created_at);

CREATE INDEX ix_bank_transactions_statement_id ON bank_transactions (statement_id);

CREATE INDEX ix_bank_transactions_payment_id ON bank_transactions (payment_id);

CREATE INDEX ix_bank_transactions_value_date ON bank_transactions (value_date);

CREATE INDEX ix_bank_tx_matched ON bank_transactions (matched, bank_account_id);

CREATE INDEX ix_bank_transactions_matched ON bank_transactions (matched);

CREATE INDEX ix_bank_tx_account_date ON bank_transactions (bank_account_id, transaction_date);

CREATE INDEX ix_bank_transactions_transaction_date ON bank_transactions (transaction_date);

CREATE INDEX ix_bank_transactions_updated_at ON bank_transactions (updated_at);

CREATE INDEX ix_bank_transactions_bank_account_id ON bank_transactions (bank_account_id);

CREATE INDEX ix_bank_transactions_reference ON bank_transactions (reference);

ALTER TABLE branches ADD CONSTRAINT fk_branches_manager_employee_id FOREIGN KEY(manager_employee_id) REFERENCES employees (id);

ALTER TABLE sites ADD CONSTRAINT fk_sites_manager_employee_id FOREIGN KEY(manager_employee_id) REFERENCES employees (id);

