# فهرس المسارات (Routes)

| المسار | Endpoint | الطرق |
|--------|----------|-------|
| / | main.dashboard | GET |
| /@vite/client | vite_client_shim | GET |
| /admin/reports/ | admin_reports.index | GET |
| /admin/reports/api/stats | admin_reports.api_stats | GET |
| /admin/reports/cards | admin_reports.cards | GET |
| /admin/reports/cards/<int:pid>/reveal | admin_reports.cards_reveal | POST |
| /admin/reports/dashboard | admin_reports.dashboard | GET |
| /admin/reports/download-backup | admin_reports.download_backup | GET |
| /admin/reports/logs/view | admin_reports.view_logs | GET |
| /admin/reports/preorders | admin_reports.preorders | GET |
| /advanced/accounting-control | advanced.accounting_control | GET, POST |
| /advanced/accounting-control/export-settings | advanced.accounting_control_export_settings | GET |
| /advanced/accounting-control/import-settings | advanced.accounting_control_import_settings | POST |
| /advanced/accounting-control/manual-backup | advanced.accounting_control_manual_backup | POST |
| /advanced/accounting-control/report.pdf | advanced.accounting_control_report_pdf | GET |
| /advanced/accounting-control/system-check | advanced.accounting_control_system_check | GET |
| /advanced/api-generator | advanced.api_generator | GET, POST |
| /advanced/api/advanced-accounting-stats | advanced.api_accounting_stats | GET |
| /advanced/api/check-ip/<ip> | security_control.api_check_ip | GET |
| /advanced/api/performance/stats | advanced.api_performance_stats | GET |
| /advanced/backup-manager | advanced.backup_manager | GET, POST |
| /advanced/dashboard-links | advanced.dashboard_links | GET, POST |
| /advanced/database-optimizer | advanced.database_optimizer | GET, POST |
| /advanced/db-merger | advanced.db_merger | GET, POST |
| /advanced/delete-backup/<filename> | advanced.delete_backup | POST |
| /advanced/download-backup/<filename> | advanced.download_backup | GET |
| /advanced/download-cloned-system/<clone_name> | advanced.download_cloned_system | GET |
| /advanced/download-mobile-app/<app_name> | advanced.download_mobile_app | GET |
| /advanced/feature-flags | advanced.feature_flags | GET, POST |
| /advanced/financial-control | advanced.financial_control | GET, POST |
| /advanced/licensing | advanced.licensing | GET, POST |
| /advanced/mobile-app-generator | advanced.mobile_app_generator | GET, POST |
| /advanced/module-manager | advanced.module_manager | GET, POST |
| /advanced/multi-tenant | advanced.multi_tenant | GET, POST |
| /advanced/owner-hub | advanced.owner_hub | GET |
| /advanced/owner-smoke-checklist | advanced.owner_smoke_checklist | GET, POST |
| /advanced/performance-profiler | advanced.performance_profiler | GET |
| /advanced/restore-backup/<filename> | advanced.restore_backup | POST |
| /advanced/restore-json-backup/<filename> | advanced.restore_json_backup | POST |
| /advanced/security-control | security_control.security_control | GET, POST |
| /advanced/system-cloner | advanced.system_cloner | GET, POST |
| /advanced/system-health | advanced.system_health | GET, POST |
| /advanced/test-db-connection | advanced.test_db_connection | POST |
| /advanced/toggle-auto-backup | advanced.toggle_auto_backup | POST |
| /advanced/version-control | advanced.version_control | GET, POST |
| /ai-admin/advanced-training | ai_admin.advanced_training | GET |
| /ai-admin/command/<command_name> | ai_admin.execute_command | POST |
| /ai-admin/config | ai_admin.ai_config_dashboard | GET |
| /ai-admin/daily-reports | ai_admin.daily_reports | GET |
| /ai-admin/evolution-report | ai_admin.evolution_report | GET |
| /ai-admin/marathon-training | ai_admin.marathon_training | POST |
| /ai-admin/memory_stats | ai_admin.memory_stats | GET |
| /ai-admin/performance | ai_admin.performance_report | GET |
| /ai-admin/reset-knowledge | ai_admin.reset_knowledge | POST |
| /ai-admin/run-code-scan | ai_admin.run_code_scan | POST |
| /ai-admin/settings | ai_admin.ai_settings | GET, POST |
| /ai-admin/stats-api | ai_admin.stats_api | GET |
| /ai-admin/system_status | ai_admin.system_status | GET |
| /ai-admin/toggle-visibility | ai_admin.toggle_visibility | POST |
| /ai-admin/train-all-packages | ai_admin.train_all_packages | POST |
| /ai-admin/train-package | ai_admin.train_package | POST |
| /ai-admin/training-log | ai_admin.training_log | GET |
| /ai-admin/training-status | ai_admin.training_status | GET |
| /ai-admin/upload_book | ai_admin.upload_book | POST |
| /ai/analytics/queries | ai.analytics_queries | GET |
| /ai/api-keys/save | ai.save_api_key | POST |
| /ai/api-keys/test | ai.test_api_key_route | POST |
| /ai/assistant | ai.assistant | GET, POST |
| /ai/chat | ai.chat | POST |
| /ai/evolution-report | ai.evolution_report | GET |
| /ai/hub | ai.hub | GET |
| /ai/models/status | ai.models_status | GET |
| /ai/stats/live | ai.live_stats | GET |
| /ai/system-map | ai.system_map | GET, POST |
| /ai/training/start | ai.start_training | POST |
| /ai/training/status/<training_id> | ai.training_status | GET |
| /api/ | api.index | GET |
| /api/archive/<int:archive_id> | api.api_delete_archive | DELETE |
| /api/archive/<int:archive_id> | api.api_get_archive | GET |
| /api/archive/<int:archive_id>/restore | api.api_restore_archive | POST |
| /api/archive/customer/<int:customer_id> | api.api_archive_customer | POST |
| /api/archive/expense/<int:expense_id> | api.api_archive_expense | POST |
| /api/archive/list | api.api_list_archives | GET |
| /api/archive/partner/<int:partner_id> | api.api_archive_partner | POST |
| /api/archive/payment/<int:payment_id> | api.api_archive_payment | POST |
| /api/archive/sale/<int:sale_id> | api.api_archive_sale | POST |
| /api/archive/service/<int:service_id> | api.api_archive_service | POST |
| /api/archive/stats | api.api_archive_stats | GET |
| /api/archive/supplier/<int:supplier_id> | api.api_archive_supplier | POST |
| /api/balances/clear-cache | balances_api.clear_balance_cache | POST |
| /api/balances/customer/<int:customer_id> | balances_api.get_customer_balance | GET |
| /api/balances/dashboard | balances_api.balances_dashboard | GET |
| /api/balances/partner/<int:partner_id> | balances_api.get_partner_balance | GET |
| /api/balances/summary | balances_api.get_balances_summary | GET |
| /api/balances/supplier/<int:supplier_id> | balances_api.get_supplier_balance | GET |
| /api/barcode/validate | bp_barcode.barcode_validate | GET |
| /api/categories | api.create_category | POST |
| /api/customers | api.create_customer_api | POST |
| /api/customers | api.customers | GET |
| /api/docs | api.docs | GET |
| /api/equipment-types/create | api.create_equipment_type | POST |
| /api/equipment-types/search | api.search_equipment_types | GET |
| /api/exchange-rates | api.get_exchange_rates | GET |
| /api/exchange_transactions | api.create_exchange_transaction | POST |
| /api/exchange_transactions | api.list_exchange_transactions | GET |
| /api/exchange_transactions/<int:id> | api.delete_exchange_transaction | DELETE |
| /api/exchange_transactions/<int:id> | api.get_exchange_transaction | GET |
| /api/expenses | api.expenses | GET |
| /api/health | api.health | GET |
| /api/invoices | api.invoices | GET |
| /api/loan_settlements | api.loan_settlements | GET |
| /api/me | api.me | GET |
| /api/online_preorders | api.online_preorders | GET |
| /api/partners | api.get_partners | GET |
| /api/partners/<int:id> | api.api_delete_partner | DELETE |
| /api/partners/<int:id> | api.api_update_partner | PATCH |
| /api/partners/<int:id> | api.api_update_partner | PUT |
| /api/payments | api.payments | GET |
| /api/permissions.csv | api.permissions_csv | GET |
| /api/permissions.json | api.permissions_json | GET |
| /api/preorders | api.preorders | GET |
| /api/products | api.products | GET |
| /api/products/<int:id> | api.update_product | PATCH |
| /api/products/<int:pid>/info | api.product_info | GET |
| /api/products/<int:product_id>/stock | api.get_product_stock | GET |
| /api/products/barcode/<code> | api.product_by_barcode | GET |
| /api/restore/customer/<int:customer_id> | api.api_restore_customer | POST |
| /api/restore/expense/<int:expense_id> | api.api_restore_expense | POST |
| /api/restore/partner/<int:partner_id> | api.api_restore_partner | POST |
| /api/restore/payment/<int:payment_id> | api.api_restore_payment | POST |
| /api/restore/sale/<int:sale_id> | api.api_restore_sale | POST |
| /api/restore/service/<int:service_id> | api.api_restore_service | POST |
| /api/restore/supplier/<int:supplier_id> | api.api_restore_supplier | POST |
| /api/sales | api.create_sale_api | POST |
| /api/sales | api.sales | GET |
| /api/sales/<int:id> | api.update_sale_api | PATCH |
| /api/sales/<int:id> | api.update_sale_api | PUT |
| /api/sales/<int:id>/payments | api.sale_payments_api | GET |
| /api/sales/<int:id>/status | api.change_sale_status_api | POST |
| /api/sales/quick | api.quick_sell_api | POST |
| /api/search_categories | api.search_categories | GET |
| /api/search_customers | api.search_customers | GET |
| /api/search_employees | api.search_employees | GET |
| /api/search_partners | api.search_partners | GET |
| /api/search_payments | api.search_payments | GET |
| /api/search_products | api.search_products | GET |
| /api/search_stock_adjustments | api.search_stock_adjustments | GET |
| /api/search_supplier_loans | api.search_supplier_loans | GET |
| /api/search_suppliers | api.search_suppliers | GET |
| /api/search_utility_accounts | api.search_utility_accounts | GET |
| /api/search_warehouses | api.search_warehouses | GET |
| /api/services | api.services | GET |
| /api/shipments | api.create_shipment_api | POST |
| /api/shipments | api.shipments | GET |
| /api/shipments/<int:id> | api.delete_shipment_api | DELETE |
| /api/shipments/<int:id> | api.get_shipment_api | GET |
| /api/shipments/<int:id> | api.update_shipment_api | PUT |
| /api/shipments/<int:id> | api.update_shipment_api | PATCH |
| /api/shipments/<int:id>/cancel | api.api_cancel_shipment | POST |
| /api/shipments/<int:id>/mark-arrived | api.api_mark_arrived | POST |
| /api/stock_adjustments/<int:id>/total | api.stock_adjustment_total | GET |
| /api/suppliers | api.create_supplier | POST |
| /api/suppliers | api.get_suppliers | GET |
| /api/suppliers/<int:id> | api.delete_supplier | DELETE |
| /api/suppliers/<int:id> | api.get_supplier | GET |
| /api/suppliers/<int:id> | api.update_supplier | PATCH |
| /api/suppliers/<int:id> | api.update_supplier | PUT |
| /api/transfers | api.transfers | GET |
| /api/users | api.users | GET |
| /api/warehouses | api.warehouses | GET |
| /api/warehouses/<int:id> | api.api_delete_warehouse | DELETE |
| /api/warehouses/<int:id> | api.api_update_warehouse | PATCH |
| /api/warehouses/<int:id> | api.api_update_warehouse | PUT |
| /api/warehouses/<int:id>/products/stocked | api.api_warehouse_products_stocked | GET |
| /api/warehouses/<int:warehouse_id>/info | api.get_warehouse_info | GET |
| /api/warehouses/<int:warehouse_id>/partner_shares | api.get_partner_shares | GET |
| /api/warehouses/<int:warehouse_id>/partner_shares | api.update_partner_shares | POST |
| /api/warehouses/<int:warehouse_id>/stock | api.update_stock | POST |
| /api/warehouses/<int:warehouse_id>/transfer | api.transfer_between_warehouses | POST |
| /api/warehouses/<int:wid>/products | api.api_products_by_warehouse | GET |
| /api/warehouses/inventory | api.api_inventory_summary | GET |
| /archive/ | archive.index | GET |
| /archive/bulk-archive | archive.bulk_archive | GET, POST |
| /archive/delete/<int:archive_id> | archive.delete_archive | POST |
| /archive/export | archive.export_archives | GET |
| /archive/restore/<int:archive_id> | archive.restore_archive | GET, POST |
| /archive/search | archive.search | GET, POST |
| /archive/view/<int:archive_id> | archive.view_archive | GET |
| /assets/ | assets.index | GET |
| /assets/add | assets.add | GET, POST |
| /assets/categories | assets.categories | GET |
| /assets/report/depreciation | assets.depreciation_schedule | GET |
| /assets/report/register | assets.asset_register | GET |
| /assets/view/<int:id> | assets.view | GET |
| /auth/customer_password_reset/<token> | auth.customer_password_reset | GET, POST |
| /auth/customer_password_reset_request | auth.customer_password_reset_request | GET, POST |
| /auth/login | auth.login | GET, POST |
| /auth/logout | auth.logout | POST |
| /auth/register/customer | auth.customer_register | GET, POST |
| /automated-backup-status | main.automated_backup_status | GET |
| /backup_db | main.backup_db | GET |
| /bank/accounts | bank.accounts | GET |
| /bank/accounts/<int:id> | bank.view_account | GET |
| /bank/accounts/add | bank.add_account | GET, POST |
| /bank/accounts/edit/<int:id> | bank.edit_account | GET, POST |
| /bank/api/auto-match/<int:bank_account_id> | bank.auto_match | POST |
| /bank/reconciliation | bank.reconciliations | GET |
| /bank/reconciliation/<int:id> | bank.view_reconciliation | GET |
| /bank/reconciliation/<int:id>/complete | bank.complete_reconciliation | POST |
| /bank/reconciliation/new | bank.new_reconciliation | GET, POST |
| /bank/reports/aged | bank.report_aged | GET |
| /bank/reports/summary | bank.report_summary | GET |
| /bank/reports/unmatched | bank.report_unmatched | GET |
| /bank/statements | bank.statements | GET |
| /bank/statements/<int:id> | bank.view_statement | GET |
| /bank/statements/upload | bank.upload_statement | GET, POST |
| /barcode/ | barcode_scanner.index | GET |
| /barcode/auto-assign | barcode_scanner.auto_assign_barcodes | POST |
| /barcode/bulk-generate | barcode_scanner.bulk_generate | POST |
| /barcode/bulk-import | barcode_scanner.bulk_import_products | POST |
| /barcode/bulk-scan | barcode_scanner.bulk_scan_page | GET |
| /barcode/check-product | barcode_scanner.check_product | GET |
| /barcode/check-product | barcode_scanner.check_product_exists | GET |
| /barcode/generate | barcode_scanner.generate_barcode | POST |
| /barcode/inventory/update | barcode_scanner.inventory_update | POST |
| /barcode/print/<int:product_id> | barcode_scanner.print_barcode | GET |
| /barcode/scan | barcode_scanner.scan_barcode | POST |
| /barcode/search | barcode_scanner.search_products | GET |
| /barcode/stats | barcode_scanner.barcode_stats | GET |
| /barcode/warehouse-fields | barcode_scanner.get_warehouse_fields | GET |
| /barcode/warehouses | barcode_scanner.get_warehouses | GET |
| /branches/ | branches_bp.list_branches | GET |
| /branches/<int:branch_id>/archive | branches_bp.archive_branch | POST |
| /branches/<int:branch_id>/dashboard | branches_bp.branch_dashboard | GET |
| /branches/<int:branch_id>/edit | branches_bp.edit_branch | GET, POST |
| /branches/<int:branch_id>/report | branches_bp.branch_report | GET |
| /branches/<int:branch_id>/restore | branches_bp.restore_branch | POST |
| /branches/<int:branch_id>/sites | branches_bp.list_sites | GET |
| /branches/<int:branch_id>/sites/create | branches_bp.create_site | GET, POST |
| /branches/api/search | branches_bp.api_search_branches | GET |
| /branches/api/sites/<int:branch_id> | branches_bp.api_branch_sites | GET |
| /branches/create | branches_bp.create_branch | GET, POST |
| /branches/export | branches_bp.export_branches | GET |
| /branches/sites/<int:site_id>/archive | branches_bp.archive_site | POST |
| /branches/sites/<int:site_id>/edit | branches_bp.edit_site | GET, POST |
| /budgets/ | budgets.index | GET |
| /budgets/add | budgets.add | GET, POST |
| /budgets/dashboard | budgets.dashboard | GET |
| /budgets/edit/<int:id> | budgets.edit | GET, POST |
| /budgets/report/variance | budgets.variance_analysis | GET |
| /budgets/report/vs-actual | budgets.budget_vs_actual | GET |
| /checks/ | checks.index | GET |
| /checks/api/alerts | checks.get_alerts | GET |
| /checks/api/check-lifecycle/<int:check_id>/<check_type> | checks.get_check_lifecycle | GET |
| /checks/api/checks | checks.get_checks | GET |
| /checks/api/first-incomplete | checks.get_first_incomplete_check | GET |
| /checks/api/get-details/<check_token> | checks.get_check_details | GET |
| /checks/api/mark-settled/<check_token> | checks.mark_check_settled | POST |
| /checks/api/statistics | checks.get_statistics | GET |
| /checks/api/unsettle/<check_token> | checks.unsettle_check | POST |
| /checks/api/update-details/<check_token> | checks.update_check_details | POST |
| /checks/api/update-status/<check_id> | checks.update_check_status | POST |
| /checks/archive/<int:check_id> | archive_routes.archive_check | POST |
| /checks/delete/<int:check_id> | checks.delete_check | POST |
| /checks/detail/<int:check_id> | checks.check_detail | GET |
| /checks/edit/<int:check_id> | checks.edit_check | GET, POST |
| /checks/new | checks.add_check | GET, POST |
| /checks/reports | checks.reports | GET |
| /cost-centers/ | cost_centers.index | GET |
| /cost-centers/<int:id> | cost_centers.view | GET |
| /cost-centers/<int:id>/allocate | cost_centers.allocate | POST |
| /cost-centers/add | cost_centers.add | GET, POST |
| /cost-centers/alerts | cost_centers_advanced.alerts_list | GET |
| /cost-centers/alerts/<int:alert_id>/toggle | cost_centers_advanced.toggle_alert | POST |
| /cost-centers/alerts/add | cost_centers_advanced.add_alert | POST |
| /cost-centers/allocation-rules | cost_centers_advanced.allocation_rules | GET |
| /cost-centers/allocation-rules/<int:rule_id>/execute | cost_centers_advanced.execute_allocation_rule | POST |
| /cost-centers/allocation-rules/add | cost_centers_advanced.add_allocation_rule | GET, POST |
| /cost-centers/api/hierarchy | cost_centers.api_hierarchy | GET |
| /cost-centers/dashboard | cost_centers_advanced.dashboard | GET |
| /cost-centers/edit/<int:id> | cost_centers.edit | GET, POST |
| /cost-centers/reports/budget-variance | cost_centers.report_budget_variance | GET |
| /cost-centers/reports/comparison | cost_centers.report_comparison | GET |
| /cost-centers/reports/summary | cost_centers.report_summary | GET |
| /cost-centers/reports/trends | cost_centers_advanced.report_trends | GET |
| /currencies/ | currencies.list | GET |
| /currencies/exchange-rates | currencies.exchange_rates | GET |
| /currencies/exchange-rates/<int:rate_id>/delete | currencies.delete_exchange_rate | POST |
| /currencies/exchange-rates/<int:rate_id>/edit | currencies.edit_exchange_rate | GET, POST |
| /currencies/exchange-rates/<int:rate_id>/toggle | currencies.toggle_exchange_rate | POST |
| /currencies/exchange-rates/new | currencies.new_exchange_rate | GET, POST |
| /currencies/new | currencies.new_currency | GET, POST |
| /currencies/reports | currencies.reports | GET |
| /currencies/settings | currencies.settings | GET |
| /currencies/settings/test-online | currencies.test_online | POST |
| /currencies/settings/toggle-online | currencies.toggle_online | POST |
| /currencies/settings/update-interval | currencies.update_interval | POST |
| /currencies/test-rate | currencies.test_rate | POST |
| /currencies/update-rates | currencies.update_rates | GET, POST |
| /customers/ | customers_bp.list_customers | GET |
| /customers/<int:customer_id> | customers_bp.customer_detail | GET |
| /customers/<int:customer_id>/account_statement | customers_bp.account_statement | GET |
| /customers/<int:customer_id>/analytics | customers_bp.customer_analytics | GET |
| /customers/<int:customer_id>/edit | customers_bp.edit_customer | GET, POST |
| /customers/<int:customer_id>/export_vcf | customers_bp.export_customer_vcf | GET |
| /customers/<int:customer_id>/send_whatsapp | customers_bp.customer_whatsapp | GET |
| /customers/<int:id>/delete | customers_bp.delete_customer | POST |
| /customers/advanced_filter | customers_bp.advanced_filter | GET |
| /customers/archive/<int:customer_id> | customers_bp.archive_customer | POST |
| /customers/balances/recalculate | customers_bp.balances_recalculate | POST |
| /customers/create | customers_bp.create_customer | POST |
| /customers/create | customers_bp.create_form | GET |
| /customers/export | customers_bp.export_customers | GET |
| /customers/export-online-credentials | customers_bp.export_online_credentials | GET |
| /customers/export/contacts | customers_bp.export_contacts | GET, POST |
| /customers/import | customers_bp.import_customers | GET, POST |
| /customers/make-online-all | customers_bp.make_online_all | POST |
| /customers/reset-passwords | customers_bp.reset_passwords | POST |
| /customers/restore/<int:customer_id> | customers_bp.restore_customer | POST |
| /customers/set-default-emails | customers_bp.set_default_emails | POST |
| /docs/accounting/ | accounting_docs.index | GET |
| /docs/accounting/accounting-standards | accounting_docs.accounting_standards | GET |
| /docs/accounting/audit-policies | accounting_docs.audit_policies | GET |
| /docs/accounting/chart-of-accounts | accounting_docs.chart_of_accounts | GET |
| /docs/accounting/correction-procedures | accounting_docs.correction_procedures | GET |
| /docs/accounting/gl-accounts-reference | accounting_docs.gl_accounts_reference | GET |
| /docs/accounting/system-health-guide | accounting_docs.system_health_guide | GET |
| /engineering/ | engineering.dashboard | GET |
| /engineering/reports/productivity | engineering.report_productivity | GET |
| /engineering/skills | engineering.skills | GET |
| /engineering/tasks | engineering.tasks | GET |
| /engineering/tasks/add | engineering.add_task | GET, POST |
| /engineering/teams | engineering.teams | GET |
| /engineering/teams/add | engineering.add_team | GET, POST |
| /engineering/timesheets | engineering.timesheets | GET |
| /engineering/timesheets/add | engineering.add_timesheet | GET, POST |
| /expenses/ | expenses_bp.list_expenses | GET |
| /expenses/<int:exp_id> | expenses_bp.detail | GET |
| /expenses/<int:exp_id>/pay | expenses_bp.pay | GET |
| /expenses/add | expenses_bp.create_expense | GET, POST |
| /expenses/archive/<int:expense_id> | expenses_bp.archive_expense | POST |
| /expenses/delete/<int:exp_id> | expenses_bp.delete | POST |
| /expenses/edit/<int:exp_id> | expenses_bp.edit | GET, POST |
| /expenses/employees | expenses_bp.employees_list | GET |
| /expenses/employees/<int:emp_id>/generate-salary | expenses_bp.generate_salary | POST |
| /expenses/employees/<int:emp_id>/installments-due | expenses_bp.get_installments_due | GET |
| /expenses/employees/<int:emp_id>/statement | expenses_bp.employee_statement | GET |
| /expenses/employees/add | expenses_bp.add_employee | GET, POST |
| /expenses/employees/delete/<int:emp_id> | expenses_bp.delete_employee | POST |
| /expenses/employees/edit/<int:emp_id> | expenses_bp.edit_employee | GET, POST |
| /expenses/export | expenses_bp.export | GET |
| /expenses/payroll/generate-all | expenses_bp.generate_all_salaries | POST |
| /expenses/payroll/monthly | expenses_bp.payroll_monthly | GET |
| /expenses/payroll/summary | expenses_bp.payroll_summary | GET |
| /expenses/print | expenses_bp.print_list | GET |
| /expenses/quick-partner-service | expenses_bp.quick_partner_service | POST |
| /expenses/quick-partner-service/pay | expenses_bp.quick_partner_service_pay | POST |
| /expenses/quick-supplier-service | expenses_bp.quick_supplier_service | POST |
| /expenses/quick-supplier-service/pay | expenses_bp.quick_supplier_service_pay | POST |
| /expenses/restore/<int:expense_id> | expenses_bp.restore_expense | POST |
| /expenses/salary-receipt/<int:salary_exp_id> | expenses_bp.salary_receipt | GET |
| /expenses/sync-to-ledger | expenses_bp.sync_expenses_to_ledger | POST |
| /expenses/types | expenses_bp.types_list | GET |
| /expenses/types/add | expenses_bp.add_type | GET, POST |
| /expenses/types/delete/<int:type_id> | expenses_bp.delete_type | POST |
| /expenses/types/edit/<int:type_id> | expenses_bp.edit_type | GET, POST |
| /favicon.ico | main.favicon | GET |
| /health/ | health.health_check | GET |
| /health/live | health.liveness | GET |
| /health/metrics | health.metrics | GET |
| /health/ping | health.ping | GET |
| /health/ready | health.readiness | GET |
| /health/status | health.health_check | GET |
| /ledger/ | ledger.index | GET |
| /ledger/account/<account> | ledger.account_ledger | GET |
| /ledger/accounts | ledger.get_accounts | GET |
| /ledger/accounts-summary | ledger.get_accounts_summary | GET |
| /ledger/api/ar_ap_summary | ledger.get_ar_ap_summary | GET |
| /ledger/api/inventory_breakdown | ledger.get_inventory_breakdown | GET |
| /ledger/batch/<int:batch_id> | ledger.get_batch_details | GET |
| /ledger/chart-of-accounts | ledger.chart_of_accounts | GET |
| /ledger/cogs-audit | ledger.cogs_audit_report | GET |
| /ledger/data | ledger.get_ledger_data | GET |
| /ledger/entity | ledger.entity_ledger | GET |
| /ledger/entity-balance-audit | ledger.entity_balance_audit | GET |
| /ledger/entity-balance-audit/auto-fix | ledger.auto_fix_entity_balance_audit | POST |
| /ledger/entity-balance-audit/fix-gl-entities | ledger.fix_gl_entities_for_entity_audit | POST |
| /ledger/entity-balance-audit/recalculate-entities | ledger.recalculate_entities_for_entity_audit | POST |
| /ledger/export | ledger.export_ledger | GET |
| /ledger/manual-entry | ledger.create_manual_entry | POST |
| /ledger/receivables-detailed-summary | ledger.get_receivables_detailed_summary | GET |
| /ledger/receivables-summary | ledger.get_receivables_summary | GET |
| /ledger/statistics | ledger.get_ledger_statistics | GET |
| /ledger/transaction/<int:id> | ledger.view_transaction | GET |
| /ledger/trial-balance | ledger.trial_balance | GET |
| /login | main.login_alias | GET |
| /notes/ | notes_bp.list_notes | GET |
| /notes/<int:note_id> | notes_bp.note_detail | GET |
| /notes/<int:note_id> | notes_bp.update_note | PATCH, POST |
| /notes/<int:note_id>/delete | notes_bp.delete_note | DELETE, POST |
| /notes/<int:note_id>/edit | notes_bp.edit_note | GET |
| /notes/<int:note_id>/toggle-pin | notes_bp.toggle_pin | POST |
| /notes/new | notes_bp.create_note | GET, POST |
| /other-systems/ | other_systems.index | GET |
| /partners/<int:partner_id>/inventory | partner_settlements_bp.partner_inventory | GET |
| /partners/<int:partner_id>/settlement | partner_settlements_bp.partner_settlement | GET |
| /partners/<int:partner_id>/settlement/approve | partner_settlements_bp.approve_settlement | POST |
| /partners/<int:partner_id>/settlements | partner_settlements_bp.partner_settlements_list | GET |
| /partners/<int:partner_id>/settlements/create | partner_settlements_bp.create | POST |
| /partners/<int:partner_id>/settlements/preview | partner_settlements_bp.preview | GET |
| /partners/settlements | partner_settlements_bp.list | GET |
| /partners/settlements/<int:settlement_id> | partner_settlements_bp.show | GET |
| /partners/settlements/<int:settlement_id>/confirm | partner_settlements_bp.confirm | POST |
| /partners/unpriced-items | partner_settlements_bp.check_unpriced_items | GET |
| /parts/ | parts_bp.parts_list | GET |
| /parts/<int:id>/delete | parts_bp.parts_delete | POST |
| /parts/<int:id>/edit | parts_bp.parts_edit | POST |
| /parts/<int:id>/stock | parts_bp.stock_levels | GET |
| /parts/create | parts_bp.parts_create | POST |
| /parts/update-cost | parts_bp.update_part_cost | POST |
| /parts/update-multiple-costs | parts_bp.update_multiple_costs | POST |
| /payments/ | payments.index | GET |
| /payments/<int:payment_id>/split/<int:split_id> | payments.view_payment_split | GET |
| /payments/<int:payment_id>/status | payments.update_payment_status | POST |
| /payments/<int:payment_id>_split_<int:split_id> | payments.view_payment_split_legacy | GET |
| /payments/<string:payment_id> | payments.view_payment | GET |
| /payments/<string:payment_id>/receipt | payments.payment_receipt | GET |
| /payments/<string:payment_id>/receipt/download | payments.download_receipt | GET |
| /payments/api/entities/<entity_type> | payments.get_entities | GET |
| /payments/api/fx-rate | payments.fx_rate_lookup | GET |
| /payments/api/related-party | payments.get_related_party | GET |
| /payments/archive/<int:payment_id> | payments.archive_payment | POST |
| /payments/create | payments.create_payment | GET, POST |
| /payments/entity-fields | payments.entity_fields | GET |
| /payments/entity-search | payments.entity_search | GET |
| /payments/expense/<int:exp_id>/create | payments.create_expense_payment | GET, POST |
| /payments/refund/<int:payment_id> | payments.refund_payment | POST |
| /payments/restore/<int:payment_id> | payments.restore_payment | POST |
| /payments/search-entities | payments.search_entities | GET |
| /payments/shop/checkout | payments.shop_checkout | POST |
| /payments/shop/payment-methods | payments.shop_payment_methods | GET |
| /payments/shop/payment-status/<int:payment_id> | payments.shop_payment_status | GET |
| /payments/shop/process-payment | payments.shop_process_payment | POST |
| /payments/shop/refund | payments.shop_refund | POST |
| /payments/split/<int:split_id>/delete | payments.delete_split | DELETE |
| /payments/split/<int:split_id>/refund | payments.refund_split | POST |
| /permissions/ | permissions.list | GET |
| /permissions/<int:permission_id>/delete | permissions.delete | POST |
| /permissions/<int:permission_id>/edit | permissions.edit | GET, POST |
| /permissions/create | permissions.create | GET, POST |
| /permissions/matrix | permissions.matrix | GET |
| /pricing/ | pricing.index | GET |
| /projects/ | projects.index | GET |
| /projects/<int:id> | projects.view_project | GET |
| /projects/<int:id>/add-cost | projects.add_cost | POST |
| /projects/<int:id>/add-phase | projects.add_phase | POST |
| /projects/<int:id>/add-revenue | projects.add_revenue | POST |
| /projects/<int:project_id>/change-orders | project_advanced.change_orders | GET |
| /projects/<int:project_id>/change-orders/<int:co_id>/approve | project_advanced.approve_change_order | POST |
| /projects/<int:project_id>/change-orders/add | project_advanced.add_change_order | POST |
| /projects/<int:project_id>/dashboard | project_advanced.dashboard | GET |
| /projects/<int:project_id>/evm | project_advanced.earned_value_analysis | GET |
| /projects/<int:project_id>/milestones | project_advanced.milestones | GET |
| /projects/<int:project_id>/milestones/<int:milestone_id>/complete | project_advanced.complete_milestone | POST |
| /projects/<int:project_id>/milestones/add | project_advanced.add_milestone | POST |
| /projects/<int:project_id>/resources | project_advanced.resources | GET |
| /projects/<int:project_id>/resources/add | project_advanced.add_resource | POST |
| /projects/<int:project_id>/risks | project_advanced.risks | GET |
| /projects/<int:project_id>/risks/add | project_advanced.add_risk | POST |
| /projects/<int:project_id>/tasks | project_advanced.tasks | GET |
| /projects/<int:project_id>/tasks/add | project_advanced.add_task | POST |
| /projects/add | projects.add_project | GET, POST |
| /projects/api/dashboard-stats | projects.api_dashboard_stats | GET |
| /projects/dashboard | project_advanced.advanced_dashboard | GET |
| /projects/edit/<int:id> | projects.edit_project | GET, POST |
| /projects/reports/budget-tracking | projects.report_budget_tracking | GET |
| /projects/reports/pnl | projects.report_pnl | GET |
| /projects/reports/profitability | projects.report_profitability | GET |
| /projects/reports/variance | projects.report_variance | GET |
| /recurring/ | recurring.index | GET |
| /recurring/add | recurring.add_template | GET, POST |
| /recurring/delete/<int:template_id> | recurring.delete_template | POST |
| /recurring/edit/<int:template_id> | recurring.edit_template | GET, POST |
| /recurring/generate-now/<int:template_id> | recurring.generate_now | POST |
| /recurring/schedules/<int:template_id> | recurring.view_schedules | GET |
| /recurring/toggle/<int:template_id> | recurring.toggle_template | POST |
| /reports | reports_bp.index | GET |
| /reports/ | reports_bp.universal | GET |
| /reports/ap-aging | reports_bp.ap_aging | GET |
| /reports/api/dynamic | reports_bp.api_dynamic | POST |
| /reports/api/model_fields | reports_bp.model_fields | GET |
| /reports/ar-aging | reports_bp.ar_aging | GET |
| /reports/below_min_stock | reports_bp.below_min_stock_report | GET |
| /reports/cash-flow | reports_bp.cash_flow_report | GET |
| /reports/customer-detail/<int:customer_id> | reports_bp.customer_detail_report | GET |
| /reports/customers | reports_bp.customers_report | GET |
| /reports/customers/advanced | reports_bp.customers_advanced_report | GET |
| /reports/dynamic | reports_bp.dynamic_report | GET, POST |
| /reports/expenses | reports_bp.expenses_report | GET |
| /reports/export/ap_aging.csv | reports_bp.export_ap_aging_csv | GET |
| /reports/export/ar_aging.csv | reports_bp.export_ar_aging_csv | GET |
| /reports/export/dynamic.csv | reports_bp.export_dynamic_csv | POST |
| /reports/financial/ | financial_reports.index | GET |
| /reports/financial/accrue-income-tax | financial_reports.accrue_income_tax | POST |
| /reports/financial/aging-report | financial_reports.aging_report | GET |
| /reports/financial/balance-sheet | financial_reports.balance_sheet | GET |
| /reports/financial/balances-summary | financial_reports.balances_summary | GET |
| /reports/financial/cash-flow | financial_reports.cash_flow | GET |
| /reports/financial/expense-breakdown | financial_reports.expense_breakdown | GET |
| /reports/financial/income-statement | financial_reports.income_statement | GET |
| /reports/financial/profit-trends | financial_reports.profit_trends | GET |
| /reports/financial/receivables-payables | financial_reports.receivables_payables | GET |
| /reports/financial/revenue-by-source | financial_reports.revenue_by_source | GET |
| /reports/financial/trial-balance | financial_reports.trial_balance | GET |
| /reports/financial/validation | financial_reports.validation_report | GET |
| /reports/inventory | reports_bp.inventory | GET |
| /reports/invoices | reports_bp.invoices_report | GET |
| /reports/online | reports_bp.online | GET |
| /reports/partner-detail/<int:partner_id> | reports_bp.partner_detail_report | GET |
| /reports/partners | reports_bp.partners_report | GET |
| /reports/payments-summary | reports_bp.payments_summary | GET |
| /reports/payments-summary-old | reports_bp.payments_summary_old | GET |
| /reports/payments/advanced | reports_bp.payments_advanced_report | GET |
| /reports/preorders | reports_bp.preorders_report | GET |
| /reports/profit-loss | reports_bp.profit_loss_report | GET |
| /reports/sales | reports_bp.sales | GET |
| /reports/sales/advanced | reports_bp.sales_advanced_report | GET |
| /reports/service-reports | reports_bp.service_reports | GET |
| /reports/shipments | reports_bp.shipments | GET |
| /reports/supplier-detail/<int:supplier_id> | reports_bp.supplier_detail_report | GET |
| /reports/suppliers | reports_bp.suppliers_report | GET |
| /reports/top-products | reports_bp.top_products | GET |
| /restore_db | main.restore_db | GET, POST |
| /returns/ | returns.list_returns | GET |
| /returns/<int:return_id> | returns.view_return | GET |
| /returns/<int:return_id>/cancel | returns.cancel_return | POST |
| /returns/<int:return_id>/confirm | returns.confirm_return | POST |
| /returns/<int:return_id>/delete | returns.delete_return | POST |
| /returns/<int:return_id>/edit | returns.edit_return | GET, POST |
| /returns/api/customer/<int:customer_id>/sales | returns.get_customer_sales | GET |
| /returns/api/sale/<int:sale_id>/items | returns.get_sale_items | GET |
| /returns/create | returns.create_return | GET, POST |
| /returns/create/<int:sale_id> | returns.create_return | GET, POST |
| /roles/ | roles.list_roles | GET |
| /roles/<int:role_id>/delete | roles.delete_role | POST |
| /roles/<int:role_id>/edit | roles.edit_role | GET, POST |
| /roles/create | roles.create_role | GET, POST |
| /sales/ | sales_bp.index | GET |
| /sales/ | sales_bp.list_sales | GET |
| /sales/<int:id> | sales_bp.sale_detail | GET |
| /sales/<int:id>/archive | sales_bp.archive_sale | POST |
| /sales/<int:id>/edit | sales_bp.edit_sale | GET, POST |
| /sales/<int:id>/invoice | sales_bp.generate_invoice | GET |
| /sales/<int:id>/payments | sales_bp.sale_payments | GET |
| /sales/<int:id>/receipt | sales_bp.sale_receipt | GET |
| /sales/<int:id>/restore | sales_bp.restore_sale | POST |
| /sales/<int:id>/status/<status> | sales_bp.change_status | POST |
| /sales/dashboard | sales_bp.dashboard | GET |
| /sales/new | sales_bp.create_sale | GET, POST |
| /sales/quick | sales_bp.quick_sell | POST |
| /security/ | security.index | GET |
| /security/advanced-analytics | security.advanced_analytics | GET |
| /security/advanced-check-linking | security.advanced_check_linking | GET, POST |
| /security/api/customers | security.api_get_customers | GET |
| /security/api/indexes/analyze-table | security.api_analyze_table | POST |
| /security/api/indexes/auto-optimize | security.api_auto_optimize_indexes | POST |
| /security/api/indexes/batch-create | security.api_batch_create_indexes | POST |
| /security/api/indexes/clean-and-rebuild | security.api_clean_rebuild_indexes | POST |
| /security/api/indexes/create | security.api_create_index | POST |
| /security/api/indexes/drop | security.api_drop_index | POST |
| /security/api/live-metrics | security.api_live_metrics | GET |
| /security/api/maintenance/analyze | security.api_maintenance_analyze | POST |
| /security/api/maintenance/checkpoint | security.api_maintenance_checkpoint | POST |
| /security/api/maintenance/db-info | security.api_maintenance_db_info | GET |
| /security/api/maintenance/vacuum | security.api_maintenance_vacuum | POST |
| /security/api/saas/invoices | security.api_saas_create_invoice | POST |
| /security/api/saas/invoices/<int:invoice_id>/mark-paid | security.api_saas_mark_paid | POST |
| /security/api/saas/invoices/<int:invoice_id>/pdf | security.api_saas_invoice_pdf | GET |
| /security/api/saas/invoices/<int:invoice_id>/send-reminder | security.api_saas_send_reminder | POST |
| /security/api/saas/plans | security.api_saas_create_plan | POST |
| /security/api/saas/plans/<int:plan_id> | security.api_saas_update_plan | PUT |
| /security/api/saas/subscriptions | security.api_saas_create_subscription | POST |
| /security/api/saas/subscriptions/<int:sub_id> | security.api_saas_get_subscription | GET |
| /security/api/saas/subscriptions/<int:sub_id> | security.api_saas_update_subscription | PUT |
| /security/api/saas/subscriptions/<int:sub_id>/cancel | security.api_saas_cancel_subscription | POST |
| /security/api/saas/subscriptions/<int:sub_id>/renew | security.api_saas_renew_subscription | POST |
| /security/api/security-audit/stats | security.api_security_audit_stats | GET |
| /security/api/system-accounts/change-password | security.api_system_account_change_password | POST |
| /security/api/system-constants | security.api_system_constants | GET |
| /security/api/users/<int:user_id>/activity-history | security.api_user_activity_history | GET |
| /security/api/users/<int:user_id>/details | security.api_user_details | GET |
| /security/api/users/bulk-operation | security.api_users_bulk_operation | POST |
| /security/audit-log | security.audit_log_viewer | GET |
| /security/audit-log/<int:log_id> | security.audit_log_detail | GET |
| /security/block-country | security.block_country | GET, POST |
| /security/block-ip | security.block_ip | GET, POST |
| /security/block-user/<int:user_id> | security.block_user | POST |
| /security/blocked-countries | security.blocked_countries | GET |
| /security/blocked-ips | security.blocked_ips | GET |
| /security/card-vault | security.card_vault | GET |
| /security/code-editor | security.theme_editor | GET, POST |
| /security/create-user | security.create_user | POST |
| /security/dark-mode-settings | security.dark_mode_settings | GET, POST |
| /security/data-export | security.data_export | GET |
| /security/data-quality-center | security.data_quality_center | GET, POST |
| /security/database-manager | security.database_manager | GET, POST |
| /security/db-editor/add-column/<table_name> | security.db_add_column | POST |
| /security/db-editor/add-row/<table_name> | security.db_add_row | POST |
| /security/db-editor/bulk-update/<table_name> | security.db_bulk_update | POST |
| /security/db-editor/delete-column/<table_name> | security.db_delete_column | POST |
| /security/db-editor/delete-row/<table_name>/<row_id> | security.db_delete_row | POST |
| /security/db-editor/edit-row/<table_name>/<int:row_id> | security.db_edit_row | POST |
| /security/db-editor/fill-missing/<table_name> | security.db_fill_missing | POST |
| /security/db-editor/schema/<table_name> | security.db_schema_editor | GET |
| /security/db-editor/update-cell/<table_name> | security.db_update_cell | POST |
| /security/delete-user/<int:user_id> | security.delete_user | POST |
| /security/email-manager | security.email_manager | GET, POST |
| /security/emergency-tools | security.emergency_tools | GET |
| /security/emergency/clear-cache | security.clear_system_cache | POST |
| /security/emergency/kill-sessions | security.kill_all_sessions | POST |
| /security/emergency/maintenance-mode | security.toggle_maintenance_mode | POST |
| /security/expenses-control/ | security_expenses.control_panel | GET |
| /security/expenses-control/library | security_expenses.api_field_library | GET |
| /security/expenses-control/library/custom | security_expenses.api_add_custom_field | POST |
| /security/expenses-control/templates | security_expenses.api_create_template | POST |
| /security/expenses-control/templates/<string:template_id> | security_expenses.api_delete_template | DELETE |
| /security/expenses-control/templates/<string:template_id>/apply | security_expenses.api_apply_template | POST |
| /security/expenses-control/types/<int:type_id>/bulk | security_expenses.api_bulk_update | POST |
| /security/expenses-control/types/<int:type_id>/fields | security_expenses.api_update_field_status | POST |
| /security/expenses-control/types/<int:type_id>/ledger | security_expenses.api_update_ledger | POST |
| /security/export-table/<table_name> | security.export_table_csv | GET |
| /security/force-reset-password/<int:user_id> | security.force_reset_password | POST |
| /security/grafana-setup | security.grafana_setup | GET |
| /security/help | security.help_page | GET |
| /security/impersonate/<int:user_id> | security.impersonate_user | POST |
| /security/index-old | security.index_old | GET |
| /security/integration-stats | security.integration_stats | GET |
| /security/integrations | security.integrations | GET, POST |
| /security/invoice-designer | security.invoice_designer | GET, POST |
| /security/ledger-control/ | ledger_control.index | GET |
| /security/ledger-control/accounts | ledger_control.accounts_management | GET |
| /security/ledger-control/accounts/<int:account_id>/delete | ledger_control.delete_account | POST |
| /security/ledger-control/accounts/<int:account_id>/update | ledger_control.update_account | POST |
| /security/ledger-control/accounts/create | ledger_control.create_account | POST |
| /security/ledger-control/api/account-balance/<account_code> | ledger_control.get_account_balance | GET |
| /security/ledger-control/backup | ledger_control.backup_ledger | POST |
| /security/ledger-control/backup-old | ledger_control.backup_ledger_old | POST |
| /security/ledger-control/batches/<int:batch_id> | ledger_control.get_batch_by_id | GET |
| /security/ledger-control/batches/<int:batch_id>/update | ledger_control.update_batch | POST |
| /security/ledger-control/batches/all | ledger_control.get_all_batches | GET |
| /security/ledger-control/cleanup | ledger_control.cleanup_old_entries | POST |
| /security/ledger-control/entries | ledger_control.entries_management | GET |
| /security/ledger-control/entries/<int:entry_id>/void | ledger_control.void_entry | POST |
| /security/ledger-control/fix-cashed-checks-balance | ledger_control.fix_cashed_checks_balance | POST |
| /security/ledger-control/health-check | ledger_control.health_check | GET |
| /security/ledger-control/operations/approve-batch/<int:batch_id> | ledger_control.approve_batch | POST |
| /security/ledger-control/operations/batch/<int:batch_id>/edit | ledger_control.get_batch_for_edit | GET |
| /security/ledger-control/operations/batch/<int:batch_id>/link-entity | ledger_control.link_batch_to_entity | POST |
| /security/ledger-control/operations/batch/<int:batch_id>/update-full | ledger_control.update_batch_full | POST |
| /security/ledger-control/operations/closing-entries/generate | ledger_control.generate_closing_entries | POST |
| /security/ledger-control/operations/closing-entries/post | ledger_control.post_closing_entries | POST |
| /security/ledger-control/operations/entities/search | ledger_control.search_entities | GET |
| /security/ledger-control/operations/fiscal-periods/api | ledger_control.get_fiscal_periods | GET |
| /security/ledger-control/operations/reject-batch/<int:batch_id> | ledger_control.reject_batch | POST |
| /security/ledger-control/operations/reverse-entry/<int:batch_id> | ledger_control.reverse_entry | POST |
| /security/ledger-control/operations/review-queue | ledger_control.review_queue | GET |
| /security/ledger-control/recalculate-balances | ledger_control.recalculate_all_balances | POST |
| /security/ledger-control/reports | ledger_control.reports_management | GET |
| /security/ledger-control/settings | ledger_control.settings_management | GET |
| /security/ledger-control/settings/update | ledger_control.update_settings | POST |
| /security/ledger-control/statistics | ledger_control.get_advanced_statistics | GET |
| /security/ledger-control/sync-checks | ledger_control.sync_payments_checks | POST |
| /security/ledger-control/validate | ledger_control.validate_entries | GET |
| /security/ledger-control/verify-customer-balances | ledger_control.verify_customer_balances | POST |
| /security/live-monitoring | security.live_monitoring | GET |
| /security/logo-manager | security.logo_manager | GET, POST |
| /security/monitoring-dashboard | security.monitoring_dashboard | GET |
| /security/notifications | security.notifications_log | GET |
| /security/notifications/test | security.test_notification | POST |
| /security/performance-monitor | security.performance_monitor | GET |
| /security/permissions-manager | security.permissions_manager | GET, POST |
| /security/prometheus-metrics | security.prometheus_metrics | GET |
| /security/reports-center | security.reports_center | GET |
| /security/saas-manager | security.saas_manager | GET |
| /security/save-integration | security.save_integration | POST |
| /security/security-audit-report | security.security_audit_report | GET |
| /security/security-center | security.security_center | GET |
| /security/send-test-message/<integration_type> | security.send_test_message | POST |
| /security/settings | security.system_settings | GET, POST |
| /security/settings-center | security.settings_center | GET, POST |
| /security/sitemap | security.sitemap | GET |
| /security/stop-impersonate | security.stop_impersonate | POST |
| /security/system-branding | security.system_branding | GET, POST |
| /security/system-cleanup | security.system_cleanup | GET, POST |
| /security/system-settings | security.system_settings | GET, POST |
| /security/tax-reports | security.tax_reports | GET |
| /security/tax-reports/export/<period> | security.export_tax_report | GET |
| /security/tax-reports/reconcile/<period> | security.reconcile_tax_report | POST |
| /security/test-integration/<integration_type> | security.test_integration | POST |
| /security/theme-editor | security.theme_editor | GET, POST |
| /security/toggle-user/<int:user_id> | security.toggle_user_status | POST |
| /security/toggle_user_status/<int:user_id> | security.toggle_user_status | POST |
| /security/tools-center | security.tools_center | GET |
| /security/ultimate-control | security.ultimate_control | GET |
| /security/unblock-ip/<ip> | security.unblock_ip | POST |
| /security/update-user-permissions/<int:user_id> | security.update_user_extra_permissions | POST |
| /security/update-user-role/<int:user_id> | security.update_user_role | POST |
| /security/user-control | security.user_control | GET |
| /security/users-center | security.users_center | GET, POST |
| /service/ | service.list_requests | GET |
| /service/<int:rid> | service.view_request | GET |
| /service/<int:rid>/<action> | service.toggle_service | POST |
| /service/<int:rid>/delete | service.delete_request | POST |
| /service/<int:rid>/diagnosis | service.update_diagnosis | POST |
| /service/<int:rid>/discount_tax | service.update_discount_tax | POST |
| /service/<int:rid>/invoice | service.create_invoice | GET, POST |
| /service/<int:rid>/parts/add | service.add_part | POST |
| /service/<int:rid>/payments/add | service.add_payment | GET, POST |
| /service/<int:rid>/pdf | service.export_pdf | GET |
| /service/<int:rid>/receipt | service.view_receipt | GET |
| /service/<int:rid>/receipt/download | service.download_receipt | GET |
| /service/<int:rid>/report | service.service_report | GET |
| /service/<int:rid>/tasks/add | service.add_task | POST |
| /service/analytics | service.analytics | GET |
| /service/api/options | service.api_service_options | GET |
| /service/api/priorities | service.api_service_priorities | GET |
| /service/api/requests | service.api_service_requests | GET |
| /service/api/statuses | service.api_service_statuses | GET |
| /service/archive/<int:id> | service.archive_service | POST |
| /service/dashboard | service.dashboard | GET |
| /service/export/csv | service.export_requests_csv | GET |
| /service/list | service.list_requests | GET |
| /service/new | service.create_request | GET, POST |
| /service/parts/<int:pid>/delete | service.delete_part | POST |
| /service/restore/<int:id> | service.restore_service | POST |
| /service/search | service.search_requests | GET |
| /service/tasks/<int:tid>/delete | service.delete_task | POST |
| /shipments/ | shipments_bp.list_shipments | GET |
| /shipments/ | shipments_bp.shipments | GET |
| /shipments/<int:id> | shipments_bp.shipment_detail | GET |
| /shipments/<int:id>/cancel | shipments_bp.cancel_shipment | POST |
| /shipments/<int:id>/delete | shipments_bp.delete_shipment | POST |
| /shipments/<int:id>/edit | shipments_bp.edit_shipment | GET, POST |
| /shipments/<int:id>/mark-arrived | shipments_bp.mark_arrived | POST |
| /shipments/<int:id>/mark-delivered | shipments_bp.mark_delivered | POST |
| /shipments/<int:id>/mark-in-customs | shipments_bp.mark_in_customs | POST |
| /shipments/<int:id>/mark-in-transit | shipments_bp.mark_in_transit | POST |
| /shipments/<int:id>/mark-returned | shipments_bp.mark_returned | POST |
| /shipments/<int:id>/update-delivery-attempt | shipments_bp.update_delivery_attempt | POST |
| /shipments/archive/<int:shipment_id> | archive_routes.archive_shipment | POST |
| /shipments/create | shipments_bp.create_shipment | GET, POST |
| /shipments/data | shipments_bp.shipments_data | GET |
| /shop/ | shop.catalog | GET |
| /shop/admin/categories/quick_create | shop.admin_categories_quick_create | POST |
| /shop/admin/preorders | shop.admin_preorders | GET |
| /shop/admin/products | shop.admin_products | GET |
| /shop/admin/products/<int:pid>/delete | shop.admin_product_delete | POST |
| /shop/admin/products/<int:pid>/edit | shop.admin_product_edit | GET, POST |
| /shop/admin/products/<int:pid>/toggle_active | shop.admin_product_toggle_active | POST |
| /shop/admin/products/<int:pid>/update_fields | shop.admin_product_update_fields | POST |
| /shop/admin/products/new | shop.admin_product_new | GET, POST |
| /shop/api/product/<int:pid> | shop.api_product_detail | GET |
| /shop/api/products | shop.api_products | GET |
| /shop/archive-preorder/<int:preorder_id> | shop.archive_preorder | POST |
| /shop/cart | shop.cart | GET |
| /shop/cart/add/<int:product_id> | shop.add_to_cart | POST |
| /shop/cart/remove/<int:item_id> | shop.remove_from_cart | POST |
| /shop/cart/update/<int:item_id> | shop.update_cart_item | POST |
| /shop/checkout | shop.checkout | GET, POST |
| /shop/order | shop.place_order | POST |
| /shop/payments/<int:op_id>/refund | shop.refund_payment | POST |
| /shop/preorder/<int:preorder_id>/cancel | shop.cancel_preorder | POST |
| /shop/preorder/<int:preorder_id>/receipt | shop.preorder_receipt | GET |
| /shop/preorders | shop.preorder_list | GET |
| /shop/product/<int:product_id> | shop.product_detail | GET |
| /shop/products | shop.products | GET |
| /shop/webhook/<gateway> | shop.gateway_webhook | POST |
| /suppliers/<int:supplier_id>/inventory | supplier_settlements_bp.supplier_inventory | GET |
| /suppliers/<int:supplier_id>/settlement | supplier_settlements_bp.supplier_settlement | GET |
| /suppliers/<int:supplier_id>/settlement/approve | supplier_settlements_bp.approve_settlement | POST |
| /suppliers/<int:supplier_id>/settlements/create | supplier_settlements_bp.create | POST |
| /suppliers/<int:supplier_id>/settlements/preview | supplier_settlements_bp.preview | GET |
| /suppliers/exchange-transaction/<int:tx_id>/update-price | supplier_settlements_bp.update_exchange_transaction_price | POST |
| /suppliers/settlements | supplier_settlements_bp.list | GET |
| /suppliers/settlements/<int:settlement_id> | supplier_settlements_bp.show | GET |
| /suppliers/settlements/<int:settlement_id>/confirm | supplier_settlements_bp.confirm | POST |
| /suppliers/settlements/<int:settlement_id>/show | supplier_settlements_bp.show_settlement | GET |
| /suppliers/settlements/<int:settlement_id>/void | supplier_settlements_bp.void | POST |
| /suppliers/settlements/approved | supplier_settlements_bp.approved_settlements_list | GET |
| /suppliers/unpriced-items | supplier_settlements_bp.check_unpriced_items | GET |
| /system/performance/ | performance_bp.index | GET |
| /system/performance/data | performance_bp.data | GET |
| /system/performance/snapshot | performance_bp.snapshot | GET |
| /toggle-automated-backup | main.toggle_automated_backup | POST |
| /user-guide/ | user_guide.index | GET |
| /users/ | users_bp.list_users | GET |
| /users/<int:user_id> | users_bp.user_detail | GET |
| /users/<int:user_id>/delete | users_bp.delete_user | POST |
| /users/<int:user_id>/edit | users_bp.edit_user | GET, POST |
| /users/api | users_bp.api_users | GET |
| /users/change-password | users_bp.change_password | GET, POST |
| /users/create | users_bp.create_user | GET, POST |
| /users/edit-profile | users_bp.edit_profile | GET, POST |
| /users/profile | users_bp.profile | GET |
| /users/registered-customers | users_bp.registered_customers | GET |
| /validation/accounting/ | accounting_validation.index | GET |
| /validation/accounting/account-consistency | accounting_validation.account_consistency | GET |
| /validation/accounting/balance-check | accounting_validation.balance_check | GET |
| /validation/accounting/entity-balance-verification | accounting_validation.entity_balance_verification | GET |
| /validation/accounting/fix-unbalanced-batches | accounting_validation.fix_unbalanced_batches | GET |
| /validation/accounting/periodic-audit | accounting_validation.periodic_audit | GET |
| /validation/accounting/transaction-integrity | accounting_validation.transaction_integrity | GET |
| /vendors/partners | vendors_bp.partners_list | GET |
| /vendors/partners/<int:id>/delete | vendors_bp.partners_delete | POST |
| /vendors/partners/<int:id>/edit | vendors_bp.partners_edit | GET, POST |
| /vendors/partners/<int:partner_id>/smart-settlement | vendors_bp.partner_smart_settlement | GET |
| /vendors/partners/<int:partner_id>/statement | vendors_bp.partners_statement | GET |
| /vendors/partners/archive/<int:partner_id> | vendors_bp.archive_partner | POST |
| /vendors/partners/balances/recalculate | vendors_bp.partners_recalculate_balances | POST |
| /vendors/partners/new | vendors_bp.partners_create | GET, POST |
| /vendors/partners/restore/<int:partner_id> | vendors_bp.restore_partner | POST |
| /vendors/suppliers | vendors_bp.suppliers_list | GET |
| /vendors/suppliers/<int:id>/delete | vendors_bp.suppliers_delete | POST |
| /vendors/suppliers/<int:id>/edit | vendors_bp.suppliers_edit | GET, POST |
| /vendors/suppliers/<int:supplier_id>/smart-settlement | vendors_bp.supplier_smart_settlement | GET |
| /vendors/suppliers/<int:supplier_id>/statement | vendors_bp.suppliers_statement | GET |
| /vendors/suppliers/archive/<int:supplier_id> | vendors_bp.archive_supplier | POST |
| /vendors/suppliers/balances/recalculate | vendors_bp.suppliers_recalculate_balances | POST |
| /vendors/suppliers/new | vendors_bp.suppliers_create | GET, POST |
| /vendors/suppliers/restore/<int:supplier_id> | vendors_bp.restore_supplier | POST |
| /warehouses/ | warehouse_bp.list | GET |
| /warehouses/<int:id>/add-product | warehouse_bp.add_product | GET, POST |
| /warehouses/<int:id>/import | warehouse_bp.import_products | GET, POST |
| /warehouses/<int:id>/import/commit | warehouse_bp.import_commit | POST |
| /warehouses/<int:id>/import/preview | warehouse_bp.import_preview | GET, POST |
| /warehouses/<int:id>/imports | warehouse_bp.import_runs | GET |
| /warehouses/<int:id>/products | warehouse_bp.products | GET |
| /warehouses/<int:id>/shipments/create | warehouse_bp.create_warehouse_shipment | GET |
| /warehouses/<int:id>/transfer | warehouse_bp.transfer_inline | POST |
| /warehouses/<int:id>/transfers | warehouse_bp.transfers | GET |
| /warehouses/<int:id>/transfers/create | warehouse_bp.create_transfer | GET, POST |
| /warehouses/<int:warehouse_id> | warehouse_bp.detail | GET |
| /warehouses/<int:warehouse_id>/delete | warehouse_bp.delete | POST |
| /warehouses/<int:warehouse_id>/edit | warehouse_bp.edit | GET, POST |
| /warehouses/<int:warehouse_id>/exchange | warehouse_bp.ajax_exchange | POST |
| /warehouses/<int:warehouse_id>/partner-shares | warehouse_bp.partner_shares | GET, POST |
| /warehouses/<int:warehouse_id>/pay | warehouse_bp.pay_warehouse | POST |
| /warehouses/<int:warehouse_id>/preview | warehouse_bp.preview_inventory | GET |
| /warehouses/<int:warehouse_id>/preview/update | warehouse_bp.preview_update | POST |
| /warehouses/<int:warehouse_id>/products/<int:product_id> | warehouse_bp.update_product_inline | PATCH, POST |
| /warehouses/<int:warehouse_id>/stock | warehouse_bp.ajax_update_stock | POST |
| /warehouses/<int:warehouse_id>/transfer | warehouse_bp.ajax_transfer | POST |
| /warehouses/api/add_customer | warehouse_bp.api_add_customer | POST |
| /warehouses/api/add_partner | warehouse_bp.api_add_partner | POST |
| /warehouses/api/add_supplier | warehouse_bp.api_add_supplier | POST |
| /warehouses/api/apply_online_defaults | warehouse_bp.api_apply_online_defaults | POST |
| /warehouses/api/partners/list | warehouse_bp.api_partners_list | GET |
| /warehouses/api/prepare_online_fields | warehouse_bp.api_prepare_online_fields | GET |
| /warehouses/api/products/<int:product_id>/partners | warehouse_bp.api_product_partners_add | POST |
| /warehouses/api/products/<int:product_id>/partners | warehouse_bp.api_product_partners_list | GET |
| /warehouses/api/products/<int:product_id>/partners/<int:share_id> | warehouse_bp.api_product_partners_delete | DELETE |
| /warehouses/api/products/<int:product_id>/partners/<int:share_id> | warehouse_bp.api_product_partners_update | PUT |
| /warehouses/api/products/<int:product_id>/suppliers | warehouse_bp.api_product_suppliers_list | GET |
| /warehouses/api/products/<int:product_id>/suppliers | warehouse_bp.api_product_suppliers_update | POST |
| /warehouses/api/suppliers/list | warehouse_bp.api_suppliers_list | GET |
| /warehouses/api/upload_product_image | warehouse_bp.api_upload_product_image | POST |
| /warehouses/api/warehouse-info | warehouse_bp.api_warehouse_info | GET |
| /warehouses/create | warehouse_bp.create | GET, POST |
| /warehouses/goto/product-card | warehouse_bp.goto_product_card | GET |
| /warehouses/goto/warehouse-products | warehouse_bp.goto_warehouse_products | GET |
| /warehouses/imports/<int:run_id>/download | warehouse_bp.import_run_download | GET |
| /warehouses/inventory | warehouse_bp.inventory_summary | GET |
| /warehouses/parts/<int:product_id> | warehouse_bp.product_card | GET |
| /warehouses/preorders | warehouse_bp.preorders_list | GET |
| /warehouses/preorders/<int:preorder_id> | warehouse_bp.preorder_detail | GET |
| /warehouses/preorders/<int:preorder_id>/cancel | warehouse_bp.preorder_cancel | POST |
| /warehouses/preorders/<int:preorder_id>/convert-to-sale | warehouse_bp.preorder_convert_to_sale | POST |
| /warehouses/preorders/<int:preorder_id>/fulfill | warehouse_bp.preorder_fulfill | POST |
| /warehouses/preorders/<int:preorder_id>/mark-fulfilled | warehouse_bp.preorder_mark_fulfilled | POST |
| /warehouses/preorders/create | warehouse_bp.preorder_create | GET, POST |
| /warehouses/transaction/<int:id> | warehouse_bp.transaction_detail | GET |
| /workflows/ | workflows.index | GET |
| /workflows/api/start | workflows.api_start_workflow | POST |
| /workflows/definitions | workflows.definitions | GET |
| /workflows/definitions/<int:id>/edit | workflows.edit_definition | GET, POST |
| /workflows/definitions/<int:id>/toggle | workflows.toggle_definition | POST |
| /workflows/definitions/add | workflows.add_definition | GET, POST |
| /workflows/instances | workflows.instances | GET |
| /workflows/instances/<int:id> | workflows.view_instance | GET |
| /workflows/instances/<int:id>/cancel | workflows.cancel_instance | POST |
| /workflows/instances/<int:id>/execute | workflows.execute_action | POST |
| /workflows/my-pending | workflows.my_pending | GET |
| /workflows/reports/cost-center-analysis | workflows.report_cost_center_analysis | GET |
| /workflows/reports/performance | workflows.report_performance | GET |
| /workflows/reports/summary | workflows.report_summary | GET |