from decimal import Decimal
from sqlalchemy import func, or_, and_
from sqlalchemy.orm import object_session, selectinload
from models import (
    Customer, Sale, SaleReturn, Invoice, ServiceRequest, PreOrder, OnlinePreOrder,
    Payment, PaymentSplit, Check, PaymentDirection, PaymentStatus, PaymentMethod, Expense, ExpenseType
)
from extensions import db


def convert_amount(amount, from_currency, to_currency, date=None):
    from models import convert_amount as _convert_amount
    return _convert_amount(amount, from_currency, to_currency, date)


def calculate_customer_balance_components(customer_id, session=None):
    """حساب جميع مكونات رصيد العميل"""
    if not session:
        session = db.session
    
    try:
        from sqlalchemy.orm import Session
        from sqlalchemy import text as sa_text
        if isinstance(session, Session):
            try:
                session.execute(sa_text("SELECT 1"))
            except Exception:
                from sqlalchemy.orm import sessionmaker
                session = sessionmaker(bind=db.engine)()
    except Exception:
        pass
    
    customer = session.get(Customer, customer_id)
    if not customer:
        return None
    
    result = {
        'sales_balance': Decimal('0.00'),
        'returns_balance': Decimal('0.00'),
        'invoices_balance': Decimal('0.00'),
        'services_balance': Decimal('0.00'),
        'preorders_balance': Decimal('0.00'),
        'online_orders_balance': Decimal('0.00'),
        'payments_in_balance': Decimal('0.00'),
        'payments_out_balance': Decimal('0.00'),
        'checks_in_balance': Decimal('0.00'),
        'checks_out_balance': Decimal('0.00'),
        'returned_checks_in_balance': Decimal('0.00'),
        'returned_checks_out_balance': Decimal('0.00'),
        'expenses_balance': Decimal('0.00'),
        'service_expenses_balance': Decimal('0.00'),
    }
    
    try:
        ils_sales_sum = session.query(func.coalesce(func.sum(Sale.total_amount), 0)).filter(
            Sale.customer_id == customer_id,
            Sale.status == 'CONFIRMED',
            Sale.currency == 'ILS'
        ).scalar() or 0
        result['sales_balance'] += Decimal(str(ils_sales_sum))
        
        other_currency_sales = session.query(
            func.sum(Sale.total_amount), Sale.currency, func.date(Sale.sale_date)
        ).filter(
            Sale.customer_id == customer_id,
            Sale.status == 'CONFIRMED',
            Sale.currency != 'ILS'
        ).group_by(Sale.currency, func.date(Sale.sale_date)).all()
        for total_amt, currency, date_val in other_currency_sales:
            try:
                result['sales_balance'] += convert_amount(Decimal(str(total_amt or 0)), currency, "ILS", date_val)
            except Exception:
                try:
                    session.rollback()
                except Exception:
                    pass
        
        ils_returns_sum = session.query(func.coalesce(func.sum(SaleReturn.total_amount), 0)).filter(
            SaleReturn.customer_id == customer_id,
            SaleReturn.status == 'CONFIRMED',
            SaleReturn.currency == 'ILS'
        ).scalar() or 0
        result['returns_balance'] += Decimal(str(ils_returns_sum))
        
        other_currency_returns = session.query(
            func.sum(SaleReturn.total_amount), SaleReturn.currency, func.date(SaleReturn.created_at)
        ).filter(
            SaleReturn.customer_id == customer_id,
            SaleReturn.status == 'CONFIRMED',
            SaleReturn.currency != 'ILS'
        ).group_by(SaleReturn.currency, func.date(SaleReturn.created_at)).all()
        for total_amt, currency, date_val in other_currency_returns:
            try:
                result['returns_balance'] += convert_amount(Decimal(str(total_amt or 0)), currency, "ILS", date_val)
            except Exception:
                try:
                    session.rollback()
                except Exception:
                    pass
        
        ils_invoices_sum = session.query(func.coalesce(func.sum(Invoice.total_amount), 0)).filter(
            Invoice.customer_id == customer_id,
            Invoice.cancelled_at.is_(None),
            Invoice.currency == 'ILS'
        ).scalar() or 0
        result['invoices_balance'] += Decimal(str(ils_invoices_sum))
        
        other_currency_invoices = session.query(
            func.sum(Invoice.total_amount), Invoice.currency, func.date(Invoice.invoice_date)
        ).filter(
            Invoice.customer_id == customer_id,
            Invoice.cancelled_at.is_(None),
            Invoice.currency != 'ILS'
        ).group_by(Invoice.currency, func.date(Invoice.invoice_date)).all()
        for total_amt, currency, date_val in other_currency_invoices:
            try:
                result['invoices_balance'] += convert_amount(Decimal(str(total_amt or 0)), currency, "ILS", date_val)
            except Exception:
                try:
                    session.rollback()
                except Exception:
                    pass
        
        # تحسين: حساب مجموع الخدمات بعملة ILS مباشرة من قاعدة البيانات
        from sqlalchemy import case
        base_expr = func.coalesce(ServiceRequest.parts_total, 0) + func.coalesce(ServiceRequest.labor_total, 0) - func.coalesce(ServiceRequest.discount_total, 0)
        base_safe = case(
            (base_expr < 0, 0),
            else_=base_expr
        )
        total_expr = base_safe * (1 + func.coalesce(ServiceRequest.tax_rate, 0) / 100.0)
        
        ils_services_sum = session.query(func.sum(total_expr)).filter(
            ServiceRequest.customer_id == customer_id,
            ServiceRequest.currency == 'ILS'
        ).scalar() or 0
        result['services_balance'] += Decimal(str(ils_services_sum))
        
        other_currency_services = session.query(
            func.sum(total_expr), ServiceRequest.currency, func.date(ServiceRequest.received_at)
        ).filter(
            ServiceRequest.customer_id == customer_id,
            ServiceRequest.currency != 'ILS'
        ).group_by(ServiceRequest.currency, func.date(ServiceRequest.received_at)).all()
        
        for total_amt, currency, date_val in other_currency_services:
            try:
                result['services_balance'] += convert_amount(Decimal(str(total_amt or 0)), currency, "ILS", date_val)
            except Exception:
                try:
                    session.rollback()
                except Exception:
                    pass
        
        result['preorders_balance'] = Decimal('0.00')
        
        ils_online_orders_sum = session.query(func.coalesce(func.sum(OnlinePreOrder.total_amount), 0)).filter(
            OnlinePreOrder.customer_id == customer_id,
            OnlinePreOrder.payment_status != 'CANCELLED',
            OnlinePreOrder.currency == 'ILS'
        ).scalar() or 0
        result['online_orders_balance'] += Decimal(str(ils_online_orders_sum))
        
        other_currency_online_orders = session.query(
            func.sum(OnlinePreOrder.total_amount), OnlinePreOrder.currency, func.date(OnlinePreOrder.created_at)
        ).filter(
            OnlinePreOrder.customer_id == customer_id,
            OnlinePreOrder.payment_status != 'CANCELLED',
            OnlinePreOrder.currency != 'ILS'
        ).group_by(OnlinePreOrder.currency, func.date(OnlinePreOrder.created_at)).all()
        for total_amt, currency, date_val in other_currency_online_orders:
            try:
                result['online_orders_balance'] += convert_amount(Decimal(str(total_amt or 0)), currency, "ILS", date_val)
            except Exception:
                try:
                    session.rollback()
                except Exception:
                    pass
        
        # تحسين: استعلام واحد لجلب جميع الدفعات الواردة
        payments_in_all = session.query(Payment).filter(
            Payment.customer_id == customer_id,
            Payment.direction == 'IN',
            Payment.status.in_(['COMPLETED', 'PENDING']),
            Payment.expense_id.is_(None)
        ).options(selectinload(Payment.splits), selectinload(Payment.related_check)).all()
        
        for p in payments_in_all:
            splits = p.splits
            
            if splits:
                total_splits = Decimal('0.00')
                
                # التحقق من الشيكات المرتدة المرتبطة بالدفعات المقسمة
                payment_checks = p.related_check
                
                returned_check_amounts = {}
                for check in payment_checks:
                    if check.status in ['RETURNED', 'BOUNCED']:
                        if check.reference_number and 'PMT-SPLIT-' in check.reference_number:
                            try:
                                split_id = int(check.reference_number.split('PMT-SPLIT-')[1].split('-')[0])
                                returned_check_amounts[split_id] = Decimal(str(check.amount or 0))
                            except:
                                pass
                        elif check.check_number:
                            for split in splits:
                                split_details = split.details or {}
                                if isinstance(split_details, str):
                                    try:
                                        import json
                                        split_details = json.loads(split_details)
                                    except:
                                        split_details = {}
                                if split_details.get('check_number') == check.check_number:
                                    returned_check_amounts[split.id] = Decimal(str(check.amount or 0))
                                    break
                
                for split in splits:
                    split_amt = Decimal(str(split.amount or 0))
                    split_converted_amt = Decimal(str(getattr(split, 'converted_amount', 0) or 0))
                    split_converted_currency = (getattr(split, 'converted_currency', None) or split.currency or 'ILS').upper()
                    
                    if split_converted_amt > 0 and split_converted_currency == 'ILS':
                        total_splits += split_converted_amt
                    elif split.currency == "ILS":
                        total_splits += split_amt
                    else:
                        try:
                            total_splits += convert_amount(split_amt, split.currency, "ILS", p.payment_date)
                        except Exception:
                            try:
                                session.rollback()
                            except Exception:
                                pass
                
                amt = total_splits
            else:
                amt = Decimal(str(p.total_amount or 0))
            
            if p.currency == "ILS":
                result['payments_in_balance'] += amt
            else:
                try:
                    result['payments_in_balance'] += convert_amount(amt, p.currency, "ILS", p.payment_date)
                except Exception:
                    try:
                        session.rollback()
                    except Exception:
                        pass
        
        # تم دمج منطق active_preorders في الاستعلام العام للدفعات لأنه يجلب جميع الدفعات الواردة بما فيها دفعات الحجوزات

        
        ils_manual_checks_in_sum = session.query(func.coalesce(func.sum(Check.amount), 0)).filter(
            Check.customer_id == customer_id,
            Check.payment_id.is_(None),
            Check.direction == 'IN',
            ~Check.status.in_(['RETURNED', 'BOUNCED', 'CANCELLED', 'ARCHIVED']),
            Check.currency == 'ILS'
        ).scalar() or 0
        checks_in_manual = Decimal(str(ils_manual_checks_in_sum))
        
        other_currency_manual_checks_in = session.query(
            func.sum(Check.amount), Check.currency, func.date(Check.check_date)
        ).filter(
            Check.customer_id == customer_id,
            Check.payment_id.is_(None),
            Check.direction == 'IN',
            ~Check.status.in_(['RETURNED', 'BOUNCED', 'CANCELLED', 'ARCHIVED']),
            Check.currency != 'ILS'
        ).group_by(Check.currency, func.date(Check.check_date)).all()
        for total_amt, currency, date_val in other_currency_manual_checks_in:
            try:
                checks_in_manual += convert_amount(Decimal(str(total_amt or 0)), currency, "ILS", date_val)
            except Exception:
                try:
                    session.rollback()
                except Exception:
                    pass
        
        result['checks_in_balance'] = checks_in_manual
        result['payments_in_balance'] += checks_in_manual
        
        # تحسين: استعلام واحد لجلب جميع الدفعات الصادرة
        payments_out_all = session.query(Payment).filter(
            Payment.customer_id == customer_id,
            Payment.direction == 'OUT',
            Payment.status.in_(['COMPLETED', 'PENDING']),
            Payment.expense_id.is_(None)
        ).options(selectinload(Payment.splits), selectinload(Payment.related_check)).all()
        
        for p in payments_out_all:
            splits = p.splits
            
            if splits:
                total_splits = Decimal('0.00')
                
                payment_checks = p.related_check
                
                returned_check_amounts = {}
                for check in payment_checks:
                    if check.status in ['RETURNED', 'BOUNCED']:
                        if check.reference_number and 'PMT-SPLIT-' in check.reference_number:
                            try:
                                split_id = int(check.reference_number.split('PMT-SPLIT-')[1].split('-')[0])
                                returned_check_amounts[split_id] = Decimal(str(check.amount or 0))
                            except:
                                pass
                        elif check.check_number:
                            for split in splits:
                                split_details = split.details or {}
                                if isinstance(split_details, str):
                                    try:
                                        import json
                                        split_details = json.loads(split_details)
                                    except:
                                        split_details = {}
                                if split_details.get('check_number') == check.check_number:
                                    returned_check_amounts[split.id] = Decimal(str(check.amount or 0))
                                    break
                
                # حساب مجموع جميع splits (بما فيها المرتجة)
                for split in splits:
                    split_amt = Decimal(str(split.amount or 0))
                    split_converted_amt = Decimal(str(getattr(split, 'converted_amount', 0) or 0))
                    split_converted_currency = (getattr(split, 'converted_currency', None) or split.currency or 'ILS').upper()
                    
                    if split_converted_amt > 0 and split_converted_currency == 'ILS':
                        total_splits += split_converted_amt
                    elif split.currency == "ILS":
                        total_splits += split_amt
                    else:
                        try:
                            total_splits += convert_amount(split_amt, split.currency, "ILS", p.payment_date)
                        except Exception:
                            try:
                                session.rollback()
                            except Exception:
                                pass
                
                amt = total_splits
            else:
                amt = Decimal(str(p.total_amount or 0))
            
            if p.currency == "ILS":
                result['payments_out_balance'] += amt
            else:
                try:
                    result['payments_out_balance'] += convert_amount(amt, p.currency, "ILS", p.payment_date)
                except Exception:
                    try:
                        session.rollback()
                    except Exception:
                        pass

        
        ils_manual_checks_out_sum = session.query(func.coalesce(func.sum(Check.amount), 0)).filter(
            Check.customer_id == customer_id,
            Check.payment_id.is_(None),
            Check.direction == 'OUT',
            ~Check.status.in_(['RETURNED', 'BOUNCED', 'CANCELLED', 'ARCHIVED']),
            Check.currency == 'ILS'
        ).scalar() or 0
        checks_out_manual = Decimal(str(ils_manual_checks_out_sum))
        
        other_currency_manual_checks_out = session.query(
            func.sum(Check.amount), Check.currency, func.date(Check.check_date)
        ).filter(
            Check.customer_id == customer_id,
            Check.payment_id.is_(None),
            Check.direction == 'OUT',
            ~Check.status.in_(['RETURNED', 'BOUNCED', 'CANCELLED', 'ARCHIVED']),
            Check.currency != 'ILS'
        ).group_by(Check.currency, func.date(Check.check_date)).all()
        for total_amt, currency, date_val in other_currency_manual_checks_out:
            try:
                checks_out_manual += convert_amount(Decimal(str(total_amt or 0)), currency, "ILS", date_val)
            except Exception:
                try:
                    session.rollback()
                except Exception:
                    pass
        
        result['checks_out_balance'] = checks_out_manual
        result['payments_out_balance'] += checks_out_manual
        
        # تحسين: استعلام واحد لجلب جميع الدفعات المرتدة (شيكات أو فشل)
        from sqlalchemy import exists
        from sqlalchemy.orm import aliased
        SplitCheck = aliased(Check)
        
        returned_payments_in = session.query(Payment).outerjoin(
            Sale, Payment.sale_id == Sale.id
        ).outerjoin(
            Invoice, Payment.invoice_id == Invoice.id
        ).outerjoin(
            ServiceRequest, Payment.service_id == ServiceRequest.id
        ).outerjoin(
            PreOrder, Payment.preorder_id == PreOrder.id
        ).outerjoin(
            Check, Check.payment_id == Payment.id
        ).filter(
            Payment.direction == 'IN',
            or_(
                Payment.customer_id == customer_id,
                Sale.customer_id == customer_id,
                Invoice.customer_id == customer_id,
                ServiceRequest.customer_id == customer_id,
                PreOrder.customer_id == customer_id
            ),
            or_(
                Check.status.in_(['RETURNED', 'BOUNCED']),
                and_(Payment.status == 'FAILED', Payment.method == PaymentMethod.CHEQUE.value),
                Payment.splits.any(
                    exists().where(
                        and_(
                            SplitCheck.reference_number == func.concat('PMT-SPLIT-', PaymentSplit.id),
                            SplitCheck.status.in_(['RETURNED', 'BOUNCED']),
                            SplitCheck.status != 'CANCELLED'
                        )
                    )
                )
            )
        ).options(
            selectinload(Payment.splits),
            selectinload(Payment.related_check)
        ).distinct().all()
        
        # تحسين: جلب جميع الشيكات المرتجعة المرتبطة بتقسيمات الدفعات دفعة واحدة لتجنب N+1
        all_returned_split_checks = session.query(Check).filter(
            Check.customer_id == customer_id,
            Check.status.in_(['RETURNED', 'BOUNCED']),
            Check.reference_number.like('PMT-SPLIT-%')
        ).all()
        
        returned_split_checks_map = {}
        for c in all_returned_split_checks:
            if c.reference_number:
                if c.reference_number not in returned_split_checks_map:
                    returned_split_checks_map[c.reference_number] = []
                returned_split_checks_map[c.reference_number].append(c)

        for p in returned_payments_in:
            splits = p.splits
            
            if splits:
                for split in splits:
                    is_cheque_split = (
                        split.method == PaymentMethod.CHEQUE.value or
                        split.method == PaymentMethod.CHEQUE or
                        (split.method and ('CHEQUE' in str(split.method).upper() or 'CHECK' in str(split.method).upper()))
                    )
                    if is_cheque_split:
                        # التحقق من وجود شيك مرتجع لهذا التقسيم
                        ref_key = f"PMT-SPLIT-{split.id}"
                        split_checks = returned_split_checks_map.get(ref_key, [])
                        # ملاحظة: يمكن تحسين هذا الاستعلام الداخلي أيضاً، لكنه يحدث فقط للدفعات المرتجعة وهي قليلة
                        
                        if split_checks:
                            for check in split_checks:
                                amt = Decimal(str(check.amount or 0))
                                check_currency = check.currency or split.currency or p.currency or "ILS"
                                if check_currency == "ILS":
                                    result['returned_checks_in_balance'] += amt
                                else:
                                    try:
                                        check_date = check.check_date if check else p.payment_date
                                        result['returned_checks_in_balance'] += convert_amount(amt, check_currency, "ILS", check_date)
                                    except Exception:
                                        try:
                                            session.rollback()
                                        except Exception:
                                            pass
                        else:
                            split_details = split.details or {}
                            if isinstance(split_details, str):
                                try:
                                    import json
                                    split_details = json.loads(split_details)
                                except:
                                    split_details = {}
                            
                            check_status = split_details.get('check_status', '').upper() if split_details else ''
                            
                            if check_status in ['RETURNED', 'BOUNCED']:
                                split_amt = Decimal(str(split.amount or 0))
                                split_converted_amt = Decimal(str(getattr(split, 'converted_amount', 0) or 0))
                                split_converted_currency = (getattr(split, 'converted_currency', None) or split.currency or 'ILS').upper()
                                split_currency = split.currency or p.currency or "ILS"
                                
                                if split_converted_amt > 0 and split_converted_currency == 'ILS':
                                    amt = split_converted_amt
                                elif split_currency == "ILS":
                                    amt = split_amt
                                else:
                                    try:
                                        amt = convert_amount(split_amt, split_currency, "ILS", p.payment_date)
                                    except Exception:
                                        try:
                                            session.rollback()
                                        except Exception:
                                            pass
                                        amt = split_amt
                                
                                result['returned_checks_in_balance'] += amt
            else:
                # استخدام الشيكات المحملة مسبقاً
                returned_checks = [c for c in p.related_check if c.status in ['RETURNED', 'BOUNCED'] and c.status != 'CANCELLED']
                
                for check in returned_checks:
                    amt = Decimal(str(check.amount or 0))
                    check_currency = check.currency or p.currency or "ILS"
                    if check_currency == "ILS":
                        result['returned_checks_in_balance'] += amt
                    else:
                        try:
                            check_date = check.check_date if check else p.payment_date
                            result['returned_checks_in_balance'] += convert_amount(amt, check_currency, "ILS", check_date)
                        except Exception:
                            try:
                                session.rollback()
                            except Exception:
                                pass
                
                if not splits and not returned_checks and p.status == 'FAILED' and p.method == PaymentMethod.CHEQUE.value:
                    amt = Decimal(str(p.total_amount or 0))
                    check_currency = p.currency or "ILS"
                    if check_currency == "ILS":
                        result['returned_checks_in_balance'] += amt
                    else:
                        try:
                            result['returned_checks_in_balance'] += convert_amount(amt, check_currency, "ILS", p.payment_date)
                        except Exception:
                            try:
                                session.rollback()
                            except Exception:
                                pass
        
        ils_manual_returned_checks_in_sum = session.query(func.coalesce(func.sum(Check.amount), 0)).filter(
            Check.customer_id == customer_id,
            Check.payment_id.is_(None),
            or_(
                Check.reference_number.is_(None),
                ~Check.reference_number.like('PMT-SPLIT-%')
            ),
            Check.direction == 'IN',
            Check.status.in_(['RETURNED', 'BOUNCED']),
            Check.status != 'CANCELLED',
            Check.currency == 'ILS'
        ).scalar() or 0
        result['returned_checks_in_balance'] += Decimal(str(ils_manual_returned_checks_in_sum))
        
        other_currency_manual_returned_checks_in = session.query(Check).filter(
            Check.customer_id == customer_id,
            Check.payment_id.is_(None),
            or_(
                Check.reference_number.is_(None),
                ~Check.reference_number.like('PMT-SPLIT-%')
            ),
            Check.direction == 'IN',
            Check.status.in_(['RETURNED', 'BOUNCED']),
            Check.status != 'CANCELLED',
            Check.currency != 'ILS'
        ).all()
        for check in other_currency_manual_returned_checks_in:
            amt = Decimal(str(check.amount or 0))
            try:
                result['returned_checks_in_balance'] += convert_amount(amt, check.currency, "ILS", check.check_date)
            except Exception:
                try:
                    session.rollback()
                except Exception:
                    pass
        
        # تحسين: استعلام واحد لجلب جميع الدفعات الصادرة المرتدة (شيكات أو فشل)
        returned_payments_out = session.query(Payment).outerjoin(
            Sale, Payment.sale_id == Sale.id
        ).outerjoin(
            Invoice, Payment.invoice_id == Invoice.id
        ).outerjoin(
            ServiceRequest, Payment.service_id == ServiceRequest.id
        ).outerjoin(
            PreOrder, Payment.preorder_id == PreOrder.id
        ).outerjoin(
            Check, Check.payment_id == Payment.id
        ).filter(
            Payment.direction == 'OUT',
            or_(
                Payment.customer_id == customer_id,
                Sale.customer_id == customer_id,
                Invoice.customer_id == customer_id,
                ServiceRequest.customer_id == customer_id,
                PreOrder.customer_id == customer_id
            ),
            or_(
                Check.status.in_(['RETURNED', 'BOUNCED']),
                and_(Payment.status == 'FAILED', Payment.method == PaymentMethod.CHEQUE.value),
                Payment.splits.any(
                    exists().where(
                        and_(
                            SplitCheck.reference_number == func.concat('PMT-SPLIT-', PaymentSplit.id),
                            SplitCheck.status.in_(['RETURNED', 'BOUNCED']),
                            SplitCheck.status != 'CANCELLED'
                        )
                    )
                )
            )
        ).options(
            selectinload(Payment.splits),
            selectinload(Payment.related_check)
        ).distinct().all()
        
        for p in returned_payments_out:
            splits = p.splits
            
            if splits:
                for split in splits:
                    is_cheque_split = (
                        split.method == PaymentMethod.CHEQUE.value or
                        split.method == PaymentMethod.CHEQUE or
                        (split.method and ('CHEQUE' in str(split.method).upper() or 'CHECK' in str(split.method).upper()))
                    )
                    if is_cheque_split:
                        ref_key = f"PMT-SPLIT-{split.id}"
                        split_checks = returned_split_checks_map.get(ref_key, [])
                        
                        if split_checks:
                            for check in split_checks:
                                amt = Decimal(str(check.amount or 0))
                                check_currency = check.currency or split.currency or p.currency or "ILS"
                                if check_currency == "ILS":
                                    result['returned_checks_out_balance'] += amt
                                else:
                                    try:
                                        check_date = check.check_date if check else p.payment_date
                                        result['returned_checks_out_balance'] += convert_amount(amt, check_currency, "ILS", check_date)
                                    except Exception:
                                        try:
                                            session.rollback()
                                        except Exception:
                                            pass
                        else:
                            split_details = split.details or {}
                            if isinstance(split_details, str):
                                try:
                                    import json
                                    split_details = json.loads(split_details)
                                except:
                                    split_details = {}
                            
                            check_status = split_details.get('check_status', '').upper() if split_details else ''
                            
                            if check_status in ['RETURNED', 'BOUNCED']:
                                split_amt = Decimal(str(split.amount or 0))
                                split_converted_amt = Decimal(str(getattr(split, 'converted_amount', 0) or 0))
                                split_converted_currency = (getattr(split, 'converted_currency', None) or split.currency or 'ILS').upper()
                                split_currency = split.currency or p.currency or "ILS"
                                
                                if split_converted_amt > 0 and split_converted_currency == 'ILS':
                                    amt = split_converted_amt
                                elif split_currency == "ILS":
                                    amt = split_amt
                                else:
                                    try:
                                        amt = convert_amount(split_amt, split_currency, "ILS", p.payment_date)
                                    except Exception:
                                        try:
                                            session.rollback()
                                        except Exception:
                                            pass
                                        amt = split_amt
                                
                                result['returned_checks_out_balance'] += amt
            else:
                # استخدام الشيكات المحملة مسبقاً
                returned_checks = [c for c in p.related_check if c.status in ['RETURNED', 'BOUNCED'] and c.status != 'CANCELLED']
                
                for check in returned_checks:
                    amt = Decimal(str(check.amount or 0))
                    check_currency = check.currency or p.currency or "ILS"
                    if check_currency == "ILS":
                        result['returned_checks_out_balance'] += amt
                    else:
                        try:
                            check_date = check.check_date if check else p.payment_date
                            result['returned_checks_out_balance'] += convert_amount(amt, check_currency, "ILS", check_date)
                        except Exception:
                            try:
                                session.rollback()
                            except Exception:
                                pass
                
                if not returned_checks and p.status == 'FAILED' and p.method == PaymentMethod.CHEQUE.value:
                    amt = Decimal(str(p.total_amount or 0))
                    check_currency = p.currency or "ILS"
                    if check_currency == "ILS":
                        result['returned_checks_out_balance'] += amt
                    else:
                        try:
                            result['returned_checks_out_balance'] += convert_amount(amt, check_currency, "ILS", p.payment_date)
                        except Exception:
                            try:
                                session.rollback()
                            except Exception:
                                pass
        
        ils_manual_returned_checks_out_sum = session.query(func.coalesce(func.sum(Check.amount), 0)).filter(
            Check.customer_id == customer_id,
            Check.payment_id.is_(None),
            Check.direction == 'OUT',
            Check.status.in_(['RETURNED', 'BOUNCED']),
            Check.status != 'CANCELLED',
            Check.currency == 'ILS'
        ).scalar() or 0
        result['returned_checks_out_balance'] += Decimal(str(ils_manual_returned_checks_out_sum))
        
        other_currency_manual_returned_checks_out = session.query(Check).filter(
            Check.customer_id == customer_id,
            Check.payment_id.is_(None),
            Check.direction == 'OUT',
            Check.status.in_(['RETURNED', 'BOUNCED']),
            Check.status != 'CANCELLED',
            Check.currency != 'ILS'
        ).all()
        for check in other_currency_manual_returned_checks_out:
            amt = Decimal(str(check.amount or 0))
            try:
                result['returned_checks_out_balance'] += convert_amount(amt, check.currency, "ILS", check.check_date)
            except Exception:
                try:
                    session.rollback()
                except Exception:
                    pass
        
        expenses = session.query(Expense).filter(
            Expense.customer_id == customer_id
        ).options(joinedload(Expense.type)).all()
        
        for exp in expenses:
            amt = Decimal(str(exp.amount or 0))
            amt_ils = amt
            if exp.currency and exp.currency != "ILS":
                try:
                    amt_ils = convert_amount(amt, exp.currency, "ILS", exp.date)
                except Exception:
                    try:
                        session.rollback()
                    except Exception:
                        pass
            
            exp_type_code = None
            if exp.type:
                exp_type_code = (exp.type.code or "").strip().upper()
            
            is_service_expense = (
                exp_type_code in ('PARTNER_EXPENSE', 'SERVICE_EXPENSE') or
                (exp.partner_id and exp.payee_type and exp.payee_type.upper() == "PARTNER") or
                (exp.supplier_id and exp.payee_type and exp.payee_type.upper() == "SUPPLIER")
            )
            
            if is_service_expense:
                result['service_expenses_balance'] += amt_ils
            else:
                result['expenses_balance'] += amt_ils
        
    except Exception as e:
        from flask import current_app
        try:
            if session is not None and hasattr(session, "rollback"):
                session.rollback()
        except Exception:
            pass
        try:
            current_app.logger.error(f"خطأ في حساب مكونات رصيد العميل #{customer_id}: {e}")
        except:
            pass
        return None
    
    return result


