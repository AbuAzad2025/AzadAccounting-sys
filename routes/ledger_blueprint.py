
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, render_template, current_app, abort
from flask_login import login_required, current_user
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import func, and_, or_, desc
from extensions import db
import utils
from models import (
    Sale, SaleReturn, Expense, Payment, ServiceRequest,
    Customer, Supplier, Partner,
    Product, StockLevel, GLBatch, GLEntry, Account,
    Invoice, PreOrder, Shipment, Employee,
    PaymentEntityType
)
from services.ledger_service import (
    SmartEntityExtractor, LedgerQueryOptimizer, CurrencyConverter,
    LedgerStatisticsCalculator, LedgerCache
)

csrf = CSRFProtect()

ledger_bp = Blueprint("ledger", __name__, url_prefix="/ledger")


@ledger_bp.before_request
def _restrict_super_admin():
    # تمت إزالة القيد للسماح للسوبر أدمن بالوصول
    pass

def extract_entity_from_batch(batch: GLBatch):
    return SmartEntityExtractor.extract_from_batch(batch)

@ledger_bp.route("/", methods=["GET"], endpoint="index")
@login_required
def ledger_index():
    """صفحة الدفتر الرئيسية"""
    return render_template("ledger/index.html")

@ledger_bp.route("/chart-of-accounts", methods=["GET"], endpoint="chart_of_accounts")
@login_required
def chart_of_accounts():
    """دليل الحسابات المحاسبية - واجهة مبسطة"""
    return render_template("ledger/chart_of_accounts.html")

