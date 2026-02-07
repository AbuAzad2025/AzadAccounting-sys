from extensions import socketio, cache

def emit_balance_update(entity_type, entity_id, balance):
    try:
        cache.delete(f'{entity_type}_balance_{entity_id}')
        cache.delete(f'entity_balance_{(entity_type or "").upper()}_{entity_id}')
        cache.delete('balances_summary_v1')
        cache.delete('suppliers_summary_v2')
        cache.delete('partners_summary_v2')
        cache.delete('customers_summary_v2')
        cache.delete('ledger_total_customer_balance')
        cache.delete('ledger_total_supplier_balance')
        cache.delete('ledger_total_partner_balance')
        cache.delete('dashboard_balance_customers')
        cache.delete('dashboard_balance_suppliers')
        cache.delete('dashboard_balance_partners')
        cache.delete('dashboard_partner_balance')
        
        socketio.emit('balance_updated', {
            'entity_type': entity_type,
            'entity_id': entity_id,
            'balance': float(balance)
        })

        try:
            from extensions import db
            from sqlalchemy import func
            from models import Supplier, Partner, Customer

            suppliers_count = db.session.query(func.count(Supplier.id)).filter(Supplier.is_archived.is_(False)).scalar() or 0
            partners_count = db.session.query(func.count(Partner.id)).filter(Partner.is_archived.is_(False)).scalar() or 0
            customers_count = db.session.query(func.count(Customer.id)).filter(Customer.is_archived.is_(False)).scalar() or 0

            suppliers_total = db.session.query(func.coalesce(func.sum(Supplier.current_balance), 0)).filter(Supplier.is_archived.is_(False)).scalar() or 0
            partners_total = db.session.query(func.coalesce(func.sum(Partner.current_balance), 0)).filter(Partner.is_archived.is_(False)).scalar() or 0
            customers_total = db.session.query(func.coalesce(func.sum(Customer.current_balance), 0)).filter(Customer.is_archived.is_(False)).scalar() or 0

            socketio.emit('balances_summary_updated', {
                'suppliers': {'count': int(suppliers_count), 'total_balance': float(suppliers_total)},
                'partners': {'count': int(partners_count), 'total_balance': float(partners_total)},
                'customers': {'count': int(customers_count), 'total_balance': float(customers_total)},
            })
        except Exception:
            pass
    except Exception as e:
        from flask import current_app
        try:
            current_app.logger.warning(f'Failed to emit balance update: {e}')
        except Exception:
            pass

def clear_all_balance_cache():
    try:
        cache.delete('balances_summary_v1')
        cache.delete('suppliers_summary_v2')
        cache.delete('partners_summary_v2')
        cache.delete('customers_summary_v2')
        cache.delete('ledger_total_customer_balance')
        cache.delete('ledger_total_supplier_balance')
        cache.delete('ledger_total_partner_balance')
        cache.delete('dashboard_balance_customers')
        cache.delete('dashboard_balance_suppliers')
        cache.delete('dashboard_balance_partners')
        cache.delete('dashboard_partner_balance')
    except Exception:
        pass