def build_customer_balance_view(customer_id, session=None):
    if not customer_id:
        return {"success": False, "error": "customer_id is required"}
    session = session or db.session
    customer = session.get(Customer, customer_id)
    if not customer:
        return {"success": False, "error": "Customer not found"}
    components = calculate_customer_balance_components(customer_id, session)
    if not components:
        try:
            if session is not None and hasattr(session, "rollback"):
                session.rollback()
        except Exception:
            pass
        return {"success": False, "error": "Unable to calculate customer balance"}

    def _dec(value):
        return Decimal(str(value or 0))

    def _component(key):
        return _dec(components.get(key, 0))

    opening_balance = _dec(customer.opening_balance or 0)
    if customer.currency and customer.currency != "ILS":
        try:
            opening_balance = convert_amount(opening_balance, customer.currency, "ILS")
        except Exception:
            try:
                session.rollback()
            except Exception:
                pass

    rights_rows = [
        {"key": "payments_in_balance", "label": "دفعات واردة", "flow": "IN", "amount": _component("payments_in_balance")},
        {"key": "returns_balance", "label": "مرتجعات مبيعات", "flow": "IN", "amount": _component("returns_balance")},
        {"key": "returned_checks_out_balance", "label": "شيكات صادرة مرتدة", "flow": "IN", "amount": _component("returned_checks_out_balance")},
        {"key": "service_expenses_balance", "label": "توريد خدمات لصالحه", "flow": "IN", "amount": _component("service_expenses_balance")},
    ]

    obligations_rows = [
        {"key": "sales_balance", "label": "مبيعات", "flow": "OUT", "amount": _component("sales_balance")},
        {"key": "invoices_balance", "label": "فواتير", "flow": "OUT", "amount": _component("invoices_balance")},
        {"key": "services_balance", "label": "صيانة", "flow": "OUT", "amount": _component("services_balance")},
        {"key": "preorders_balance", "label": "حجوزات مسبقة", "flow": "OUT", "amount": _component("preorders_balance")},
        {"key": "online_orders_balance", "label": "طلبات أونلاين", "flow": "OUT", "amount": _component("online_orders_balance")},
        {"key": "payments_out_balance", "label": "دفعات صادرة", "flow": "OUT", "amount": _component("payments_out_balance")},
        {"key": "returned_checks_in_balance", "label": "شيكات واردة مرتدة", "flow": "OUT", "amount": _component("returned_checks_in_balance")},
        {"key": "expenses_balance", "label": "مصاريف / خصومات", "flow": "OUT", "amount": _component("expenses_balance")},
    ]

    rights_total = sum((row["amount"] for row in rights_rows), Decimal("0.00"))
    obligations_total = sum((row["amount"] for row in obligations_rows), Decimal("0.00"))
    calculated_balance = opening_balance + rights_total - obligations_total
    stored_balance = _dec(customer.current_balance or 0)
    difference = calculated_balance - stored_balance
    tolerance = Decimal("0.01")

    def _serialize(rows):
        ordered = sorted(rows, key=lambda r: r["amount"], reverse=True)
        return [
            {
                "key": row["key"],
                "label": row["label"],
                "flow": row.get("flow"),
                "amount": float(row["amount"]),
            }
            for row in ordered
        ]

    def _direction_text(amount):
        if amount > 0:
            return "له عندنا"
        if amount < 0:
            return "عليه لنا"
        return "متوازن"

    def _action_text(amount):
        if amount > 0:
            return "يجب أن ندفع له"
        if amount < 0:
            return "يجب أن يدفع لنا"
        return "لا يوجد رصيد مستحق"

    formula = f"({float(opening_balance):.2f} + {float(rights_total):.2f} - {float(obligations_total):.2f}) = {float(calculated_balance):.2f}"

    return {
        "success": True,
        "customer": {
            "id": customer.id,
            "name": customer.name,
            "currency": customer.currency or "ILS",
        },
        "opening_balance": {
            "amount": float(opening_balance),
            "direction": _direction_text(opening_balance),
        },
        "rights": {
            "total": float(rights_total),
            "items": _serialize(rights_rows),
        },
        "obligations": {
            "total": float(obligations_total),
            "items": _serialize(obligations_rows),
        },
        "payments": {
            "received": float(_component("payments_in_balance")),
            "paid": float(_component("payments_out_balance")),
            "returned_in": float(_component("returned_checks_in_balance")),
            "returned_out": float(_component("returned_checks_out_balance")),
        },
        "checks": {
            "in_progress": float(_component("checks_in_balance")),
            "outstanding": float(_component("checks_out_balance")),
        },
        "balance": {
            "amount": float(calculated_balance),
            "direction": _direction_text(calculated_balance),
            "action": _action_text(calculated_balance),
            "formula": formula,
            "matches_stored": difference.copy_abs() <= tolerance,
            "stored": float(stored_balance),
            "difference": float(difference),
        },
        "components": {key: float(_dec(val)) for key, val in components.items()},
    }