@ledger_bp.route("/accounts", methods=["GET"], endpoint="get_accounts")
@login_required
def get_accounts():
    """API: جلب جميع الحسابات المحاسبية"""
    try:
        accounts = Account.query.filter_by(is_active=True).order_by(Account.code).all()
        
        accounts_list = []
        for acc in accounts:
            accounts_list.append({
                'id': acc.id,
                'code': acc.code,
                'name': acc.name,
                'type': acc.type,
                'is_active': acc.is_active
            })
        
        return jsonify({
            'success': True,
            'accounts': accounts_list,
            'total': len(accounts_list)
        })
    except Exception as e:
        current_app.logger.error(f"خطأ في جلب الحسابات: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@ledger_bp.route("/manual-entry", methods=["POST"], endpoint="create_manual_entry")
@login_required
def create_manual_entry():
    """إنشاء قيد يدوي (Manual Journal Entry)"""
    try:
        from flask_login import current_user
        from decimal import Decimal
        
        data = request.get_json()
        
        # استخراج البيانات
        entry_date = data.get('date')
        amount = Decimal(str(data.get('amount', 0)))
        description = data.get('description', '').strip()
        debit_account = data.get('debit_account', '').strip()
        credit_account = data.get('credit_account', '').strip()
        
        # التحقق
        if not all([entry_date, amount, description, debit_account, credit_account]):
            return jsonify({'success': False, 'error': 'جميع الحقول مطلوبة'}), 400
        
        if amount <= 0:
            return jsonify({'success': False, 'error': 'المبلغ يجب أن يكون أكبر من صفر'}), 400
        
        if debit_account == credit_account:
            return jsonify({'success': False, 'error': 'لا يمكن أن يكون الحساب نفسه في الطرفين'}), 400
        
        # التحقق من وجود الحسابات
        debit_acc = Account.query.filter_by(code=debit_account, is_active=True).first()
        credit_acc = Account.query.filter_by(code=credit_account, is_active=True).first()
        
        if not debit_acc or not credit_acc:
            return jsonify({'success': False, 'error': 'حساب غير صحيح أو غير نشط'}), 400
        
        # إنشاء GLBatch
        from datetime import datetime
        posted_at = datetime.strptime(entry_date, '%Y-%m-%d')
        
        ref_number = f"MAN-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        # استخدام timestamp كـ source_id فريد لكل قيد يدوي
        unique_source_id = int(datetime.now().timestamp() * 1000)
        
        batch = GLBatch(
            source_type='MANUAL',
            source_id=unique_source_id,
            purpose='MANUAL_ENTRY',
            posted_at=posted_at,
            currency='ILS',
            memo=description,
            status='POSTED',
            entity_type=None,
            entity_id=None
        )
        db.session.add(batch)
        db.session.flush()
        
        # إنشاء GLEntry - المدين
        entry_debit = GLEntry(
            batch_id=batch.id,
            account=debit_account,
            debit=amount,
            credit=0,
            currency='ILS',
            ref=ref_number
        )
        db.session.add(entry_debit)
        
        # إنشاء GLEntry - الدائن
        entry_credit = GLEntry(
            batch_id=batch.id,
            account=credit_account,
            debit=0,
            credit=amount,
            currency='ILS',
            ref=ref_number
        )
        db.session.add(entry_credit)
        
        db.session.commit()
        
        current_app.logger.info(f"✅ تم إنشاء قيد يدوي: {description} - {amount} ₪")
        
        return jsonify({
            'success': True,
            'message': 'تم حفظ القيد اليدوي بنجاح',
            'batch_id': batch.id,
            'batch_code': batch.code
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"❌ خطأ في إنشاء قيد يدوي: {str(e)}")
        
        return jsonify({'success': False, 'error': str(e)}), 500

@ledger_bp.route("/data", methods=["GET"], endpoint="get_ledger_data")
@login_required
def get_ledger_data():
    """جلب بيانات دفتر الأستاذ من قاعدة البيانات الحقيقية"""
    try:
        from models import fx_rate
        
        from_date_str = request.args.get('from_date')
        to_date_str = request.args.get('to_date')
        transaction_type = request.args.get('transaction_type', '').strip()
        
        # تحليل التواريخ
        from_date = datetime.strptime(from_date_str, '%Y-%m-%d') if from_date_str else None
        to_date = datetime.strptime(to_date_str, '%Y-%m-%d').replace(hour=23, minute=59, second=59) if to_date_str else None
        
        ledger_entries = []
        running_balance = 0.0
        
        # --- بداية منطق القيد المزدوج (Double Entry Journal) ---
        # بدلاً من تجميع البيانات يدوياً من جداول المبيعات والمصاريف، نقوم بجلب القيود مباشرة من GLEntry
        # هذا يضمن دقة محاسبية (Debit = Credit) وعدم ازدواجية، ويعكس دفتر اليومية العام.

        query = db.session.query(GLEntry, GLBatch, Account).join(GLBatch, GLEntry.batch_id == GLBatch.id).outerjoin(Account, GLEntry.account == Account.code)
        
        if from_date:
            query = query.filter(GLBatch.posted_at >= from_date)
        if to_date:
            query = query.filter(GLBatch.posted_at <= to_date)
            
        if transaction_type:
            tt_upper = transaction_type.strip().upper()
            if tt_upper == 'SALE':
                query = query.filter(GLBatch.source_type == 'SALE')
            elif tt_upper in ['SALE_RETURN', 'RETURN']:
                query = query.filter(GLBatch.source_type == 'SALE_RETURN')
            elif tt_upper in ['PURCHASE', 'EXPENSE']:
                query = query.filter(GLBatch.source_type.in_(['EXPENSE', 'PURCHASE']))
            elif tt_upper == 'PAYMENT':
                 query = query.filter(GLBatch.source_type == 'PAYMENT')
            elif tt_upper == 'OPENING':
                 query = query.filter(GLBatch.purpose == 'OPENING_BALANCE')
            elif tt_upper in ['MANUAL', 'JOURNAL']:
                 query = query.filter(GLBatch.source_type == 'MANUAL')
            elif tt_upper == 'SERVICE':
                query = query.filter(GLBatch.source_type == 'SERVICE')

        # ترتيب حسب التاريخ، ثم رقم القيد، ثم المدين أولاً (المتعارف عليه في اليومية)
        entries = query.order_by(GLBatch.posted_at, GLBatch.id, desc(GLEntry.debit)).limit(5000).all()
        
        # قاموس لترجمة أنواع العمليات
        type_map = {
            'SALE': 'مبيعات',
            'SALE_RETURN': 'مرتجع مبيعات',
            'EXPENSE': 'مصروف',
            'PURCHASE': 'مشتريات',
            'PAYMENT': 'دفعة',
            'MANUAL': 'قيد يدوي',
            'OPENING_BALANCE': 'رصيد افتتاحي',
            'SERVICE': 'صيانة',
            'PREORDER': 'حجز مسبق',
            'EXCHANGE': 'توريد/صرف'
        }

        for entry, batch, account in entries:
            # استخراج اسم الجهة (عميل، مورد، الخ)
            entity_name, entity_type_ar, entity_id, entity_type_code = SmartEntityExtractor.extract_from_batch(batch)
            if not entity_name:
                entity_name = "—"
            
            # بناء الوصف: البيان من القيد + اسم الحساب
            desc_parts = []
            if batch.memo:
                desc_parts.append(batch.memo)
            
            account_display = f"{entry.account}"
            if account:
                account_display = f"{account.name} ({entry.account})"
            
            # الوصف النهائي: الحساب | البيان
            description = f"{account_display}"
            if batch.memo:
                 description += f" | {batch.memo}"

            # نوع العملية بالعربي
            source_type = (batch.source_type or '').upper()
            type_ar = type_map.get(source_type, source_type)
            if batch.purpose == 'OPENING_BALANCE':
                type_ar = 'رصيد افتتاحي'

            debit = float(entry.debit or 0)
            credit = float(entry.credit or 0)
            
            # الرصيد المتراكم في العرض (الفرق بين المدين والدائن)
            # في دفتر اليومية، الرصيد التراكمي للشركة ككل هو صفر دائماً (نظرياً)
            # لكن سنعرض التراكمي للفترة المحددة
            running_balance += (debit - credit)
            
            ledger_entries.append({
                "id": entry.id,
                "date": batch.posted_at.strftime('%Y-%m-%d'),
                "transaction_number": (batch.code or f"BATCH-{batch.id}"),
                "type": (batch.source_type or "").lower(),
                "type_ar": type_ar,
                "description": description,
                "debit": debit,
                "credit": credit,
                "balance": running_balance, 
                "entity_name": entity_name,
                "entity_type": entity_type_ar or "",
                "batch_id": batch.id,
                "source_id": batch.source_id
            })

        # --- نهاية منطق القيد المزدوج ---
        
        # ترتيب حسب التاريخ
        sort = request.args.get('sort', 'date')
        order = request.args.get('order', 'asc')
        
        if sort == 'date':
            if order == 'asc':
                ledger_entries.sort(key=lambda x: (x['date'], x.get('id', 0)))
            else:
                ledger_entries.sort(key=lambda x: (x['date'], x.get('id', 0)), reverse=True)
        elif sort == 'debit':
            if order == 'asc':
                ledger_entries.sort(key=lambda x: (x['debit'], x.get('id', 0)))
            else:
                ledger_entries.sort(key=lambda x: (x['debit'], x.get('id', 0)), reverse=True)
        elif sort == 'credit':
            if order == 'asc':
                ledger_entries.sort(key=lambda x: (x['credit'], x.get('id', 0)))
            else:
                ledger_entries.sort(key=lambda x: (x['credit'], x.get('id', 0)), reverse=True)
        elif sort == 'balance':
            if order == 'asc':
                ledger_entries.sort(key=lambda x: (x.get('balance', 0), x.get('id', 0)))
            else:
                ledger_entries.sort(key=lambda x: (x.get('balance', 0), x.get('id', 0)), reverse=True)
        elif sort == 'type':
            if order == 'asc':
                ledger_entries.sort(key=lambda x: (x.get('type_ar', ''), x.get('id', 0)))
            else:
                ledger_entries.sort(key=lambda x: (x.get('type_ar', ''), x.get('id', 0)), reverse=True)
        else:
            ledger_entries.sort(key=lambda x: (x['date'], x.get('id', 0)))
        
        # إعادة حساب الرصيد المتراكم
        running_balance = 0.0
        for entry in ledger_entries:
            running_balance += entry['debit'] - entry['credit']
            entry['balance'] = running_balance
        
        # حساب الإحصائيات الحقيقية من قاعدة البيانات
        from models import fx_rate
        
        # 1. إجمالي المبيعات
        sales_query = Sale.query.filter(Sale.status == 'CONFIRMED')
        if from_date:
            sales_query = sales_query.filter(Sale.sale_date >= from_date)
        if to_date:
            sales_query = sales_query.filter(Sale.sale_date <= to_date)
        
        total_sales = 0.0
        for sale in sales_query.all():
            amount = float(sale.total_amount or 0)
            if sale.currency and sale.currency != 'ILS':
                try:
                    rate = fx_rate(sale.currency, 'ILS', sale.sale_date, raise_on_missing=False)
                    if rate > 0:
                        amount = float(amount * float(rate))
                    else:
                        current_app.logger.warning(f"⚠️ سعر صرف مفقود في إحصائيات دفتر الأستاذ: {sale.currency}/ILS للبيع #{sale.id}")
                except Exception as e:
                    current_app.logger.error(f"❌ خطأ في تحويل العملة في إحصائيات دفتر الأستاذ للبيع #{sale.id}: {str(e)}")
            total_sales += amount
        
        # 2. إجمالي المشتريات والنفقات
        expenses_query = Expense.query
        if from_date:
            expenses_query = expenses_query.filter(Expense.date >= from_date)
        if to_date:
            expenses_query = expenses_query.filter(Expense.date <= to_date)
        
        total_expenses = 0.0
        for expense in expenses_query.all():
            amount = float(expense.amount or 0)
            if expense.currency and expense.currency != 'ILS':
                try:
                    rate = fx_rate(expense.currency, 'ILS', expense.date, raise_on_missing=False)
                    if rate > 0:
                        amount = float(amount * float(rate))
                    else:
                        current_app.logger.warning(f"⚠️ سعر صرف مفقود في إحصائيات دفتر الأستاذ: {expense.currency}/ILS للمصروف #{expense.id}")
                except Exception as e:
                    current_app.logger.error(f"❌ خطأ في تحويل العملة في إحصائيات دفتر الأستاذ للمصروف #{expense.id}: {str(e)}")
            total_expenses += amount
        
        # 3. إجمالي الخدمات (الصيانة)
        services_query = ServiceRequest.query
        if from_date:
            services_query = services_query.filter(ServiceRequest.created_at >= from_date)
        if to_date:
            services_query = services_query.filter(ServiceRequest.created_at <= to_date)
        
        total_services = 0.0
        for service in services_query.limit(10000).all():
            # استخدام total_amount المحفوظ في قاعدة البيانات (بعد الخصم والضريبة)
            service_total = float(service.total_amount or 0)
            
            # إذا كان total_amount غير موجود أو صفر، نحسبه يدوياً
            if service_total <= 0:
                parts_total = float(service.parts_total or 0)
                labor_total = float(service.labor_total or 0)
                discount = float(service.discount_total or 0)
                tax_rate = float(service.tax_rate or 0)
                
                # الحساب: (parts + labor - discount) * (1 + tax_rate/100)
                subtotal = parts_total + labor_total - discount
                if subtotal < 0:
                    subtotal = 0
                tax_amount = subtotal * (tax_rate / 100.0)
                service_total = subtotal + tax_amount
            
            # تحويل للشيقل إذا كانت بعملة أخرى
            service_currency = getattr(service, 'currency', 'ILS') or 'ILS'
            if service_currency != 'ILS':
                try:
                    rate = fx_rate(service_currency, 'ILS', service.created_at or datetime.utcnow(), raise_on_missing=False)
                    if rate > 0:
                        service_total = float(service_total * float(rate))
                    else:
                        current_app.logger.warning(f"⚠️ سعر صرف مفقود في إحصائيات دفتر الأستاذ: {service_currency}/ILS للخدمة #{service.id}")
                except Exception as e:
                    current_app.logger.error(f"❌ خطأ في تحويل العملة في إحصائيات دفتر الأستاذ للخدمة #{service.id}: {str(e)}")
            
            total_services += service_total
        
        # 4. حساب تكلفة البضاعة المباعة (COGS - Cost of Goods Sold)
        from models import SaleLine
        
        total_cogs = 0.0  # تكلفة البضاعة المباعة
        cogs_details = []
        products_without_cost = []  # منتجات بدون تكلفة شراء
        estimated_products = []  # منتجات تم تقدير تكلفتها
        
        # جلب جميع أسطر المبيعات في الفترة
        sale_lines_query = (
            db.session.query(SaleLine)
            .join(Sale, Sale.id == SaleLine.sale_id)
        )
        if from_date:
            sale_lines_query = sale_lines_query.filter(Sale.sale_date >= from_date)
        if to_date:
            sale_lines_query = sale_lines_query.filter(Sale.sale_date <= to_date)
        
        for line in sale_lines_query.limit(100000).all():
            if line.product:
                qty_sold = float(line.quantity or 0)
                product = line.product
                unit_cost = None
                cost_source = None
                
                # 1️⃣ محاولة استخدام تكلفة الشراء (الأفضل)
                if product.purchase_price and product.purchase_price > 0:
                    unit_cost = float(product.purchase_price)
                    cost_source = "purchase_price"
                # 2️⃣ التكلفة بعد الشحن
                elif product.cost_after_shipping and product.cost_after_shipping > 0:
                    unit_cost = float(product.cost_after_shipping)
                    cost_source = "cost_after_shipping"
                # 3️⃣ التكلفة قبل الشحن
                elif product.cost_before_shipping and product.cost_before_shipping > 0:
                    unit_cost = float(product.cost_before_shipping)
                    cost_source = "cost_before_shipping"
                # 4️⃣ تقدير محافظ: 70% من سعر البيع
                elif product.price and product.price > 0:
                    unit_cost = float(product.price) * 0.70  # 70% من سعر البيع
                    cost_source = "estimated_70%"
                    
                    # تسجيل تحذير
                    current_app.logger.warning(
                        f"⚠️ تقدير تكلفة المنتج '{product.name}' (#{product.id}): "
                        f"استخدام 70% من سعر البيع = {unit_cost:.2f} ₪"
                    )
                    
                    # إضافة للقائمة
                    estimated_products.append({
                        'id': product.id,
                        'name': product.name,
                        'selling_price': float(product.price),
                        'estimated_cost': unit_cost,
                        'qty_sold': qty_sold
                    })
                # 5️⃣ لا يوجد أي سعر - تجاهل المنتج
                else:
                    current_app.logger.error(
                        f"❌ المنتج '{product.name}' (#{product.id}) بدون تكلفة أو سعر - "
                        f"تم تجاهله من حساب COGS"
                    )
                    products_without_cost.append({
                        'id': product.id,
                        'name': product.name,
                        'qty_sold': qty_sold
                    })
                    continue  # تخطي هذا المنتج
                
                line_cogs = qty_sold * unit_cost
                total_cogs += line_cogs
                
                if len(cogs_details) < 10:  # حفظ أول 10 لأغراض التفصيل
                    cogs_details.append({
                        'product': product.name,
                        'qty': qty_sold,
                        'unit_cost': unit_cost,
                        'total': line_cogs,
                        'source': cost_source
                    })
        
        # 5. حساب تكلفة الخدمات (قطع الغيار المستخدمة)
        from models import ServicePart
        
        total_service_costs = 0.0
        
        service_parts_query = (
            db.session.query(ServicePart)
            .join(ServiceRequest, ServiceRequest.id == ServicePart.service_id)
        )
        if from_date:
            service_parts_query = service_parts_query.filter(ServiceRequest.created_at >= from_date)
        if to_date:
            service_parts_query = service_parts_query.filter(ServiceRequest.created_at <= to_date)
        
        for part in service_parts_query.limit(50000).all():
            if part.part:  # part هو المنتج
                qty_used = float(part.quantity or 0)
                product = part.part
                unit_cost = None
                
                # نفس المنطق: تكلفة فعلية أو تقدير
                if product.purchase_price and product.purchase_price > 0:
                    unit_cost = float(product.purchase_price)
                elif product.cost_after_shipping and product.cost_after_shipping > 0:
                    unit_cost = float(product.cost_after_shipping)
                elif product.cost_before_shipping and product.cost_before_shipping > 0:
                    unit_cost = float(product.cost_before_shipping)
                elif product.price and product.price > 0:
                    unit_cost = float(product.price) * 0.70  # 70% من سعر البيع
                    current_app.logger.warning(
                        f"⚠️ تقدير تكلفة قطعة الغيار '{product.name}' في الخدمات: "
                        f"70% من سعر البيع = {unit_cost:.2f} ₪"
                    )
                    if product.id not in [p['id'] for p in estimated_products]:
                        estimated_products.append({
                            'id': product.id,
                            'name': product.name,
                            'selling_price': float(product.price),
                            'estimated_cost': unit_cost,
                            'qty_sold': qty_used,
                            'in_service': True
                        })
                else:
                    current_app.logger.error(
                        f"❌ قطعة الغيار '{product.name}' بدون تكلفة - تم تجاهلها من حساب تكاليف الخدمات"
                    )
                    if product.id not in [p['id'] for p in products_without_cost]:
                        products_without_cost.append({
                            'id': product.id,
                            'name': product.name,
                            'qty_sold': qty_used,
                            'in_service': True
                        })
                    continue
                
                total_service_costs += qty_used * unit_cost
        
        # 6. حساب الحجوزات المسبقة
        preorders_query = PreOrder.query
        if from_date:
            preorders_query = preorders_query.filter(PreOrder.created_at >= from_date)
        if to_date:
            preorders_query = preorders_query.filter(PreOrder.created_at <= to_date)
        
        total_preorders = 0.0
        for preorder in preorders_query.limit(10000).all():
            amount = float(preorder.total_amount or 0)
            preorder_currency = getattr(preorder, 'currency', 'ILS') or 'ILS'
            if preorder_currency != 'ILS':
                try:
                    rate = fx_rate(preorder_currency, 'ILS', preorder.created_at or datetime.utcnow(), raise_on_missing=False)
                    if rate > 0:
                        amount = float(amount * float(rate))
                except Exception as e:
                    current_app.logger.warning(f"⚠️ خطأ في تحويل عملة الحجز المسبق #{preorder.id}: {str(e)}")
            total_preorders += amount
        
        # 7. حساب قيمة المخزون (مجمّع حسب المنتج) - بسعر التكلفة
        total_stock_value_stats = 0.0
        total_stock_qty_stats = 0
        
        stock_summary_stats = (
            db.session.query(
                Product.id,
                Product.name,
                Product.purchase_price,
                Product.currency,
                func.sum(StockLevel.quantity).label('total_qty')
            )
            .join(StockLevel, StockLevel.product_id == Product.id)
            .filter(StockLevel.quantity > 0)
            .group_by(Product.id, Product.name, Product.purchase_price, Product.currency)
            .all()
        )
        
        for row in stock_summary_stats:
            qty = float(row.total_qty or 0)
            price = float(row.purchase_price or 0)  # سعر التكلفة وليس سعر البيع
            product_currency = row.currency
            
            # تحويل للشيقل
            if product_currency and product_currency != 'ILS' and price > 0:
                try:
                    rate = fx_rate(product_currency, 'ILS', datetime.utcnow(), raise_on_missing=False)
                    if rate and rate > 0:
                        price = float(price * float(rate))
                except Exception:
                    pass
            
            total_stock_value_stats += qty * price
            total_stock_qty_stats += int(qty)
        
        # 8. صافي الربح الحقيقي
        gross_profit_sales = total_sales - total_cogs  # ربح المبيعات
        gross_profit_services = total_services - total_service_costs  # ربح الخدمات
        total_gross_profit = gross_profit_sales + gross_profit_services
        net_profit = total_gross_profit - total_expenses  # الربح الصافي
        
        statistics = {
            "total_sales": total_sales,
            "total_cogs": total_cogs,
            "gross_profit_sales": gross_profit_sales,
            "total_services": total_services,
            "total_service_costs": total_service_costs,
            "gross_profit_services": gross_profit_services,
            "total_gross_profit": total_gross_profit,
            "total_revenue": total_sales + total_services,
            "total_expenses": total_expenses,
            "net_profit": net_profit,
            "profit_margin": (net_profit / (total_sales + total_services) * 100) if (total_sales + total_services) > 0 else 0,
            "total_preorders": total_preorders,
            "total_stock_value": total_stock_value_stats,
            "total_stock_qty": total_stock_qty_stats,
            "cogs_details": cogs_details,
            "estimated_products_count": len(estimated_products),
            "estimated_products": estimated_products,
            "products_without_cost_count": len(products_without_cost),
            "products_without_cost": products_without_cost
        }
        
        search_term = (request.args.get('q') or '').strip()
        filtered_entries = ledger_entries
        if search_term:
            search_lower = search_term.lower()

            def _entry_matches(entry):
                fields = [
                    entry.get("transaction_number"),
                    entry.get("type"),
                    entry.get("type_ar"),
                    entry.get("description"),
                    entry.get("entity_name"),
                    entry.get("entity_type"),
                    entry.get("date"),
                ]
                for field in fields:
                    if field and search_lower in str(field).lower():
                        return True
                for numeric in (entry.get("debit"), entry.get("credit"), entry.get("balance")):
                    if numeric is not None and search_lower in f"{numeric}".lower():
                        return True
                payment_details = entry.get("payment_details")
                if isinstance(payment_details, dict):
                    for value in payment_details.values():
                        if value and search_lower in str(value).lower():
                            return True
                return False

            filtered_entries = [entry for entry in ledger_entries if _entry_matches(entry)]

        page = request.args.get('page', 1, type=int) or 1
        total_entries = len(filtered_entries)
        per_page_param = (request.args.get('per_page') or '').strip().lower()
        if per_page_param in {'all', 'max', '*', '0', '-1'}:
            per_page = total_entries if total_entries > 0 else 1
        else:
            try:
                per_page_value = int(per_page_param) if per_page_param else 25
            except ValueError:
                per_page_value = 25
            per_page = max(10, min(per_page_value, 500))
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_entries = filtered_entries[start_idx:end_idx]
        
        # حساب إجماليات البيانات (لدفتر الأستاذ)
        ledger_totals = {
            'total_debit': sum(entry['debit'] for entry in filtered_entries),
            'total_credit': sum(entry['credit'] for entry in filtered_entries),
            'final_balance': filtered_entries[-1]['balance'] if filtered_entries else 0
        }
        
        return jsonify({
            "data": paginated_entries,
            "statistics": statistics,
            "totals": ledger_totals,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total_entries,
                "pages": (total_entries + per_page - 1) // per_page if total_entries > 0 else 1
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error in get_ledger_data: {str(e)}")
        return jsonify({"error": str(e), "data": [], "statistics": {}}), 500

@ledger_bp.route("/cogs-audit", methods=["GET"], endpoint="cogs_audit_report")
@login_required
def cogs_audit_report():
    """تقرير شامل لفحص تكلفة البضاعة المباعة (COGS) بدقة"""
    try:
        from models import SaleLine, fx_rate
        
        from_date_str = request.args.get('from_date')
        to_date_str = request.args.get('to_date')
        
        from_date = datetime.strptime(from_date_str, '%Y-%m-%d') if from_date_str else None
        to_date = datetime.strptime(to_date_str, '%Y-%m-%d').replace(hour=23, minute=59, second=59) if to_date_str else None
        
        sale_lines_query = (
            db.session.query(SaleLine)
            .join(Sale, Sale.id == SaleLine.sale_id)
            .filter(Sale.status == 'CONFIRMED')
        )
        if from_date:
            sale_lines_query = sale_lines_query.filter(Sale.sale_date >= from_date)
        if to_date:
            sale_lines_query = sale_lines_query.filter(Sale.sale_date <= to_date)
        
        products_audit = []
        total_cogs_actual = 0.0
        total_cogs_estimated = 0.0
        total_cogs_missing = 0.0
        total_sales_value = 0.0
        
        estimated_count = 0
        missing_count = 0
        actual_count = 0
        
        for line in sale_lines_query.limit(100000).all():
            if not line.product:
                continue
                
            product = line.product
            qty_sold = float(line.quantity or 0)
            unit_price = float(line.unit_price or 0)
            line_total = qty_sold * unit_price
            
            sale_currency = line.sale.currency or 'ILS'
            if sale_currency != 'ILS':
                try:
                    rate = fx_rate(sale_currency, 'ILS', line.sale.sale_date, raise_on_missing=False)
                    if rate > 0:
                        line_total = float(line_total * float(rate))
                except Exception:
                    pass
            
            total_sales_value += line_total
            
            unit_cost = None
            cost_source = None
            cost_status = None
            
            if product.purchase_price and product.purchase_price > 0:
                unit_cost = float(product.purchase_price)
                cost_source = "purchase_price"
                cost_status = "actual"
                actual_count += 1
            elif product.cost_after_shipping and product.cost_after_shipping > 0:
                unit_cost = float(product.cost_after_shipping)
                cost_source = "cost_after_shipping"
                cost_status = "actual"
                actual_count += 1
            elif product.cost_before_shipping and product.cost_before_shipping > 0:
                unit_cost = float(product.cost_before_shipping)
                cost_source = "cost_before_shipping"
                cost_status = "actual"
                actual_count += 1
            elif product.price and product.price > 0:
                unit_cost = float(product.price) * 0.70
                cost_source = "estimated_70%"
                cost_status = "estimated"
                estimated_count += 1
            else:
                unit_cost = 0.0
                cost_source = "missing"
                cost_status = "missing"
                missing_count += 1
            
            line_cogs = qty_sold * unit_cost
            
            if cost_status == "actual":
                total_cogs_actual += line_cogs
            elif cost_status == "estimated":
                total_cogs_estimated += line_cogs
            else:
                total_cogs_missing += line_cogs
            
            products_audit.append({
                'product_id': product.id,
                'product_name': product.name,
                'product_sku': product.sku or 'N/A',
                'sale_id': line.sale_id,
                'sale_number': line.sale.sale_number or f'SAL-{line.sale_id}',
                'sale_date': line.sale.sale_date.strftime('%Y-%m-%d') if line.sale.sale_date else 'N/A',
                'qty_sold': qty_sold,
                'unit_price': unit_price,
                'line_total': line_total,
                'unit_cost': unit_cost,
                'cost_source': cost_source,
                'cost_status': cost_status,
                'line_cogs': line_cogs,
                'gross_profit': line_total - line_cogs,
                'profit_margin': ((line_total - line_cogs) / line_total * 100) if line_total > 0 else 0,
                'purchase_price': float(product.purchase_price) if product.purchase_price else None,
                'cost_after_shipping': float(product.cost_after_shipping) if product.cost_after_shipping else None,
                'cost_before_shipping': float(product.cost_before_shipping) if product.cost_before_shipping else None,
                'selling_price': float(product.price) if product.price else None
            })
        
        total_cogs = total_cogs_actual + total_cogs_estimated + total_cogs_missing
        total_gross_profit = total_sales_value - total_cogs
        overall_margin = (total_gross_profit / total_sales_value * 100) if total_sales_value > 0 else 0
        
        summary = {
            'total_products_sold': len(products_audit),
            'total_sales_value': total_sales_value,
            'total_cogs': total_cogs,
            'total_cogs_actual': total_cogs_actual,
            'total_cogs_estimated': total_cogs_estimated,
            'total_cogs_missing': total_cogs_missing,
            'total_gross_profit': total_gross_profit,
            'overall_margin': overall_margin,
            'actual_count': actual_count,
            'estimated_count': estimated_count,
            'missing_count': missing_count,
            'actual_percentage': (actual_count / len(products_audit) * 100) if products_audit else 0,
            'estimated_percentage': (estimated_count / len(products_audit) * 100) if products_audit else 0,
            'missing_percentage': (missing_count / len(products_audit) * 100) if products_audit else 0,
            'estimated_impact': (total_cogs_estimated / total_cogs * 100) if total_cogs > 0 else 0,
            'missing_impact': (total_cogs_missing / total_cogs * 100) if total_cogs > 0 else 0
        }
        
        return jsonify({
            'success': True,
            'summary': summary,
            'products': products_audit,
            'from_date': from_date_str,
            'to_date': to_date_str
        })
        
    except Exception as e:
        current_app.logger.error(f"Error in cogs_audit_report: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@ledger_bp.route("/accounts-summary", methods=["GET"], endpoint="get_accounts_summary")
@login_required
def get_accounts_summary():
    """جلب ملخص الحسابات (ميزان مراجعة مبسط) من قيود GL مباشرة"""
    try:
        from_date_str = request.args.get("from_date")
        to_date_str = request.args.get("to_date")

        from_date = datetime.strptime(from_date_str, "%Y-%m-%d") if from_date_str else None
        to_date = (
            datetime.strptime(to_date_str, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
            if to_date_str
            else None
        )

        base_q = (
            db.session.query(
                GLEntry.account,
                Account.name,
                Account.type,
                func.sum(GLEntry.debit).label("td"),
                func.sum(GLEntry.credit).label("tc"),
            )
            .join(Account, Account.code == GLEntry.account)
            .join(GLBatch)
            .filter(GLBatch.status == "POSTED")
        )
        if from_date:
            base_q = base_q.filter(GLBatch.posted_at >= from_date)
        if to_date:
            base_q = base_q.filter(GLBatch.posted_at <= to_date)

        rows = base_q.group_by(GLEntry.account, Account.name, Account.type).all()

        groups = {
            "المبيعات": {"debit": 0.0, "credit": 0.0},
            "الخدمات (الصيانة)": {"debit": 0.0, "credit": 0.0},
            "تكلفة البضاعة المباعة (COGS)": {"debit": 0.0, "credit": 0.0},
            "المشتريات والنفقات": {"debit": 0.0, "credit": 0.0},
            "الخزينة": {"debit": 0.0, "credit": 0.0},
            "المخزون": {"debit": 0.0, "credit": 0.0},
            "ذمم العملاء": {"debit": 0.0, "credit": 0.0},
            "ذمم الموردين والخصوم الأخرى": {"debit": 0.0, "credit": 0.0},
            "الضرائب المستحقة": {"debit": 0.0, "credit": 0.0},
            "حقوق الملكية": {"debit": 0.0, "credit": 0.0},
            "أصول أخرى": {"debit": 0.0, "credit": 0.0},
        }

        for r in rows:
            code = (r.account or "").upper()
            acc_type = (r.type or "").upper()
            debit = float(r.td or 0)
            credit = float(r.tc or 0)

            if acc_type == "REVENUE":
                if code.startswith("4000"):
                    g = groups["المبيعات"]
                elif code.startswith("4100"):
                    g = groups["الخدمات (الصيانة)"]
                else:
                    g = groups["المبيعات"]
            elif acc_type == "EXPENSE":
                if code.startswith("51"):
                    g = groups["تكلفة البضاعة المباعة (COGS)"]
                else:
                    g = groups["المشتريات والنفقات"]
            elif acc_type == "ASSET":
                if code in {"1000_CASH", "1010_BANK", "1020_CARD_CLEARING"} or code.startswith("10"):
                    g = groups["الخزينة"]
                elif code.startswith("11"):
                    g = groups["ذمم العملاء"]
                elif code.startswith("12") or code.startswith("13"):
                    g = groups["المخزون"]
                else:
                    g = groups["أصول أخرى"]
            elif acc_type == "LIABILITY":
                if code.startswith("2100"):
                    g = groups["الضرائب المستحقة"]
                else:
                    g = groups["ذمم الموردين والخصوم الأخرى"]
            elif acc_type == "EQUITY":
                g = groups["حقوق الملكية"]
            else:
                continue

            g["debit"] += debit
            g["credit"] += credit

        order = [
            "المبيعات",
            "الخدمات (الصيانة)",
            "تكلفة البضاعة المباعة (COGS)",
            "المشتريات والنفقات",
            "الخزينة",
            "المخزون",
            "ذمم العملاء",
            "ذمم الموردين والخصوم الأخرى",
            "الضرائب المستحقة",
            "حقوق الملكية",
            "أصول أخرى",
        ]
        accounts = []
        total_debit = 0.0
        total_credit = 0.0
        for name in order:
            g = groups.get(name)
            if not g:
                continue
            if abs(g["debit"]) < 0.01 and abs(g["credit"]) < 0.01:
                continue
            accounts.append(
                {
                    "name": name,
                    "debit_balance": g["debit"],
                    "credit_balance": g["credit"],
                }
            )
            total_debit += g["debit"]
            total_credit += g["credit"]

        accounts_totals = {
            "total_debit": total_debit,
            "total_credit": total_credit,
            "net_balance": total_debit - total_credit,
        }

        return jsonify({"accounts": accounts, "totals": accounts_totals})

    except Exception as e:
        error_msg = f"Error in get_accounts_summary: {str(e)}"
        current_app.logger.error(error_msg)
        return jsonify({"error": str(e)}), 500

@ledger_bp.route("/receivables-detailed-summary", methods=["GET"], endpoint="get_receivables_detailed_summary")
@login_required
def get_receivables_detailed_summary():
    """جلب ملخص الذمم التفصيلي مع أعمار الديون"""
    try:
        from_date_str = request.args.get('from_date')
        to_date_str = request.args.get('to_date')
        
        from_date = datetime.strptime(from_date_str, '%Y-%m-%d') if from_date_str else None
        to_date = datetime.strptime(to_date_str, '%Y-%m-%d').replace(hour=23, minute=59, second=59) if to_date_str else None
        
        receivables = []
        today = datetime.utcnow()
        
        # 1. العملاء (Customers) مع أعمار الديون
        from models import fx_rate
        
        customers = Customer.query.limit(10000).all()
        for customer in customers:
            from decimal import Decimal
            
            db.session.refresh(customer)
            balance = Decimal(str(customer.current_balance or 0))
            
            if balance == 0:
                continue
            
            oldest_date = None
            last_payment_date = None
            
            oldest_sale = Sale.query.filter(Sale.customer_id == customer.id, Sale.status == 'CONFIRMED').order_by(Sale.sale_date.asc()).first()
            if oldest_sale and oldest_sale.sale_date:
                oldest_date = oldest_sale.sale_date
            
            oldest_invoice = Invoice.query.filter(Invoice.customer_id == customer.id, Invoice.cancelled_at.is_(None)).order_by(Invoice.invoice_date.asc()).first()
            if oldest_invoice:
                ref_dt = oldest_invoice.invoice_date or oldest_invoice.created_at
                if ref_dt and (oldest_date is None or ref_dt < oldest_date):
                    oldest_date = ref_dt
            
            oldest_service = ServiceRequest.query.filter(ServiceRequest.customer_id == customer.id).order_by(ServiceRequest.received_at.asc()).first()
            if oldest_service:
                ref_dt = oldest_service.received_at or oldest_service.created_at
                if ref_dt and (oldest_date is None or ref_dt < oldest_date):
                    oldest_date = ref_dt
            
            last_payment = Payment.query.filter(
                Payment.customer_id == customer.id
            ).order_by(Payment.payment_date.desc()).first()
            if not last_payment:
                last_payment = Payment.query.join(Sale, Payment.sale_id == Sale.id).filter(
                    Sale.customer_id == customer.id
                ).order_by(Payment.payment_date.desc()).first()
            if not last_payment:
                last_payment = Payment.query.join(Invoice, Payment.invoice_id == Invoice.id).filter(
                    Invoice.customer_id == customer.id
                ).order_by(Payment.payment_date.desc()).first()
            
            if last_payment and last_payment.payment_date:
                last_payment_date = last_payment.payment_date
            
            days_overdue = 0
            if balance < 0 and oldest_date:
                days_overdue = (today - oldest_date).days
            
            last_transaction = last_payment_date if last_payment_date else oldest_date
            last_transaction_str = last_transaction.strftime('%Y-%m-%d') if last_transaction else None
            
            receivables.append({
                "name": customer.name,
                "type": "customer",
                "type_ar": "عميل",
                "balance": float(balance),
                "debit": float(abs(balance)) if balance < 0 else 0.0,
                "credit": float(balance) if balance > 0 else 0.0,
                "days_overdue": days_overdue,
                "last_transaction": last_transaction_str
            })
        
        # 2. الموردين (Suppliers) مع أعمار الديون
        suppliers = Supplier.query.limit(10000).all()
        for supplier in suppliers:
            # حساب المشتريات من المورد (النفقات)
            expenses_query = Expense.query.filter(
                Expense.payee_type == 'SUPPLIER',
                Expense.payee_entity_id == supplier.id
            )
            if from_date:
                expenses_query = expenses_query.filter(Expense.date >= from_date)
            if to_date:
                expenses_query = expenses_query.filter(Expense.date <= to_date)
            
            total_purchases = 0.0
            oldest_expense_date = None
            
            for expense in expenses_query.limit(10000).all():
                amount = float(expense.amount or 0)
                if expense.currency and expense.currency != 'ILS':
                    try:
                        rate = fx_rate(expense.currency, 'ILS', expense.date, raise_on_missing=False)
                        if rate > 0:
                            amount = float(amount * float(rate))
                    except Exception:
                        pass
                total_purchases += amount
                
                if not oldest_expense_date or expense.date < oldest_expense_date:
                    oldest_expense_date = expense.date
            
            # حساب الدفعات للمورد
            payments_query = Payment.query.filter(
                Payment.supplier_id == supplier.id,
                Payment.direction == 'OUT',
                Payment.status == 'COMPLETED'
            )
            if from_date:
                payments_query = payments_query.filter(Payment.payment_date >= from_date)
            if to_date:
                payments_query = payments_query.filter(Payment.payment_date <= to_date)
            
            total_payments = 0.0
            last_payment_date = None
            
            for payment in payments_query.limit(10000).all():
                amount = float(payment.total_amount or 0)
                if payment.currency and payment.currency != 'ILS':
                    try:
                        rate = fx_rate(payment.currency, 'ILS', payment.payment_date, raise_on_missing=False)
                        if rate > 0:
                            amount = float(amount * float(rate))
                    except Exception:
                        pass
                total_payments += amount
                
                if not last_payment_date or payment.payment_date > last_payment_date:
                    last_payment_date = payment.payment_date
            
            # حساب عمر الدين
            days_overdue = 0
            if total_purchases > total_payments and oldest_expense_date:
                days_overdue = (today - oldest_expense_date).days
            
            # آخر حركة
            last_transaction = last_payment_date if last_payment_date else oldest_expense_date
            last_transaction_str = last_transaction.strftime('%Y-%m-%d') if last_transaction else None
            
            if total_purchases > 0 or total_payments > 0:
                receivables.append({
                    "name": supplier.name,
                    "type": "supplier",
                    "type_ar": "مورد",
                    "debit": total_payments,
                    "credit": total_purchases,
                    "balance": float(total_purchases - total_payments),
                    "days_overdue": days_overdue,
                    "last_transaction": last_transaction_str
                })
        
        # 3. الشركاء (Partners)
        partners = Partner.query.limit(10000).all()
        for partner in partners:
            # حساب النفقات المرتبطة بالشريك
            expenses_query = Expense.query.filter(
                Expense.payee_type == 'PARTNER',
                Expense.payee_entity_id == partner.id
            )
            if from_date:
                expenses_query = expenses_query.filter(Expense.date >= from_date)
            if to_date:
                expenses_query = expenses_query.filter(Expense.date <= to_date)
            
            total_expenses = 0.0
            oldest_expense_date = None
            
            for expense in expenses_query.limit(10000).all():
                amount = float(expense.amount or 0)
                if expense.currency and expense.currency != 'ILS':
                    try:
                        rate = fx_rate(expense.currency, 'ILS', expense.date, raise_on_missing=False)
                        if rate > 0:
                            amount = float(amount * float(rate))
                    except Exception:
                        pass
                total_expenses += amount
                
                if not oldest_expense_date or expense.date < oldest_expense_date:
                    oldest_expense_date = expense.date
            
            # حساب الدفعات من/إلى الشريك
            payments_in_query = Payment.query.filter(
                Payment.partner_id == partner.id,
                Payment.direction == 'IN',
                Payment.status == 'COMPLETED'
            )
            payments_out_query = Payment.query.filter(
                Payment.partner_id == partner.id,
                Payment.direction == 'OUT',
                Payment.status == 'COMPLETED'
            )
            
            if from_date:
                payments_in_query = payments_in_query.filter(Payment.payment_date >= from_date)
                payments_out_query = payments_out_query.filter(Payment.payment_date >= from_date)
            if to_date:
                payments_in_query = payments_in_query.filter(Payment.payment_date <= to_date)
                payments_out_query = payments_out_query.filter(Payment.payment_date <= to_date)
            
            total_in = 0.0
            total_out = 0.0
            last_payment_date = None
            
            for payment in payments_in_query.all():
                amount = float(payment.total_amount or 0)
                if payment.currency and payment.currency != 'ILS':
                    try:
                        rate = fx_rate(payment.currency, 'ILS', payment.payment_date, raise_on_missing=False)
                        if rate > 0:
                            amount = float(amount * float(rate))
                    except Exception:
                        pass
                total_in += amount
                
                if not last_payment_date or payment.payment_date > last_payment_date:
                    last_payment_date = payment.payment_date
            
            for payment in payments_out_query.all():
                amount = float(payment.total_amount or 0)
                if payment.currency and payment.currency != 'ILS':
                    try:
                        rate = fx_rate(payment.currency, 'ILS', payment.payment_date, raise_on_missing=False)
                        if rate > 0:
                            amount = float(amount * float(rate))
                    except Exception:
                        pass
                total_out += amount
                
                if not last_payment_date or payment.payment_date > last_payment_date:
                    last_payment_date = payment.payment_date
            
            # حساب عمر الدين
            days_overdue = 0
            balance = (total_in + total_expenses) - total_out
            if balance < 0 and oldest_expense_date:
                days_overdue = (today - oldest_expense_date).days
            
            # آخر حركة
            last_transaction = last_payment_date if last_payment_date else oldest_expense_date
            last_transaction_str = last_transaction.strftime('%Y-%m-%d') if last_transaction else None
            
            if total_in > 0 or total_out > 0 or total_expenses > 0:
                receivables.append({
                    "name": partner.name,
                    "type": "partner",
                    "type_ar": "شريك",
                    "debit": total_in + total_expenses,
                    "credit": total_out,
                    "balance": float(total_out - (total_in + total_expenses)),
                    "days_overdue": days_overdue,
                    "last_transaction": last_transaction_str
                })
        
        # حساب إجماليات الذمم من الباكند
        receivables_totals = {
            'total_debit': sum([r['debit'] for r in receivables]),
            'total_credit': sum([r['credit'] for r in receivables]),
            'net_balance': sum([r['credit'] for r in receivables]) - sum([r['debit'] for r in receivables])
        }
        
        return jsonify({
            'receivables': receivables,
            'totals': receivables_totals
        })
        
    except Exception as e:
        current_app.logger.error(f"Error in get_receivables_detailed_summary: {str(e)}")
        return jsonify([]), 500

@ledger_bp.route("/receivables-summary", methods=["GET"], endpoint="get_receivables_summary")
@login_required
def get_receivables_summary():
    """جلب ملخص الذمم (العملاء، الموردين، الشركاء)"""
    try:
        from_date_str = request.args.get('from_date')
        to_date_str = request.args.get('to_date')
        
        from_date = datetime.strptime(from_date_str, '%Y-%m-%d') if from_date_str else None
        to_date = datetime.strptime(to_date_str, '%Y-%m-%d').replace(hour=23, minute=59, second=59) if to_date_str else None
        
        receivables = []
        
        # 1. العملاء (Customers) - من دفتر الأستاذ
        cust_query = db.session.query(
            GLBatch.entity_id,
            func.sum(GLEntry.debit).label('debit'),
            func.sum(GLEntry.credit).label('credit')
        ).join(GLEntry, GLBatch.id == GLEntry.batch_id).filter(
            GLBatch.entity_type == 'CUSTOMER',
            GLEntry.account == '1100_AR'
        )
        
        if from_date:
            cust_query = cust_query.filter(GLBatch.posted_at >= from_date)
        if to_date:
            cust_query = cust_query.filter(GLBatch.posted_at <= to_date)
            
        cust_rows = cust_query.group_by(GLBatch.entity_id).all()
        
        if cust_rows:
            c_ids = [r.entity_id for r in cust_rows]
            c_map = {c.id: c.name for c in Customer.query.filter(Customer.id.in_(c_ids)).all()}
            
            for r in cust_rows:
                if (r.debit or 0) > 0 or (r.credit or 0) > 0:
                    receivables.append({
                        "name": c_map.get(r.entity_id, f"Client #{r.entity_id}"),
                        "type": "customer",
                        "type_ar": "عميل",
                        "debit": float(r.debit or 0),
                        "credit": float(r.credit or 0)
                    })

        # 2. الموردين (Suppliers) - من دفتر الأستاذ
        supp_query = db.session.query(
            GLBatch.entity_id,
            func.sum(GLEntry.debit).label('debit'),
            func.sum(GLEntry.credit).label('credit')
        ).join(GLEntry, GLBatch.id == GLEntry.batch_id).filter(
            GLBatch.entity_type == 'SUPPLIER',
            GLEntry.account == '2000_AP'
        )
        
        if from_date:
            supp_query = supp_query.filter(GLBatch.posted_at >= from_date)
        if to_date:
            supp_query = supp_query.filter(GLBatch.posted_at <= to_date)
            
        supp_rows = supp_query.group_by(GLBatch.entity_id).all()
        
        if supp_rows:
            s_ids = [r.entity_id for r in supp_rows]
            s_map = {s.id: s.name for s in Supplier.query.filter(Supplier.id.in_(s_ids)).all()}
            
            for r in supp_rows:
                if (r.debit or 0) > 0 or (r.credit or 0) > 0:
                    receivables.append({
                        "name": s_map.get(r.entity_id, f"Supplier #{r.entity_id}"),
                        "type": "supplier",
                        "type_ar": "مورد",
                        "debit": float(r.debit or 0),
                        "credit": float(r.credit or 0)
                    })
        
        # 3. الشركاء (Partners) - من دفتر الأستاذ
        partner_query = db.session.query(
            GLBatch.entity_id,
            func.sum(GLEntry.debit).label('debit'),
            func.sum(GLEntry.credit).label('credit')
        ).join(GLEntry, GLBatch.id == GLEntry.batch_id).filter(
            GLBatch.entity_type == 'PARTNER',
            GLEntry.account == '2000_AP'
        )
        
        if from_date:
            partner_query = partner_query.filter(GLBatch.posted_at >= from_date)
        if to_date:
            partner_query = partner_query.filter(GLBatch.posted_at <= to_date)
        
        partner_rows = partner_query.group_by(GLBatch.entity_id).all()
        
        if partner_rows:
            p_ids = [r.entity_id for r in partner_rows]
            p_map = {p.id: p.name for p in Partner.query.filter(Partner.id.in_(p_ids)).all()}
            
            for r in partner_rows:
                if (r.debit or 0) > 0 or (r.credit or 0) > 0:
                    receivables.append({
                        "name": p_map.get(r.entity_id, f"Partner #{r.entity_id}"),
                        "type": "partner",
                        "type_ar": "شريك",
                        "debit": float(r.debit or 0),
                        "credit": float(r.credit or 0)
                    })
        
        return jsonify(receivables)
        
    except Exception as e:
        current_app.logger.error(f"Error in get_receivables_summary: {str(e)}")
        return jsonify([]), 500

@ledger_bp.route("/export", methods=["GET"], endpoint="export_ledger")
@login_required
def export_ledger():
    """تصدير دفتر الأستاذ"""
    # يمكن إضافة منطق التصدير هنا
    return "تصدير دفتر الأستاذ - قريباً"

@ledger_bp.route("/transaction/<int:id>", methods=["GET"], endpoint="view_transaction")
@login_required
def view_transaction(id):
    """عرض تفاصيل العملية"""
    # يمكن إضافة منطق عرض التفاصيل هنا
    return f"تفاصيل العملية رقم {id} - قريباً"

def _parse_dates():
    s_from = request.args.get("from", "").strip()
    s_to = request.args.get("to", "").strip()
    def _parse_one(s, end=False):
        if not s:
            return None
        try:
            if len(s) == 10:
                dt = datetime.strptime(s, "%Y-%m-%d")
                return dt.replace(hour=23, minute=59, second=59, microsecond=999999) if end else dt.replace(hour=0, minute=0, second=0, microsecond=0)
            return datetime.fromisoformat(s)
        except Exception:
            return None
    now = datetime.utcnow()
    if not s_from:
        dfrom = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        dfrom = _parse_one(s_from, end=False) or now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if not s_to:
        dto = now
    else:
        dto = _parse_one(s_to, end=True) or now
    dto_excl = dto + timedelta(microseconds=1)
    return dfrom, dto_excl

def _entity_filter(q):
    et = (request.args.get("entity_type") or "").strip()
    eid = request.args.get("entity_id", type=int)
    if et and eid:
        q = q.filter(GLBatch.entity_type == et.upper(), GLBatch.entity_id == eid)
    return q

def _get_pagination():
    page = request.args.get("page", type=int)
    per_page = request.args.get("per_page", type=int)
    if page and page > 0:
        pp = 10 if not per_page else max(1, min(per_page, 200))
        return page, pp
    return None, None

@ledger_bp.get("/trial-balance")
@login_required
def trial_balance():
    dfrom, dto = _parse_dates()
    q = (db.session.query(
            GLEntry.account.label("account"),
            func.coalesce(func.sum(GLEntry.debit), 0.0).label("debit"),
            func.coalesce(func.sum(GLEntry.credit), 0.0).label("credit")
        )
        .join(GLBatch, GLBatch.id == GLEntry.batch_id)
        .filter(GLBatch.posted_at >= dfrom, GLBatch.posted_at < dto)
    )
    q = _entity_filter(q)
    rows = q.group_by(GLEntry.account).order_by(GLEntry.account.asc()).all()
    data = []
    for r in rows:
        dr = float(r.debit or 0.0)
        cr = float(r.credit or 0.0)
        net = dr - cr
        side = "DR" if net >= 0 else "CR"
        data.append({"account": r.account, "debit": dr, "credit": cr, "net": abs(net), "side": side})
    return jsonify({"from": dfrom.isoformat(), "to": (dto - timedelta(microseconds=1)).isoformat(), "rows": data})

@ledger_bp.get("/account/<account>")
@login_required
def account_ledger(account):
    dfrom, dto = _parse_dates()
    
    account_obj = Account.query.filter_by(code=account).first()
    is_asset_or_expense = True
    if account_obj:
        acc_type = (account_obj.type or "").upper()
        is_asset_or_expense = acc_type in ["ASSET", "EXPENSE"]
    
    if is_asset_or_expense:
        q_open = (db.session.query(func.coalesce(func.sum(GLEntry.debit - GLEntry.credit), 0.0))
                  .join(GLBatch, GLBatch.id == GLEntry.batch_id)
                  .filter(GLEntry.account == account, GLBatch.posted_at < dfrom))
    else:
        q_open = (db.session.query(func.coalesce(func.sum(GLEntry.credit - GLEntry.debit), 0.0))
                  .join(GLBatch, GLBatch.id == GLEntry.batch_id)
                  .filter(GLEntry.account == account, GLBatch.posted_at < dfrom))
    q_open = _entity_filter(q_open)
    opening = float(q_open.scalar() or 0.0)
    base = (db.session.query(
                GLBatch.posted_at.label("posted_at"),
                GLBatch.source_type.label("source_type"),
                GLBatch.source_id.label("source_id"),
                GLBatch.purpose.label("purpose"),
                GLBatch.memo.label("memo"),
                GLBatch.entity_type.label("entity_type"),
                GLBatch.entity_id.label("entity_id"),
                GLEntry.debit.label("debit"),
                GLEntry.credit.label("credit"),
                GLEntry.ref.label("ref"),
                GLEntry.id.label("entry_id")
            )
            .join(GLBatch, GLBatch.id == GLEntry.batch_id)
            .filter(GLEntry.account == account, GLBatch.posted_at >= dfrom, GLBatch.posted_at < dto)
            .order_by(GLBatch.posted_at.asc(), GLEntry.id.asc()))
    base = _entity_filter(base)
    page, per_page = _get_pagination()
    if page:
        total = base.count()
        offset = (page - 1) * per_page
        rows = base.limit(per_page).offset(offset).all()
        running_start = opening
        if rows:
            first = rows[0]
            if is_asset_or_expense:
                q_prefix = (db.session.query(func.coalesce(func.sum(GLEntry.debit - GLEntry.credit), 0.0))
                            .join(GLBatch, GLBatch.id == GLEntry.batch_id)
                            .filter(GLEntry.account == account,
                                    or_(GLBatch.posted_at < first.posted_at,
                                        and_(GLBatch.posted_at == first.posted_at, GLEntry.id < first.entry_id))))
            else:
                q_prefix = (db.session.query(func.coalesce(func.sum(GLEntry.credit - GLEntry.debit), 0.0))
                            .join(GLBatch, GLBatch.id == GLEntry.batch_id)
                            .filter(GLEntry.account == account,
                                    or_(GLBatch.posted_at < first.posted_at,
                                        and_(GLBatch.posted_at == first.posted_at, GLEntry.id < first.entry_id))))
            q_prefix = _entity_filter(q_prefix).filter(GLBatch.posted_at >= dfrom, GLBatch.posted_at < dto)
            running_start += float(q_prefix.scalar() or 0.0)
        running = running_start
        lines = []
        for r in rows:
            dr = float(r.debit or 0.0)
            cr = float(r.credit or 0.0)
            if is_asset_or_expense:
                running += (dr - cr)
            else:
                running += (cr - dr)
            
            # 🧠 استخراج الجهة بذكاء من batch
            batch_obj = GLBatch(
                source_type=r.source_type,
                source_id=r.source_id,
                entity_type=r.entity_type,
                entity_id=r.entity_id
            )
            entity_name, entity_type_ar, _, _ = extract_entity_from_batch(batch_obj)
            
            lines.append({
                "date": r.posted_at.isoformat(),
                "source": f"{r.source_type}:{r.source_id}",
                "purpose": r.purpose,
                "memo": r.memo,
                "ref": r.ref,
                "entity_type": r.entity_type,
                "entity_id": r.entity_id,
                "entity_name": entity_name,  # ✅ إضافة اسم الجهة
                "entity_type_ar": entity_type_ar,  # ✅ إضافة نوع الجهة بالعربي
                "debit": dr,
                "credit": cr,
                "balance": running
            })
        closing = None
        return jsonify({
            "account": account,
            "from": dfrom.isoformat(),
            "to": (dto - timedelta(microseconds=1)).isoformat(),
            "opening_balance": opening,
            "closing_balance": closing,
            "page": page,
            "per_page": per_page,
            "total": total,
            "lines": lines
        })
    rows = base.all()
    running = opening
    lines = []
    for r in rows:
        dr = float(r.debit or 0.0)
        cr = float(r.credit or 0.0)
        if is_asset_or_expense:
            running += (dr - cr)
        else:
            running += (cr - dr)
        
        # 🧠 استخراج الجهة بذكاء من batch
        batch_obj = GLBatch(
            source_type=r.source_type,
            source_id=r.source_id,
            entity_type=r.entity_type,
            entity_id=r.entity_id
        )
        entity_name, entity_type_ar, _, _ = extract_entity_from_batch(batch_obj)
        
        lines.append({
            "date": r.posted_at.isoformat(),
            "source": f"{r.source_type}:{r.source_id}",
            "purpose": r.purpose,
            "memo": r.memo,
            "ref": r.ref,
            "entity_type": r.entity_type,
            "entity_id": r.entity_id,
            "entity_name": entity_name,  # ✅ إضافة اسم الجهة
            "entity_type_ar": entity_type_ar,  # ✅ إضافة نوع الجهة بالعربي
            "debit": dr,
            "credit": cr,
            "balance": running
        })
    return jsonify({
        "account": account,
        "from": dfrom.isoformat(),
        "to": (dto - timedelta(microseconds=1)).isoformat(),
        "opening_balance": opening,
        "closing_balance": running,
        "lines": lines
    })

@ledger_bp.get("/entity")
@login_required
def entity_ledger():
    dfrom, dto = _parse_dates()
    et = (request.args.get("entity_type") or "").upper().strip()
    eid = request.args.get("entity_id", type=int)
    if not (et and eid):
        return jsonify({"error": "entity_type & entity_id مطلوبان"}), 400
    
    # 🧠 الحصول على اسم الجهة
    entity_name = "—"
    if et == 'CUSTOMER':
        customer = db.session.get(Customer, eid)
        entity_name = customer.name if customer else f"عميل #{eid}"
    elif et == 'SUPPLIER':
        supplier = db.session.get(Supplier, eid)
        if supplier:
            db.session.refresh(supplier)
        entity_name = supplier.name if supplier else f"مورد #{eid}"
    elif et == 'PARTNER':
        partner = db.session.get(Partner, eid)
        entity_name = partner.name if partner else f"شريك #{eid}"
    elif et == 'EMPLOYEE':
        employee = db.session.get(Employee, eid)
        entity_name = employee.name if employee else f"موظف #{eid}"
    base = (db.session.query(
                GLBatch.posted_at.label("posted_at"),
                GLBatch.source_type.label("source_type"),
                GLBatch.source_id.label("source_id"),
                GLBatch.purpose.label("purpose"),
                GLBatch.memo.label("memo"),
                GLEntry.account.label("account"),
                GLEntry.debit.label("debit"),
                GLEntry.credit.label("credit"),
                GLEntry.ref.label("ref"),
                GLEntry.id.label("entry_id")
            )
            .join(GLBatch, GLBatch.id == GLEntry.batch_id)
            .filter(GLBatch.entity_type == et, GLBatch.entity_id == eid,
                    GLBatch.posted_at >= dfrom, GLBatch.posted_at < dto)
            .order_by(GLBatch.posted_at.asc(), GLEntry.id.asc()))
    total_dr_q = (db.session.query(func.coalesce(func.sum(GLEntry.debit), 0.0))
                  .join(GLBatch, GLBatch.id == GLEntry.batch_id)
                  .filter(GLBatch.entity_type == et, GLBatch.entity_id == eid,
                          GLBatch.posted_at >= dfrom, GLBatch.posted_at < dto))
    total_cr_q = (db.session.query(func.coalesce(func.sum(GLEntry.credit), 0.0))
                  .join(GLBatch, GLBatch.id == GLEntry.batch_id)
                  .filter(GLBatch.entity_type == et, GLBatch.entity_id == eid,
                          GLBatch.posted_at >= dfrom, GLBatch.posted_at < dto))
    page, per_page = _get_pagination()
    if page:
        total = base.count()
        rows = base.limit(per_page).offset((page - 1) * per_page).all()
        items = []
        for r in rows:
            dr = float(r.debit or 0.0)
            cr = float(r.credit or 0.0)
            items.append({
                "date": r.posted_at.isoformat(),
                "source": f"{r.source_type}:{r.source_id}",
                "purpose": r.purpose,
                "memo": r.memo,
                "account": r.account,
                "debit": dr,
                "credit": cr,
                "ref": r.ref
            })
        return jsonify({
            "entity_type": et,
            "entity_id": eid,
            "entity_name": entity_name,  # ✅ إضافة اسم الجهة
            "from": dfrom.isoformat(),
            "to": (dto - timedelta(microseconds=1)).isoformat(),
            "total_debit": float(total_dr_q.scalar() or 0.0),
            "total_credit": float(total_cr_q.scalar() or 0.0),
            "page": page,
            "per_page": per_page,
            "total": total,
            "lines": items
        })
    rows = base.all()
    total_dr = float(total_dr_q.scalar() or 0.0)
    total_cr = float(total_cr_q.scalar() or 0.0)
    items = []
    for r in rows:
        dr = float(r.debit or 0.0)
        cr = float(r.credit or 0.0)
        items.append({
            "date": r.posted_at.isoformat(),
            "source": f"{r.source_type}:{r.source_id}",
            "purpose": r.purpose,
            "memo": r.memo,
            "account": r.account,
            "debit": dr,
            "credit": cr,
            "ref": r.ref
        })
    return jsonify({
        "entity_type": et,
        "entity_id": eid,
        "entity_name": entity_name,  # ✅ إضافة اسم الجهة
        "from": dfrom.isoformat(),
        "to": (dto - timedelta(microseconds=1)).isoformat(),
        "total_debit": total_dr,
        "total_credit": total_cr,
        "lines": items
    })


@ledger_bp.route("/batch/<int:batch_id>", methods=["GET"], endpoint="get_batch_details")
@login_required
def get_batch_details(batch_id):
    """جلب تفاصيل قيد محاسبي (GLBatch + Entries)"""
    try:
        # جلب القيد
        batch = GLBatch.query.get(batch_id)
        if not batch:
            return jsonify({"success": False, "error": "القيد غير موجود"}), 404
        
        # 🧠 استخراج الجهة المرتبطة بذكاء
        entity_name, entity_type_ar, entity_id_extracted, entity_type_code = extract_entity_from_batch(batch)
        
        # جلب القيود الفرعية
        entries = GLEntry.query.filter_by(batch_id=batch_id).all()
        
        entries_list = []
        for entry in entries:
            account = Account.query.filter_by(code=entry.account).first()
            entries_list.append({
                "account_code": entry.account,
                "account_name": account.name if account else entry.account,
                "debit": float(entry.debit or 0),
                "credit": float(entry.credit or 0),
                "ref": entry.ref
            })
        
        return jsonify({
            "success": True,
            "batch": {
                "id": batch.id,
                "code": batch.code,
                "source_type": batch.source_type,
                "source_id": batch.source_id,
                "purpose": batch.purpose,
                "memo": batch.memo,
                "posted_at": batch.posted_at.isoformat() if batch.posted_at else None,
                "currency": batch.currency,
                "status": batch.status,
                "entity_name": entity_name,  # ✅ إضافة اسم الجهة
                "entity_type": entity_type_ar,  # ✅ إضافة نوع الجهة بالعربي
                "entity_id": entity_id_extracted,  # ✅ إضافة معرف الجهة
                "entity_type_code": entity_type_code  # ✅ إضافة كود نوع الجهة
            },
            "entries": entries_list,
            "total_debit": sum(e["debit"] for e in entries_list),
            "total_credit": sum(e["credit"] for e in entries_list)
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