def calculate_balance_before_date(customer_id, before_date, session=None):
    """
    حساب رصيد العميل المتراكم قبل تاريخ معين (للرصيد الافتتاحي في كشف الحساب)
    """
    if not session:
        session = db.session
        
    try:
        from sqlalchemy.orm import Session
        from sqlalchemy import text as sa_text
        if isinstance(session, Session):
            try:
                session.execute(sa_text("SELECT 1"))
            except Exception:
                from sqlalchemy.orm import sessionmaker
                session = sessionmaker(bind=db.engine)()
    except Exception:
        pass
        
    customer = session.get(Customer, customer_id)
    if not customer:
        return Decimal('0.00')

    # 1. Opening Balance (Static)
    opening_balance = Decimal(str(customer.opening_balance or 0))
    if customer.currency and customer.currency != "ILS":
        try:
            opening_balance = convert_amount(opening_balance, customer.currency, "ILS", customer.created_at)
        except:
            pass
        
    # Helper for summing with date filter and currency conversion
    def sum_model(model, date_field, amount_field='total_amount', extra_filters=None):
        total = Decimal('0.00')
        
        # ILS
        filters = [
            getattr(model, 'customer_id') == customer_id,
            getattr(model, 'currency') == 'ILS',
            getattr(model, date_field) < before_date
        ]
        if extra_filters:
            filters.extend(extra_filters)
            
        val = session.query(func.coalesce(func.sum(getattr(model, amount_field)), 0)).filter(*filters).scalar() or 0
        total += Decimal(str(val))
        
        # Other Currencies
        filters_other = [
            getattr(model, 'customer_id') == customer_id,
            getattr(model, 'currency') != 'ILS',
            getattr(model, date_field) < before_date
        ]
        if extra_filters:
            filters_other.extend(extra_filters)
            
        others = session.query(model).filter(*filters_other).all()
        for item in others:
            amt = Decimal(str(getattr(item, amount_field) or 0))
            try:
                d_val = getattr(item, date_field) or before_date
                total += convert_amount(amt, item.currency, "ILS", d_val)
            except:
                pass
        return total

    # 2. Rights (Flow IN - Increases what we owe him or decreases what he owes us)
    # Payments IN
    payments_in = Decimal('0.00')
    p_filters = [
        Payment.direction == 'IN',
        Payment.status.in_(['COMPLETED', 'PENDING']),
        Payment.expense_id.is_(None)
    ]
    
    p_in_all = session.query(Payment).filter(
        Payment.customer_id == customer_id,
        Payment.payment_date < before_date,
        *p_filters
    ).all()
    
    for p in p_in_all:
        amt = Decimal(str(p.total_amount or 0))
        if p.currency != 'ILS':
             try:
                amt = convert_amount(amt, p.currency, "ILS", p.payment_date)
             except:
                pass
        payments_in += amt

    # Sale Returns
    returns_balance = sum_model(SaleReturn, 'created_at', 'total_amount', [SaleReturn.status == 'CONFIRMED'])
    
    # Manual Checks IN
    checks_in = Decimal('0.00')
    c_filters = [
        Check.payment_id.is_(None),
        Check.direction == 'IN',
        ~Check.status.in_(['RETURNED', 'BOUNCED', 'CANCELLED', 'ARCHIVED'])
    ]
    checks_in_all = session.query(Check).filter(
        Check.customer_id == customer_id,
        Check.check_date < before_date,
        *c_filters
    ).all()
    for c in checks_in_all:
        amt = Decimal(str(c.amount or 0))
        if c.currency and c.currency != 'ILS':
            try:
                amt = convert_amount(amt, c.currency, "ILS", c.check_date)
            except:
                pass
        checks_in += amt
    
    # Service Expenses
    service_expenses = Decimal('0.00')
    exp_all = session.query(Expense).filter(
        Expense.customer_id == customer_id,
        Expense.date < before_date
    ).all()
    
    for exp in exp_all:
        amt = Decimal(str(exp.amount or 0))
        if exp.currency and exp.currency != "ILS":
            try:
                amt = convert_amount(amt, exp.currency, "ILS", exp.date)
            except:
                pass
        
        exp_type_code = None
        if exp.type_id:
            et = session.query(ExpenseType).filter_by(id=exp.type_id).first()
            if et:
                exp_type_code = (et.code or "").strip().upper()
                
        is_service_expense = (
            exp_type_code in ('PARTNER_EXPENSE', 'SERVICE_EXPENSE') or
            (exp.partner_id and exp.payee_type and exp.payee_type.upper() == "PARTNER") or
            (exp.supplier_id and exp.payee_type and exp.payee_type.upper() == "SUPPLIER")
        )
        
        if is_service_expense:
            service_expenses += amt
            
    rights_total = payments_in + returns_balance + checks_in + service_expenses
    
    # 3. Obligations (Flow OUT - Increases what he owes us)
    sales_balance = sum_model(Sale, 'sale_date', 'total_amount', [Sale.status == 'CONFIRMED'])
    invoices_balance = sum_model(Invoice, 'invoice_date', 'total_amount', [Invoice.cancelled_at.is_(None)])
    
    # Services
    services_balance = Decimal('0.00')
    srv_all = session.query(ServiceRequest).filter(
        ServiceRequest.customer_id == customer_id,
        ServiceRequest.received_at < before_date
    ).all()
    for srv in srv_all:
        subtotal = Decimal(str(srv.parts_total or 0)) + Decimal(str(srv.labor_total or 0))
        discount = Decimal(str(srv.discount_total or 0))
        base = subtotal - discount
        if base < 0: base = Decimal('0.00')
        tax = base * (Decimal(str(srv.tax_rate or 0)) / Decimal('100'))
        total = base + tax
        if srv.currency and srv.currency != 'ILS':
            try:
                total = convert_amount(total, srv.currency, "ILS", srv.received_at)
            except:
                pass
        services_balance += total

    # Online Orders
    online_orders_balance = sum_model(OnlinePreOrder, 'created_at', 'total_amount', [OnlinePreOrder.payment_status != 'CANCELLED'])
    
    # Payments OUT
    payments_out = Decimal('0.00')
    p_out_filters = [
        Payment.direction == 'OUT',
        Payment.status.in_(['COMPLETED', 'PENDING']),
        Payment.expense_id.is_(None)
    ]
    p_out_all = session.query(Payment).filter(
        Payment.customer_id == customer_id,
        Payment.payment_date < before_date,
        *p_out_filters
    ).all()
    for p in p_out_all:
        amt = Decimal(str(p.total_amount or 0))
        if p.currency != 'ILS':
             try:
                amt = convert_amount(amt, p.currency, "ILS", p.payment_date)
             except:
                pass
        payments_out += amt

    # Expenses (Normal expenses, not service ones)
    expenses_balance = Decimal('0.00')
    # Reuse exp_all from above
    for exp in exp_all:
        amt = Decimal(str(exp.amount or 0))
        if exp.currency and exp.currency != "ILS":
            try:
                amt = convert_amount(amt, exp.currency, "ILS", exp.date)
            except:
                pass
        
        exp_type_code = None
        if exp.type_id:
            et = session.query(ExpenseType).filter_by(id=exp.type_id).first()
            if et:
                exp_type_code = (et.code or "").strip().upper()
                
        is_service_expense = (
            exp_type_code in ('PARTNER_EXPENSE', 'SERVICE_EXPENSE') or
            (exp.partner_id and exp.payee_type and exp.payee_type.upper() == "PARTNER") or
            (exp.supplier_id and exp.payee_type and exp.payee_type.upper() == "SUPPLIER")
        )
        
        if not is_service_expense:
            expenses_balance += amt
    
    obligations_total = sales_balance + invoices_balance + services_balance + online_orders_balance + payments_out + expenses_balance
    
    return opening_balance + rights_total - obligations_total

