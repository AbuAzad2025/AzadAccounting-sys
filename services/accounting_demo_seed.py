from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP

from extensions import db
from utils.customer_balance_updater import update_customer_balance_components
from utils.partner_balance_updater import update_partner_balance_components
from utils.supplier_balance_updater import update_supplier_balance_components


def _d(x) -> Decimal:
    try:
        return Decimal(str(x or 0))
    except Exception:
        return Decimal("0")


def _q2(x) -> Decimal:
    return _d(x).quantize(Decimal("0.01"), ROUND_HALF_UP)


def _create_demo_gl_coverage_batches(
    *,
    seed_tag: str,
    customer_id: int,
    supplier_id: int,
    partner_id: int,
    employee_id: int,
) -> list[str]:
    from models import _gl_upsert_batch_and_entries

    conn = db.session.connection()
    base = 900000 + int(customer_id or 0) * 1000
    types: list[tuple[str, str, str | None, int | None, list[tuple[str, float, float]]]] = [
        ("CUSTOMER", "OPENING_BALANCE", "CUSTOMER", customer_id, [("1100_AR", 100.0, 0.0), ("3000_EQUITY", 0.0, 100.0)]),
        ("SUPPLIER", "OPENING_BALANCE", "SUPPLIER", supplier_id, [("5100_PURCHASES", 80.0, 0.0), ("2000_AP", 0.0, 80.0)]),
        ("PARTNER", "OPENING_BALANCE", "PARTNER", partner_id, [("1300_INVENTORY", 60.0, 0.0), ("3200_PARTNER_EQUITY", 0.0, 60.0)]),
        ("SALE_LINE", "SALE", "CUSTOMER", customer_id, [("1100_AR", 25.0, 0.0), ("4000_SALES", 0.0, 25.0)]),
        ("SERVICE_PART", "SERVICE", "CUSTOMER", customer_id, [("1100_AR", 20.0, 0.0), ("4100_SERVICE_REVENUE", 0.0, 20.0)]),
        ("EXCHANGE", "EXCHANGE", None, None, [("1300_INVENTORY", 30.0, 0.0), ("1000_CASH", 0.0, 30.0)]),
        ("EXCHANGE_PURCHASE", "EXCHANGE", "SUPPLIER", supplier_id, [("5100_PURCHASES", 30.0, 0.0), ("2000_AP", 0.0, 30.0)]),
        ("EXCHANGE_RETURN", "EXCHANGE", "SUPPLIER", supplier_id, [("2000_AP", 12.0, 0.0), ("5100_PURCHASES", 0.0, 12.0)]),
        ("EXCHANGE_ADJUST", "EXCHANGE", None, None, [("5800_INV_ADJ", 8.0, 0.0), ("1300_INVENTORY", 0.0, 8.0)]),
        ("CONSUME_SALE", "COGS", None, None, [("5000_COGS", 10.0, 0.0), ("1300_INVENTORY", 0.0, 10.0)]),
        ("CONSUME_SERVICE", "COGS", None, None, [("5000_COGS", 9.0, 0.0), ("1300_INVENTORY", 0.0, 9.0)]),
        ("LOAN_SETTLEMENT", "SETTLEMENT", None, None, [("2100_LOANS", 40.0, 0.0), ("1000_CASH", 0.0, 40.0)]),
        ("SUPPLIER_INVOICE", "INVOICE", "SUPPLIER", supplier_id, [("5100_PURCHASES", 55.0, 0.0), ("2000_AP", 0.0, 55.0)]),
        ("SHIPMENT", "SHIPMENT", None, None, [("1300_INVENTORY", 70.0, 0.0), ("2000_AP", 0.0, 70.0)]),
        ("SHIPMENT_REVERSAL", "REVERSAL", None, None, [("2000_AP", 22.0, 0.0), ("1300_INVENTORY", 0.0, 22.0)]),
        ("PAYMENT", "PAYMENT", "CUSTOMER", customer_id, [("1000_CASH", 15.0, 0.0), ("1100_AR", 0.0, 15.0)]),
        ("PAYMENT_REVERSAL", "REVERSAL", "CUSTOMER", customer_id, [("1100_AR", 15.0, 0.0), ("1000_CASH", 0.0, 15.0)]),
        ("PAYMENT_CANCELLATION", "CANCELLATION", "CUSTOMER", customer_id, [("1100_AR", 5.0, 0.0), ("1000_CASH", 0.0, 5.0)]),
        ("PAYMENT_SPLIT", "PAYMENT", "CUSTOMER", customer_id, [("1000_CASH", 11.0, 0.0), ("1100_AR", 0.0, 11.0)]),
        ("INVOICE_REVERSAL", "REVERSAL", "CUSTOMER", customer_id, [("4000_SALES", 14.0, 0.0), ("1100_AR", 0.0, 14.0)]),
        ("SALE_REVERSAL", "REVERSAL", "CUSTOMER", customer_id, [("4000_SALES", 16.0, 0.0), ("1100_AR", 0.0, 16.0)]),
        ("SALE_RETURN", "RETURN", "CUSTOMER", customer_id, [("4000_SALES", 18.0, 0.0), ("1100_AR", 0.0, 18.0)]),
        ("SERVICE_REVERSAL", "REVERSAL", "CUSTOMER", customer_id, [("4100_SERVICE_REVENUE", 13.0, 0.0), ("1100_AR", 0.0, 13.0)]),
        ("PREORDER", "PREORDER", "CUSTOMER", customer_id, [("1100_AR", 21.0, 0.0), ("4000_SALES", 0.0, 21.0)]),
        ("PREORDER_REVERSAL", "REVERSAL", "CUSTOMER", customer_id, [("4000_SALES", 21.0, 0.0), ("1100_AR", 0.0, 21.0)]),
        ("ONLINE_ORDER", "ONLINE_SALE", "CUSTOMER", customer_id, [("1301", 19.0, 0.0), ("4100", 0.0, 19.0)]),
        ("ONLINE_ORDER_REVERSAL", "REVERSAL", "CUSTOMER", customer_id, [("4100", 19.0, 0.0), ("1301", 0.0, 19.0)]),
        ("ONLINE_PREORDER", "ONLINE_SALE", "CUSTOMER", customer_id, [("1301", 17.0, 0.0), ("4100", 0.0, 17.0)]),
        ("EXPENSE", "ACCRUAL", None, None, [("6200_RENT", 23.0, 0.0), ("1000_CASH", 0.0, 23.0)]),
        ("EXPENSE_REVERSAL", "REVERSAL", None, None, [("1000_CASH", 23.0, 0.0), ("6200_RENT", 0.0, 23.0)]),
        ("PROJECT_COST", "PROJECT", None, None, [("6900_PROJECT_COST", 12.0, 0.0), ("1000_CASH", 0.0, 12.0)]),
        ("PROJECT_REVENUE", "PROJECT", None, None, [("1100_AR", 27.0, 0.0), ("7900_PROJECT_REVENUE", 0.0, 27.0)]),
        ("PARTNER_SETTLEMENT", "SETTLEMENT", "PARTNER", partner_id, [("2000_AP", 9.0, 0.0), ("1000_CASH", 0.0, 9.0)]),
        ("SUPPLIER_SETTLEMENT", "SETTLEMENT", "SUPPLIER", supplier_id, [("2000_AP", 8.0, 0.0), ("1000_CASH", 0.0, 8.0)]),
        ("CHECK", "PAYMENT", "CUSTOMER", customer_id, [("1030_CHECKS", 10.0, 0.0), ("1100_AR", 0.0, 10.0)]),
        ("CHECK_REVERSAL", "REVERSAL", "CUSTOMER", customer_id, [("1100_AR", 10.0, 0.0), ("1030_CHECKS", 0.0, 10.0)]),
        ("MANUAL", "JOURNAL", None, None, [("1000_CASH", 33.0, 0.0), ("4000_SALES", 0.0, 33.0)]),
        ("DEPRECIATION", "DEPRECIATION", None, None, [("6800_DEPRECIATION", 7.0, 0.0), ("1599_ACC_DEP", 0.0, 7.0)]),
        ("CLOSING_ENTRY", "CLOSING", None, None, [("4000_SALES", 6.0, 0.0), ("3900_INCOME_SUMMARY", 0.0, 6.0)]),
        ("REVERSAL", "REVERSAL", None, None, [("3900_INCOME_SUMMARY", 6.0, 0.0), ("4000_SALES", 0.0, 6.0)]),
        ("ALLOCATION", "ALLOCATION", None, None, [("6100_SALARIES", 4.0, 0.0), ("6200_RENT", 0.0, 4.0)]),
        ("BANK_ACCOUNT", "TRANSFER", None, None, [("1010_BANK", 5.0, 0.0), ("1000_CASH", 0.0, 5.0)]),
    ]

    produced: list[str] = []
    for i, (st, purpose, etype, eid, entries) in enumerate(types, start=1):
        sid = base + i
        _gl_upsert_batch_and_entries(
            conn,
            source_type=st,
            source_id=sid,
            purpose=purpose,
            currency="ILS",
            memo=f"DemoSeed:{seed_tag}:GLCOVER:{st}",
            entries=entries,
            ref=f"{seed_tag}-{st}-{sid}",
            entity_type=etype,
            entity_id=eid,
        )
        produced.append(st)

    _gl_upsert_batch_and_entries(
        conn,
        source_type="EMPLOYEE",
        source_id=base + 999,
        purpose="OPENING_BALANCE",
        currency="ILS",
        memo=f"DemoSeed:{seed_tag}:GLCOVER:EMPLOYEE",
        entries=[("6110_EMPLOYEE_ADVANCES", 13.0, 0.0), ("1000_CASH", 0.0, 13.0)],
        ref=f"{seed_tag}-EMP-{base + 999}",
        entity_type="EMPLOYEE",
        entity_id=int(employee_id),
    )
    produced.append("EMPLOYEE")

    return produced


def seed_accounting_demo(
    *,
    tag: str | None = None,
    days_ago: int = 0,
    with_settlements: bool = True,
    update_balances: bool = True,
    cover_all_gl_types: bool = False,
    full_system: bool = False,
    scale: int = 1,
) -> dict:
    from models import (
        Account,
        Archive,
        BankAccount,
        BankReconciliation,
        BankStatement,
        BankTransaction,
        Branch,
        Check,
        CheckStatus,
        CostCenter,
        CostCenterAlert,
        CostCenterAllocation,
        Currency,
        Customer,
        Budget,
        BudgetCommitment,
        ExchangeRate,
        ExchangeTransaction,
        Employee,
        EmployeeAdvanceInstallment,
        EmployeeDeduction,
        Expense,
        ExpenseType,
        FixedAsset,
        FixedAssetCategory,
        AssetDepreciation,
        AssetMaintenance,
        GLBatch,
        GLEntry,
        Invoice,
        InvoiceLine,
        Note,
        Partner,
        PartnerSettlementStatus,
        Permission,
        Payment,
        PaymentDirection,
        PaymentEntityType,
        PaymentMethod,
        PaymentSplit,
        PaymentStatus,
        PreOrder,
        Product,
        Project,
        ProjectCost,
        ProjectMilestone,
        ProjectChangeOrder,
        ProjectRisk,
        ProjectPhase,
        ProjectRevenue,
        Role,
        Sale,
        SaleLine,
        SaleReturn,
        SaleReturnLine,
        Shipment,
        ShipmentItem,
        ShipmentPartner,
        SaaSPlan,
        SaaSSubscription,
        SaaSInvoice,
        ServicePart,
        ServiceRequest,
        ServiceStatus,
        ServiceTask,
        StockAdjustment,
        StockAdjustmentItem,
        StockLevel,
        Supplier,
        SupplierSettlementStatus,
        SystemSettings,
        Site,
        Transfer,
        TransferDirection,
        User,
        Warehouse,
        WarehousePartnerShare,
        WarehouseType,
        WorkflowDefinition,
        WorkflowInstance,
        WorkflowAction,
        build_partner_settlement_draft,
        build_supplier_settlement_draft,
        _get_rate_cached,
    )
    from permissions_config.permissions import PermissionsRegistry

    now = datetime.now(timezone.utc) - timedelta(days=int(days_ago or 0))
    seed_tag = (tag or "").strip() or uuid.uuid4().hex[:8].upper()
    phone_suffix = f"{int(uuid.uuid4().hex[:7], 16) % 10**7:07d}"
    payment_prefix = f"PMT-{seed_tag}-{uuid.uuid4().hex[:6].upper()}"
    scale_i = max(1, int(scale or 1))

    def _ensure_account(code: str, name: str = ""):
        c = (code or "").strip().upper()
        if not c:
            return
        if db.session.query(Account.id).filter(Account.code == c).scalar() is not None:
            return
        try:
            prefix = str(c).split("_", 1)[0]
            leading = int(prefix[:1]) if prefix and prefix[:1].isdigit() else None
        except Exception:
            leading = None
        acc_type = "ASSET"
        if leading == 2:
            acc_type = "LIABILITY"
        elif leading == 3:
            acc_type = "EQUITY"
        elif leading == 4:
            acc_type = "REVENUE"
        elif leading in (5, 6, 7, 8, 9):
            acc_type = "EXPENSE"
        db.session.add(Account(code=c, name=(name or c), type=acc_type, is_active=True))
        db.session.flush()

    def _seed_permissions_and_owner_user() -> dict:
        all_perms = PermissionsRegistry.get_all_permissions() or {}
        for code, info in all_perms.items():
            c = (code or "").strip().lower()
            if not c:
                continue
            row = db.session.query(Permission).filter(Permission.code == c).one_or_none()
            if row:
                if not row.name_ar and info.get("name_ar"):
                    row.name_ar = info.get("name_ar")
                if not row.module and info.get("module"):
                    row.module = info.get("module")
                if row.is_protected is None:
                    row.is_protected = bool(info.get("is_protected", False))
                continue
            db.session.add(
                Permission(
                    name=(info.get("name_ar") or info.get("code_ar") or c),
                    code=c,
                    description=info.get("description") or "",
                    name_ar=info.get("name_ar") or "",
                    module=(info.get("module") or "other"),
                    is_protected=bool(info.get("is_protected", False)),
                    aliases=[],
                )
            )
        db.session.flush()

        owner_role = db.session.query(Role).filter(Role.name == "owner").one_or_none()
        if not owner_role:
            owner_role = Role(name="owner", description="Owner", is_default=False)
            db.session.add(owner_role)
            db.session.flush()

        exclude = set((PermissionsRegistry.ROLES.get("owner") or {}).get("exclude", []) or [])
        desired = []
        for p in db.session.query(Permission).all():
            c = (p.code or "").strip().lower()
            if c and c not in exclude:
                desired.append(p)
        owner_role.permissions = desired
        db.session.flush()

        pwd = "Aa123456!"
        owner_user = User.query.filter(User.username == f"owner_{seed_tag.lower()}").one_or_none()
        if not owner_user:
            owner_user = User(username=f"owner_{seed_tag.lower()}", email=f"owner_{seed_tag.lower()}@local", is_active=True, is_system_account=True, role_id=owner_role.id)
            owner_user.set_password(pwd)
            db.session.add(owner_user)
            db.session.flush()
        else:
            owner_user.role_id = owner_role.id
            owner_user.is_active = True
        return {"owner_user_id": int(owner_user.id), "owner_username": owner_user.username, "owner_password": pwd}

    def _attach_one_split(p: Payment):
        p.splits.append(PaymentSplit(method=p.method, amount=p.total_amount, currency=p.currency, converted_currency=p.currency, details={}))

    def _attach_splits(p: Payment, splits: list[tuple[str, Decimal, dict]]):
        p.splits[:] = []
        for method, amount, details in splits:
            p.splits.append(PaymentSplit(method=method, amount=_q2(amount), currency=p.currency, converted_currency=p.currency, details=(details or {})))

    for code, name in (("ILS", "شيكل"), ("USD", "دولار"), ("JOD", "دينار"), ("EUR", "يورو")):
        cur = db.session.get(Currency, code)
        if not cur:
            db.session.add(Currency(code=code, name=name, symbol=code, is_active=True, decimals=2))
        else:
            cur.is_active = True

    fx_time = now - timedelta(days=2)
    fx_rows = [
        ("USD", "ILS", Decimal("3.70")),
        ("JOD", "ILS", Decimal("5.20")),
        ("EUR", "ILS", Decimal("4.05")),
        ("ILS", "USD", Decimal("0.27027027")),
        ("ILS", "JOD", Decimal("0.19230769")),
        ("ILS", "EUR", Decimal("0.24691358")),
    ]
    for base, quote, rate in fx_rows:
        ex = ExchangeRate.query.filter(
            ExchangeRate.base_code == base,
            ExchangeRate.quote_code == quote,
            ExchangeRate.valid_from == fx_time,
        ).first()
        if not ex:
            db.session.add(ExchangeRate(base_code=base, quote_code=quote, rate=rate, valid_from=fx_time, source="demo", is_active=True))

    try:
        _get_rate_cached.cache_clear()
    except Exception:
        pass

    branch = Branch.query.order_by(Branch.id.asc()).first()
    if not branch:
        branch = Branch(code=f"DEMO-{seed_tag}", name=f"فرع ديمو {seed_tag}", is_active=True, currency="ILS", timezone="Asia/Jerusalem")
        db.session.add(branch)
        db.session.flush()

    et_other = ExpenseType.query.filter(ExpenseType.code == "OTHER").first()
    if not et_other:
        et_other = ExpenseType(name="أخرى", description="أخرى", is_active=True, code="OTHER")
        db.session.add(et_other)
        db.session.flush()

    def _ensure_expense_type(code: str, name: str, fields_meta: dict | None = None) -> ExpenseType:
        c = (code or "").strip().upper()
        row = ExpenseType.query.filter(ExpenseType.code == c).first()
        if row:
            if fields_meta and not (row.fields_meta or None):
                row.fields_meta = fields_meta
            return row
        row = ExpenseType(name=name, description=name, is_active=True, code=c, fields_meta=fields_meta or None)
        db.session.add(row)
        db.session.flush()
        return row

    et_ship_freight = _ensure_expense_type("SHIP_FREIGHT", "شحن")
    et_ship_customs = _ensure_expense_type("SHIP_CUSTOMS", "جمارك")
    et_damaged = _ensure_expense_type("DAMAGED", "تالف")
    et_salary = _ensure_expense_type(
        "SALARY",
        "رواتب",
        {
            "required": ["employee_id", "period"],
            "optional": ["description"],
            "gl_account_code": "6100_SALARIES",
            "ledger": {"expense_account": "6100_SALARIES", "counterparty_account": "2150_PAY_CLR", "cash_account": "1000_CASH"},
            "payment_behavior": "ON_ACCOUNT",
        },
    )
    et_emp_advance = _ensure_expense_type(
        "EMPLOYEE_ADVANCE",
        "سلفة موظف",
        {
            "required": ["employee_id"],
            "optional": ["period", "description"],
            "gl_account_code": "6110_EMPLOYEE_ADVANCES",
            "ledger": {"expense_account": "6110_EMPLOYEE_ADVANCES", "counterparty_account": "2150_EMP_ADV", "cash_account": "1000_CASH"},
            "payment_behavior": "ON_ACCOUNT",
        },
    )
    et_utilities = _ensure_expense_type("UTILITIES", "مرافق")
    et_rent = _ensure_expense_type("RENT", "إيجار")
    et_marketing = _ensure_expense_type("MARKETING", "تسويق")

    user = User.query.filter(User.username == f"demo_seed_{seed_tag.lower()}").one_or_none()
    if not user:
        user = User(username=f"demo_seed_{seed_tag.lower()}", email=f"demo_seed_{seed_tag.lower()}@local", is_active=True, is_system_account=True)
        user.set_password(uuid.uuid4().hex + "Aa1!")
        db.session.add(user)
        db.session.flush()

    customer = Customer(name=f"عميل ديمو {seed_tag}", phone=f"059{phone_suffix}", is_active=True, currency="ILS")
    supplier = Supplier(name=f"مورد ديمو {seed_tag}", phone=f"056{phone_suffix}", is_archived=False, currency="USD", customer_id=None)
    partner = Partner(name=f"شريك ديمو {seed_tag}", phone_number=f"057{phone_suffix}", is_archived=False, currency="ILS", customer_id=None)
    db.session.add_all([customer, supplier, partner])
    db.session.flush()

    supplier.customer_id = customer.id
    partner.customer_id = customer.id

    wh_main = Warehouse(name=f"مستودع رئيسي {seed_tag}", warehouse_type=WarehouseType.MAIN.value, is_active=True)
    wh_exchange = Warehouse(name=f"مستودع تبادل {seed_tag}", warehouse_type=WarehouseType.EXCHANGE.value, supplier_id=supplier.id, is_active=True)
    wh_partner = Warehouse(name=f"مستودع شريك {seed_tag}", warehouse_type=WarehouseType.PARTNER.value, partner_id=partner.id, share_percent=20.0, is_active=True)
    wh_online = Warehouse(name=f"مستودع أونلاين {seed_tag}", warehouse_type=WarehouseType.ONLINE.value, is_active=True, online_slug=f"online-{seed_tag.lower()}", online_is_default=True)
    wh_inventory = Warehouse(name=f"مستودع ملكيتي {seed_tag}", warehouse_type=WarehouseType.INVENTORY.value, is_active=True)
    db.session.add_all([wh_main, wh_exchange, wh_partner, wh_online, wh_inventory])
    db.session.flush()

    prod_ils = Product(
        name=f"قطعة ILS {seed_tag}",
        barcode=f"ILS{seed_tag}01",
        currency="ILS",
        price=_q2("120"),
        selling_price=_q2("120"),
        purchase_price=_q2("80"),
        tax_rate=_q2("0"),
        supplier_id=supplier.id,
    )
    prod_usd = Product(
        name=f"قطعة USD {seed_tag}",
        barcode=f"USD{seed_tag}01",
        currency="USD",
        price=_q2("50"),
        selling_price=_q2("50"),
        purchase_price=_q2("35"),
        tax_rate=_q2("0"),
        supplier_id=supplier.id,
    )
    db.session.add_all([prod_ils, prod_usd])
    db.session.flush()

    db.session.add(WarehousePartnerShare(partner_id=partner.id, warehouse_id=wh_main.id, product_id=prod_ils.id, share_percentage=20.0))

    tx_in = ExchangeTransaction(product_id=prod_ils.id, warehouse_id=wh_exchange.id, supplier_id=supplier.id, quantity=20, direction="IN", unit_cost=_q2("80"), created_at=now - timedelta(days=1))
    db.session.add(tx_in)
    db.session.flush()

    transfer = Transfer(product_id=prod_ils.id, source_id=wh_exchange.id, destination_id=wh_main.id, quantity=10, direction=TransferDirection.OUT.value, transfer_date=now - timedelta(days=1), user_id=user.id)
    db.session.add(transfer)

    tx_out = ExchangeTransaction(product_id=prod_ils.id, warehouse_id=wh_exchange.id, supplier_id=supplier.id, quantity=3, direction="OUT", unit_cost=_q2("80"), created_at=now - timedelta(hours=20))
    db.session.add(tx_out)

    transfer_to_online = Transfer(product_id=prod_ils.id, source_id=wh_main.id, destination_id=wh_online.id, quantity=2, direction=TransferDirection.OUT.value, transfer_date=now - timedelta(hours=18), user_id=user.id)
    transfer_online_to_inventory = Transfer(product_id=prod_ils.id, source_id=wh_online.id, destination_id=wh_inventory.id, quantity=1, direction=TransferDirection.OUT.value, transfer_date=now - timedelta(hours=17), user_id=user.id)
    db.session.add_all([transfer_to_online, transfer_online_to_inventory])

    lvl_main = db.session.query(StockLevel).filter_by(product_id=prod_ils.id, warehouse_id=wh_main.id).with_for_update(read=False).first()
    if not lvl_main:
        lvl_main = StockLevel(product_id=prod_ils.id, warehouse_id=wh_main.id, quantity=0, reserved_quantity=0)
        db.session.add(lvl_main)
        db.session.flush()
    lvl_main.reserved_quantity = int(lvl_main.reserved_quantity or 0) + 2
    lvl_main.reserved_quantity = max(0, int(lvl_main.reserved_quantity or 0) - 2)

    ship_ref = f"AZD-DEMO-{seed_tag}-{uuid.uuid4().hex[:6].upper()}"
    shipment = Shipment(
        number=ship_ref,
        shipment_number=ship_ref,
        destination_id=wh_main.id,
        currency="USD",
        shipment_date=now - timedelta(hours=16),
        expected_arrival=now - timedelta(hours=2),
        origin="DEMO-ORIGIN",
        destination="DEMO-DEST",
        carrier="DEMO-CARRIER",
        tracking_number=f"TRK-{seed_tag}-{uuid.uuid4().hex[:6].upper()}",
        shipping_cost=_q2("120"),
        customs=_q2("80"),
        vat=_q2("0"),
        insurance=_q2("20"),
        notes=f"DemoSeed:{seed_tag}:SHIP",
        status="DRAFT",
    )
    shipment.items.append(ShipmentItem(product_id=prod_usd.id, warehouse_id=wh_main.id, quantity=3, unit_cost=_q2("35"), declared_value=_q2("105"), notes="بنود شحنة USD"))
    shipment.items.append(ShipmentItem(product_id=prod_ils.id, warehouse_id=wh_partner.id, quantity=1, unit_cost=_q2("80"), declared_value=_q2("80"), notes="بنود شريك"))
    shipment.partners.append(ShipmentPartner(partner_id=partner.id, share_percentage=_q2("20"), share_amount=_q2("0"), notes="شريك في شحنة"))
    db.session.add(shipment)
    db.session.flush()

    shipment.status = "IN_TRANSIT"
    shipment.status = "IN_CUSTOMS"
    shipment.status = "ARRIVED"

    ship_ref_delivered = f"AZD-DEMO-{seed_tag}-D-{uuid.uuid4().hex[:6].upper()}"
    shipment_delivered = Shipment(
        number=ship_ref_delivered,
        shipment_number=ship_ref_delivered,
        destination_id=wh_main.id,
        currency="USD",
        shipment_date=now - timedelta(hours=15),
        actual_arrival=now - timedelta(hours=3),
        delivered_date=now - timedelta(hours=1),
        origin="DEMO-ORIGIN",
        destination="DEMO-DEST",
        carrier="DEMO-CARRIER",
        tracking_number=f"TRK-{seed_tag}-D-{uuid.uuid4().hex[:6].upper()}",
        shipping_cost=_q2("0"),
        customs=_q2("0"),
        vat=_q2("0"),
        insurance=_q2("0"),
        notes=f"DemoSeed:{seed_tag}:SHIP_DELIVERED",
        status="DELIVERED",
    )
    ship_ref_cancelled = f"AZD-DEMO-{seed_tag}-C-{uuid.uuid4().hex[:6].upper()}"
    shipment_cancelled = Shipment(
        number=ship_ref_cancelled,
        shipment_number=ship_ref_cancelled,
        destination_id=wh_main.id,
        currency="USD",
        shipment_date=now - timedelta(hours=14),
        origin="DEMO-ORIGIN",
        destination="DEMO-DEST",
        carrier="DEMO-CARRIER",
        tracking_number=f"TRK-{seed_tag}-C-{uuid.uuid4().hex[:6].upper()}",
        shipping_cost=_q2("0"),
        customs=_q2("0"),
        vat=_q2("0"),
        insurance=_q2("0"),
        notes=f"DemoSeed:{seed_tag}:SHIP_CANCELLED",
        status="CANCELLED",
    )
    shipment_cancelled.items.append(ShipmentItem(product_id=prod_usd.id, warehouse_id=wh_main.id, quantity=1, unit_cost=_q2("35"), declared_value=_q2("35"), notes="شحنة ملغاة"))
    db.session.add_all([shipment_delivered, shipment_cancelled])
    db.session.flush()

    ship_exp_freight = Expense(
        date=now - timedelta(hours=10),
        amount=_q2("120"),
        currency="USD",
        type_id=int(et_ship_freight.id),
        branch_id=branch.id,
        warehouse_id=wh_main.id,
        shipment_id=shipment.id,
        payee_type="SHIPMENT",
        payee_entity_id=int(shipment.id),
        payee_name=str(shipment.shipment_number or shipment.number or shipment.id),
        payment_method="bank",
        description=f"شحن الشحنة {seed_tag}",
        notes=f"DemoSeed:{seed_tag}:SHIP_EXP_FREIGHT",
    )
    ship_exp_customs = Expense(
        date=now - timedelta(hours=8),
        amount=_q2("80"),
        currency="ILS",
        type_id=int(et_ship_customs.id),
        branch_id=branch.id,
        warehouse_id=wh_main.id,
        shipment_id=shipment.id,
        payee_type="SHIPMENT",
        payee_entity_id=int(shipment.id),
        payee_name=str(shipment.shipment_number or shipment.number or shipment.id),
        payment_method="cash",
        description=f"جمارك الشحنة {seed_tag}",
        notes=f"DemoSeed:{seed_tag}:SHIP_EXP_CUSTOMS",
    )
    db.session.add_all([ship_exp_freight, ship_exp_customs])

    pay_shipment = Payment(
        payment_number=f"{payment_prefix}-SHIP-OUT",
        payment_date=now - timedelta(hours=7),
        total_amount=_q2("50"),
        currency="USD",
        method=PaymentMethod.BANK.value,
        status=PaymentStatus.COMPLETED.value,
        direction=PaymentDirection.OUT.value,
        entity_type=PaymentEntityType.SHIPMENT.value,
        shipment_id=shipment.id,
        created_by=user.id,
        reference=f"DemoSeed:{seed_tag}:SHIP_PAY",
    )
    _attach_one_split(pay_shipment)
    db.session.add(pay_shipment)

    stock_adj = StockAdjustment(warehouse_id=wh_main.id, reason="DAMAGED", notes=f"DemoSeed:{seed_tag}:ADJ")
    db.session.add(stock_adj)
    db.session.flush()
    stock_adj_item = StockAdjustmentItem(adjustment_id=stock_adj.id, product_id=prod_ils.id, warehouse_id=wh_main.id, quantity=1, unit_cost=_q2("80"), notes="تالف ديمو")
    db.session.add(stock_adj_item)
    db.session.flush()
    adj_expense = Expense(
        date=now - timedelta(hours=6),
        amount=_q2(stock_adj.total_cost or 0),
        currency="ILS",
        type_id=int(et_damaged.id),
        branch_id=branch.id,
        warehouse_id=wh_main.id,
        stock_adjustment_id=stock_adj.id,
        payee_type="WAREHOUSE",
        payee_entity_id=int(wh_main.id),
        payee_name=wh_main.name,
        payment_method="cash",
        description=f"تالف مخزون {seed_tag}",
        notes=f"DemoSeed:{seed_tag}:ADJ_EXP",
    )
    db.session.add(adj_expense)

    notes: list[Note] = []
    notes.append(Note(content=f"ملاحظة عاجلة للعميل {seed_tag}", author_id=user.id, entity_type="CUSTOMER", entity_id=str(customer.id), is_pinned=True, priority="URGENT"))
    notes.append(Note(content=f"ملاحظة على الشحنة {seed_tag}", author_id=user.id, entity_type="SHIPMENT", entity_id=str(shipment.id), is_pinned=False, priority="HIGH", notification_type="REMINDER", notification_date=now + timedelta(days=1), target_type="ROLE", target_ids="admin,manager"))
    notes.append(Note(content=f"ملاحظة مستودع أونلاين {seed_tag}", author_id=user.id, entity_type="WAREHOUSE", entity_id=str(wh_online.id), is_pinned=False, priority="MEDIUM"))
    notes.append(Note(content=f"ملاحظة عامة {seed_tag}", author_id=user.id, entity_type="OTHER", entity_id=None, is_pinned=False, priority="LOW"))
    db.session.add_all(notes)

    def _period_range(dt: datetime):
        y = dt.year
        m = dt.month
        start = datetime(y, m, 1, tzinfo=dt.tzinfo).date()
        if m == 12:
            end = datetime(y, 12, 31, tzinfo=dt.tzinfo).date()
        else:
            end = (datetime(y, m + 1, 1, tzinfo=dt.tzinfo) - timedelta(days=1)).date()
        return start, end

    emp_ils = Employee(name=f"موظف ديمو 1 {seed_tag}", position="محاسب", salary=_q2("5000"), phone=f"058{phone_suffix}", email=f"emp1_{seed_tag.lower()}@local", hire_date=(now - timedelta(days=800)).date(), currency="ILS", branch_id=branch.id)
    emp_usd = Employee(name=f"موظف ديمو 2 {seed_tag}", position="مبيعات", salary=_q2("1600"), phone=f"058{int(phone_suffix) + 1:07d}", email=f"emp2_{seed_tag.lower()}@local", hire_date=(now - timedelta(days=400)).date(), currency="USD", branch_id=branch.id)
    db.session.add_all([emp_ils, emp_usd])
    db.session.flush()

    db.session.add(EmployeeDeduction(employee_id=emp_ils.id, deduction_type="PHONE", amount=_q2("100"), currency="ILS", start_date=(now - timedelta(days=60)).date(), end_date=None, is_active=True, notes=f"DemoSeed:{seed_tag}:DED1"))
    db.session.add(EmployeeDeduction(employee_id=emp_usd.id, deduction_type="INSURANCE", amount=_q2("50"), currency="USD", start_date=(now - timedelta(days=30)).date(), end_date=None, is_active=True, notes=f"DemoSeed:{seed_tag}:DED2"))

    adv_exp = Expense(
        date=now - timedelta(days=15),
        amount=_q2("600"),
        currency="ILS",
        type_id=int(et_emp_advance.id),
        branch_id=branch.id,
        employee_id=emp_ils.id,
        payee_type="EMPLOYEE",
        payee_entity_id=int(emp_ils.id),
        payee_name=emp_ils.name,
        payment_method="cash",
        description=f"سلفة موظف {seed_tag}",
        notes=f"DemoSeed:{seed_tag}:EMP_ADV",
        period_start=_period_range(now)[0],
        period_end=_period_range(now)[1],
    )
    db.session.add(adv_exp)
    db.session.flush()

    pay_adv = Payment(
        payment_number=f"{payment_prefix}-ADV-OUT",
        payment_date=now - timedelta(days=15),
        total_amount=_q2("600"),
        currency="ILS",
        method=PaymentMethod.CASH.value,
        status=PaymentStatus.COMPLETED.value,
        direction=PaymentDirection.OUT.value,
        entity_type=PaymentEntityType.EXPENSE.value,
        expense_id=adv_exp.id,
        created_by=user.id,
        reference=f"DemoSeed:{seed_tag}:ADV_PAY",
    )
    _attach_one_split(pay_adv)
    db.session.add(pay_adv)

    cur_period_start, cur_period_end = _period_range(now)
    inst1 = EmployeeAdvanceInstallment(employee_id=emp_ils.id, advance_expense_id=adv_exp.id, installment_number=1, total_installments=3, amount=_q2("200"), currency="ILS", due_date=cur_period_start, paid=False)
    inst2 = EmployeeAdvanceInstallment(employee_id=emp_ils.id, advance_expense_id=adv_exp.id, installment_number=2, total_installments=3, amount=_q2("200"), currency="ILS", due_date=cur_period_start + timedelta(days=15), paid=False)
    inst3 = EmployeeAdvanceInstallment(employee_id=emp_ils.id, advance_expense_id=adv_exp.id, installment_number=3, total_installments=3, amount=_q2("200"), currency="ILS", due_date=cur_period_end, paid=False)
    db.session.add_all([inst1, inst2, inst3])
    db.session.flush()

    def _salary_amount(emp: Employee, installments_total: Decimal) -> Decimal:
        base = _d(emp.salary or 0)
        deductions = _d(emp.total_deductions or 0)
        social_emp = _d(getattr(emp, "social_insurance_employee_amount", 0) or 0)
        income_tax = _d(getattr(emp, "income_tax_amount", 0) or 0)
        net = base - deductions - social_emp - income_tax - _d(installments_total or 0)
        if net < 0:
            net = Decimal("0")
        return _q2(net)

    salary_ils_amt = _salary_amount(emp_ils, _d("600"))
    salary_ils = Expense(
        date=now,
        amount=salary_ils_amt,
        currency="ILS",
        type_id=int(et_salary.id),
        branch_id=branch.id,
        employee_id=emp_ils.id,
        payee_type="EMPLOYEE",
        payee_entity_id=int(emp_ils.id),
        payee_name=emp_ils.name,
        payment_method="bank",
        description=f"راتب شهر {now.month}/{now.year} - {emp_ils.name}",
        notes=f"DemoSeed:{seed_tag}:SALARY_ILS",
        period_start=cur_period_start,
        period_end=cur_period_end,
    )
    salary_usd_amt = _salary_amount(emp_usd, _d("0"))
    salary_usd = Expense(
        date=now,
        amount=salary_usd_amt,
        currency="USD",
        type_id=int(et_salary.id),
        branch_id=branch.id,
        employee_id=emp_usd.id,
        payee_type="EMPLOYEE",
        payee_entity_id=int(emp_usd.id),
        payee_name=emp_usd.name,
        payment_method="bank",
        description=f"راتب شهر {now.month}/{now.year} - {emp_usd.name}",
        notes=f"DemoSeed:{seed_tag}:SALARY_USD",
        period_start=cur_period_start,
        period_end=cur_period_end,
    )
    db.session.add_all([salary_ils, salary_usd])
    db.session.flush()

    pay_sal_ils = Payment(
        payment_number=f"{payment_prefix}-SAL-OUT-ILS",
        payment_date=now,
        total_amount=_q2(_d(salary_ils_amt) - _d("150")),
        currency="ILS",
        method=PaymentMethod.BANK.value,
        status=PaymentStatus.COMPLETED.value,
        direction=PaymentDirection.OUT.value,
        entity_type=PaymentEntityType.EXPENSE.value,
        expense_id=salary_ils.id,
        created_by=user.id,
        reference=f"DemoSeed:{seed_tag}:SAL_PAY_PARTIAL",
    )
    _attach_one_split(pay_sal_ils)
    db.session.add(pay_sal_ils)

    pay_sal_usd = Payment(
        payment_number=f"{payment_prefix}-SAL-OUT-USD",
        payment_date=now,
        total_amount=salary_usd_amt,
        currency="USD",
        method=PaymentMethod.BANK.value,
        status=PaymentStatus.COMPLETED.value,
        direction=PaymentDirection.OUT.value,
        entity_type=PaymentEntityType.EXPENSE.value,
        expense_id=salary_usd.id,
        created_by=user.id,
        reference=f"DemoSeed:{seed_tag}:SAL_PAY_FULL",
    )
    _attach_one_split(pay_sal_usd)
    db.session.add(pay_sal_usd)

    for inst in (inst1, inst2, inst3):
        inst.paid = True
        inst.paid_date = now.date()
        inst.paid_in_salary_expense_id = salary_ils.id

    exp_util = Expense(date=now - timedelta(days=3), amount=_q2("220"), currency="ILS", type_id=int(et_utilities.id), branch_id=branch.id, payee_type="OTHER", payee_name="شركة كهرباء", payment_method="cash", description=f"كهرباء {seed_tag}", notes=f"DemoSeed:{seed_tag}:UTIL1")
    exp_rent = Expense(date=now - timedelta(days=2), amount=_q2("1200"), currency="ILS", type_id=int(et_rent.id), branch_id=branch.id, payee_type="OTHER", payee_name="مالك العقار", payment_method="bank", description=f"إيجار {seed_tag}", notes=f"DemoSeed:{seed_tag}:RENT1")
    exp_mkt = Expense(date=now - timedelta(days=1), amount=_q2("75"), currency="USD", type_id=int(et_marketing.id), branch_id=branch.id, payee_type="OTHER", payee_name="منصة إعلانات", payment_method="card", description=f"تسويق {seed_tag}", notes=f"DemoSeed:{seed_tag}:MKT1")
    db.session.add_all([exp_util, exp_rent, exp_mkt])
    db.session.flush()

    pay_rent = Payment(
        payment_number=f"{payment_prefix}-RENT-OUT",
        payment_date=now - timedelta(days=2),
        total_amount=_q2("1200"),
        currency="ILS",
        method=PaymentMethod.BANK.value,
        status=PaymentStatus.COMPLETED.value,
        direction=PaymentDirection.OUT.value,
        entity_type=PaymentEntityType.EXPENSE.value,
        expense_id=exp_rent.id,
        created_by=user.id,
        reference=f"DemoSeed:{seed_tag}:RENT_PAY",
    )
    _attach_one_split(pay_rent)
    db.session.add(pay_rent)

    pay_mkt = Payment(
        payment_number=f"{payment_prefix}-MKT-OUT",
        payment_date=now - timedelta(days=1),
        total_amount=_q2("75"),
        currency="USD",
        method=PaymentMethod.CARD.value,
        status=PaymentStatus.COMPLETED.value,
        direction=PaymentDirection.OUT.value,
        entity_type=PaymentEntityType.EXPENSE.value,
        expense_id=exp_mkt.id,
        created_by=user.id,
        reference=f"DemoSeed:{seed_tag}:MKT_PAY",
    )
    _attach_one_split(pay_mkt)
    db.session.add(pay_mkt)

    sale_ils = Sale(customer_id=customer.id, seller_id=user.id, sale_date=now, status="CONFIRMED", currency="ILS", tax_rate=_q2("0"), shipping_cost=_q2("0"), discount_total=_q2("0"))
    db.session.add(sale_ils)
    db.session.flush()
    db.session.add(SaleLine(sale_id=sale_ils.id, product_id=prod_ils.id, warehouse_id=wh_main.id, quantity=2, unit_price=_q2("120"), discount_rate=_q2("0"), tax_rate=_q2("0")))

    pay_sale_cash = Payment(
        payment_number=f"{payment_prefix}-SALE",
        payment_date=now,
        total_amount=_q2("150"),
        currency="ILS",
        method=PaymentMethod.CASH.value,
        status=PaymentStatus.COMPLETED.value,
        direction=PaymentDirection.IN.value,
        entity_type=PaymentEntityType.SALE.value,
        sale_id=sale_ils.id,
        created_by=user.id,
        reference=f"DemoSeed:{seed_tag}:SALE_CASH",
    )
    _attach_one_split(pay_sale_cash)
    db.session.add(pay_sale_cash)

    sale_return = SaleReturn(sale_id=sale_ils.id, customer_id=customer.id, warehouse_id=wh_main.id, status="CONFIRMED", currency="ILS", reason="مرتجع ديمو", notes=f"DemoSeed:{seed_tag}:RETURN")
    db.session.add(sale_return)
    db.session.flush()
    db.session.add(SaleReturnLine(sale_return_id=sale_return.id, product_id=prod_ils.id, warehouse_id=wh_main.id, quantity=1, unit_price=_q2("120"), condition="GOOD", liability_party="NONE"))

    sale_credit = Sale(customer_id=customer.id, seller_id=user.id, sale_date=now - timedelta(days=10), status="CONFIRMED", currency="ILS", tax_rate=_q2("0"), shipping_cost=_q2("10"), discount_total=_q2("5"))
    db.session.add(sale_credit)
    db.session.flush()
    db.session.add(SaleLine(sale_id=sale_credit.id, product_id=prod_ils.id, warehouse_id=wh_main.id, quantity=1, unit_price=_q2("130"), discount_rate=_q2("0"), tax_rate=_q2("0")))

    sale_card = Sale(customer_id=customer.id, seller_id=user.id, sale_date=now - timedelta(days=5), status="CONFIRMED", currency="ILS", tax_rate=_q2("0"), shipping_cost=_q2("0"), discount_total=_q2("0"))
    db.session.add(sale_card)
    db.session.flush()
    db.session.add(SaleLine(sale_id=sale_card.id, product_id=prod_ils.id, warehouse_id=wh_main.id, quantity=2, unit_price=_q2("125"), discount_rate=_q2("0"), tax_rate=_q2("0")))
    pay_sale_card = Payment(
        payment_number=f"{payment_prefix}-SALE-CARD",
        payment_date=now - timedelta(days=5),
        total_amount=_q2("250"),
        currency="ILS",
        method=PaymentMethod.CARD.value,
        status=PaymentStatus.COMPLETED.value,
        direction=PaymentDirection.IN.value,
        entity_type=PaymentEntityType.SALE.value,
        sale_id=sale_card.id,
        created_by=user.id,
        reference=f"DemoSeed:{seed_tag}:SALE_CARD",
    )
    _attach_one_split(pay_sale_card)
    db.session.add(pay_sale_card)

    inv_usd = Invoice(invoice_number=f"INV-{seed_tag}", invoice_date=now, customer_id=customer.id, source="MANUAL", kind="INVOICE", currency="USD")
    db.session.add(inv_usd)
    db.session.flush()
    db.session.add(InvoiceLine(invoice_id=inv_usd.id, product_id=prod_usd.id, description="بند USD", quantity=1, unit_price=_q2("50"), discount=0, tax_rate=0))

    pay_invoice_usd = Payment(
        payment_number=f"{payment_prefix}-INV",
        payment_date=now,
        total_amount=_q2("20"),
        currency="USD",
        method=PaymentMethod.BANK.value,
        status=PaymentStatus.COMPLETED.value,
        direction=PaymentDirection.IN.value,
        entity_type=PaymentEntityType.INVOICE.value,
        invoice_id=inv_usd.id,
        created_by=user.id,
        reference=f"DemoSeed:{seed_tag}:INV_BANK",
    )
    _attach_one_split(pay_invoice_usd)
    db.session.add(pay_invoice_usd)

    service = ServiceRequest(customer_id=customer.id, mechanic_id=user.id, status=ServiceStatus.COMPLETED.value, received_at=now, completed_at=now, currency="ILS", tax_rate=_q2("0"), discount_total=_q2("0"), notes=f"DemoSeed:{seed_tag}:SR")
    db.session.add(service)
    db.session.flush()
    db.session.add(ServicePart(service_id=service.id, part_id=prod_ils.id, warehouse_id=wh_main.id, quantity=1, unit_price=_q2("60"), discount=_q2("0"), tax_rate=_q2("0"), partner_id=partner.id, share_percentage=_q2("20")))
    db.session.add(ServiceTask(service_id=service.id, description="أجرة صيانة", quantity=1, unit_price=_q2("40"), discount=_q2("0"), tax_rate=_q2("0")))

    preorder = PreOrder(product_id=prod_ils.id, warehouse_id=wh_main.id, quantity=1, customer_id=customer.id, prepaid_amount=_q2("0"), tax_rate=_q2("0"), payment_method=PaymentMethod.CASH.value, notes=f"DemoSeed:{seed_tag}:PRE", preorder_date=now)
    db.session.add(preorder)

    bounced = Payment(
        payment_number=f"{payment_prefix}-BOUNCED",
        payment_date=now,
        total_amount=_q2("30"),
        currency="USD",
        method=PaymentMethod.CHEQUE.value,
        status=PaymentStatus.FAILED.value,
        direction=PaymentDirection.IN.value,
        entity_type=PaymentEntityType.CUSTOMER.value,
        customer_id=customer.id,
        created_by=user.id,
        reference=f"DemoSeed:{seed_tag}:BOUNCED_USD",
    )
    db.session.add(bounced)
    db.session.flush()

    db.session.add(
        Check(
            amount=_q2("30"),
            currency="USD",
            check_number=f"{seed_tag}BOUNCE",
            check_bank="Demo Bank",
            check_date=now,
            check_due_date=now + timedelta(days=7),
            status=CheckStatus.BOUNCED.value,
            direction=PaymentDirection.IN.value,
            customer_id=customer.id,
            payment_id=bounced.id,
            reference_number=f"DemoSeed:{seed_tag}:CHK_BOUNCED",
            notes="شيك مرتد ديمو",
            created_by_id=user.id,
        )
    )

    ex_customer = Expense(
        date=now,
        amount=_q2("25"),
        currency="ILS",
        type_id=int(et_other.id),
        branch_id=branch.id,
        customer_id=customer.id,
        payee_type="CUSTOMER",
        payee_entity_id=customer.id,
        payee_name=customer.name,
        payment_method="cash",
        description=f"مصروف على العميل {seed_tag}",
        notes=f"DemoSeed:{seed_tag}:EXP_CUST",
    )
    ex_supplier = Expense(
        date=now,
        amount=_q2("10"),
        currency="USD",
        type_id=int(et_other.id),
        branch_id=branch.id,
        supplier_id=supplier.id,
        payee_type="SUPPLIER",
        payee_entity_id=supplier.id,
        payee_name=supplier.name,
        payment_method="bank",
        description=f"مصروف على المورد {seed_tag}",
        notes=f"DemoSeed:{seed_tag}:EXP_SUP",
    )
    ex_partner = Expense(
        date=now,
        amount=_q2("15"),
        currency="ILS",
        type_id=int(et_other.id),
        branch_id=branch.id,
        partner_id=partner.id,
        payee_type="PARTNER",
        payee_entity_id=partner.id,
        payee_name=partner.name,
        payment_method="cash",
        description=f"مصروف على الشريك {seed_tag}",
        notes=f"DemoSeed:{seed_tag}:EXP_PAR",
    )
    db.session.add_all([ex_customer, ex_supplier, ex_partner])

    pay_out_supplier = Payment(
        payment_number=f"{payment_prefix}-SUP-OUT",
        payment_date=now,
        total_amount=_q2("50"),
        currency="USD",
        method=PaymentMethod.BANK.value,
        status=PaymentStatus.COMPLETED.value,
        direction=PaymentDirection.OUT.value,
        entity_type=PaymentEntityType.SUPPLIER.value,
        supplier_id=supplier.id,
        created_by=user.id,
        reference=f"DemoSeed:{seed_tag}:SUP_OUT",
    )
    pay_out_partner = Payment(
        payment_number=f"{payment_prefix}-PAR-OUT",
        payment_date=now,
        total_amount=_q2("30"),
        currency="ILS",
        method=PaymentMethod.CASH.value,
        status=PaymentStatus.COMPLETED.value,
        direction=PaymentDirection.OUT.value,
        entity_type=PaymentEntityType.PARTNER.value,
        partner_id=partner.id,
        created_by=user.id,
        reference=f"DemoSeed:{seed_tag}:PAR_OUT",
    )
    _attach_one_split(pay_out_supplier)
    _attach_one_split(pay_out_partner)
    db.session.add_all([pay_out_supplier, pay_out_partner])

    created = {
        "seed_tag": seed_tag,
        "branch_id": int(branch.id),
        "user_id": int(user.id),
        "customer_id": int(customer.id),
        "supplier_id": int(supplier.id),
        "partner_id": int(partner.id),
        "employee_ils_id": int(emp_ils.id),
        "employee_usd_id": int(emp_usd.id),
        "salary_expense_ils_id": int(salary_ils.id),
        "salary_expense_usd_id": int(salary_usd.id),
        "employee_advance_expense_id": int(adv_exp.id),
        "employee_advance_payment_id": None,
        "utilities_expense_id": int(exp_util.id),
        "rent_expense_id": int(exp_rent.id),
        "rent_payment_id": None,
        "marketing_expense_id": int(exp_mkt.id),
        "marketing_payment_id": None,
        "warehouse_main_id": int(wh_main.id),
        "warehouse_exchange_id": int(wh_exchange.id),
        "warehouse_partner_id": int(wh_partner.id),
        "warehouse_online_id": int(wh_online.id),
        "warehouse_inventory_id": int(wh_inventory.id),
        "product_ils_id": int(prod_ils.id),
        "product_usd_id": int(prod_usd.id),
        "exchange_out_id": None,
        "transfer_to_online_id": None,
        "transfer_online_to_inventory_id": None,
        "shipment_id": int(shipment.id),
        "shipment_other_ids": [],
        "shipment_payment_id": None,
        "shipment_expense_ids": [],
        "stock_adjustment_id": int(stock_adj.id),
        "stock_adjustment_expense_id": None,
        "note_ids": [],
        "sale_id": int(sale_ils.id),
        "sale_payment_id": None,
        "sale_credit_id": int(sale_credit.id),
        "sale_card_id": int(sale_card.id),
        "sale_card_payment_id": None,
        "sale_return_id": int(sale_return.id),
        "invoice_id": int(inv_usd.id),
        "invoice_payment_id": None,
        "service_id": int(service.id),
        "preorder_id": None,
        "expense_customer_id": None,
        "expense_supplier_id": None,
        "expense_partner_id": None,
        "supplier_settlement_id": None,
        "partner_settlement_id": None,
    }

    db.session.flush()
    created["sale_payment_id"] = int(pay_sale_cash.id)
    created["invoice_payment_id"] = int(pay_invoice_usd.id)
    created["preorder_id"] = int(preorder.id)
    created["expense_customer_id"] = int(ex_customer.id)
    created["expense_supplier_id"] = int(ex_supplier.id)
    created["expense_partner_id"] = int(ex_partner.id)
    created["employee_advance_payment_id"] = int(db.session.query(Payment.id).filter(Payment.expense_id == adv_exp.id, Payment.reference == f"DemoSeed:{seed_tag}:ADV_PAY").scalar() or 0) or None
    created["rent_payment_id"] = int(db.session.query(Payment.id).filter(Payment.expense_id == exp_rent.id, Payment.reference == f"DemoSeed:{seed_tag}:RENT_PAY").scalar() or 0) or None
    created["marketing_payment_id"] = int(db.session.query(Payment.id).filter(Payment.expense_id == exp_mkt.id, Payment.reference == f"DemoSeed:{seed_tag}:MKT_PAY").scalar() or 0) or None
    created["sale_card_payment_id"] = int(db.session.query(Payment.id).filter(Payment.sale_id == sale_card.id, Payment.reference == f"DemoSeed:{seed_tag}:SALE_CARD").scalar() or 0) or None
    created["exchange_out_id"] = int(tx_out.id)
    created["transfer_to_online_id"] = int(transfer_to_online.id)
    created["transfer_online_to_inventory_id"] = int(transfer_online_to_inventory.id)
    created["shipment_payment_id"] = int(pay_shipment.id)
    created["shipment_expense_ids"] = [int(ship_exp_freight.id), int(ship_exp_customs.id)]
    created["shipment_other_ids"] = [int(shipment_delivered.id), int(shipment_cancelled.id)]
    created["stock_adjustment_expense_id"] = int(adj_expense.id)
    created["note_ids"] = [int(n.id) for n in notes]

    if with_settlements:
        from_dt = now - timedelta(days=5)
        to_dt = now + timedelta(days=1)
        ss = build_supplier_settlement_draft(supplier.id, from_dt, to_dt, currency="ILS")
        ps = build_partner_settlement_draft(partner.id, from_dt, to_dt, currency="ILS")
        db.session.add_all([ss, ps])
        db.session.flush()
        ss.status = SupplierSettlementStatus.DRAFT.value
        ps.status = PartnerSettlementStatus.DRAFT.value
        ss.mark_confirmed()
        ps.mark_confirmed()
        db.session.flush()
        created["supplier_settlement_id"] = int(ss.id)
        created["partner_settlement_id"] = int(ps.id)

    if cover_all_gl_types:
        created["gl_coverage_source_types"] = _create_demo_gl_coverage_batches(
            seed_tag=seed_tag,
            customer_id=int(customer.id),
            supplier_id=int(supplier.id),
            partner_id=int(partner.id),
            employee_id=int(emp_ils.id),
        )

    if full_system:
        created.update(_seed_permissions_and_owner_user())
        SystemSettings.set_setting("enable_bank_reconciliation", True, data_type="boolean", commit=False)
        SystemSettings.set_setting("enable_cost_centers", True, data_type="boolean", commit=False)
        SystemSettings.set_setting("enable_projects", True, data_type="boolean", commit=False)
        SystemSettings.set_setting("auto_gl_posting", True, data_type="boolean", commit=False)
        SystemSettings.set_setting("enable_budget_module", True, data_type="boolean", commit=False)
        SystemSettings.set_setting("enable_fixed_assets", True, data_type="boolean", commit=False)
        SystemSettings.set_setting("enable_auto_depreciation", False, data_type="boolean", commit=False)

        _ensure_account("1010_BANK", "البنك")
        _ensure_account("1020_CARD_CLEARING", "مقاصة البطاقات")
        _ensure_account("1500_FIXED_ASSETS", "أصول ثابتة")
        _ensure_account("1600_ACCUM_DEPR", "مجمع الإهلاك")
        _ensure_account("6600_DEPRECIATION", "مصروف الإهلاك")
        _ensure_account("6900_PROJECT_COST", "تكاليف مشاريع")
        _ensure_account("7900_PROJECT_REVENUE", "إيرادات مشاريع")
        _ensure_account("3900_INCOME_SUMMARY", "ملخص الدخل")
        _ensure_account("1030_CHECKS", "شيكات")
        _ensure_account("6200_RENT", "إيجار")

        site = Site.query.filter(Site.branch_id == branch.id).order_by(Site.id.asc()).first()
        if not site:
            site = Site(branch_id=branch.id, name=f"موقع ديمو {seed_tag}", code=f"SITE-{seed_tag}", is_active=True, manager_user_id=user.id, manager_employee_id=emp_ils.id, address="", city="")
            db.session.add(site)
            db.session.flush()

        bank_ils = BankAccount.query.filter(BankAccount.code == f"BNK-{seed_tag}-ILS").one_or_none()
        if not bank_ils:
            bank_ils = BankAccount(
                code=f"BNK-{seed_tag}-ILS",
                name=f"حساب بنكي ILS {seed_tag}",
                bank_name="Demo Bank",
                account_number=f"ACCT-{seed_tag}-ILS",
                currency="ILS",
                branch_id=branch.id,
                gl_account_code="1010_BANK",
                opening_balance=_q2("10000"),
                current_balance=_q2("10000"),
                created_by=user.id,
                updated_by=user.id,
                is_active=True,
            )
            db.session.add(bank_ils)
            db.session.flush()

        st_date = now.date()
        stmt = BankStatement.query.filter(BankStatement.statement_number == f"STMT-{seed_tag}-1").one_or_none()
        if not stmt:
            stmt = BankStatement(
                bank_account_id=bank_ils.id,
                statement_number=f"STMT-{seed_tag}-1",
                statement_date=st_date,
                period_start=st_date - timedelta(days=7),
                period_end=st_date,
                opening_balance=_q2("10000"),
                closing_balance=_q2("10000") + _q2("150") - _q2("75"),
                total_deposits=_q2("150"),
                total_withdrawals=_q2("75"),
                status="IMPORTED",
                created_by=user.id,
                updated_by=user.id,
            )
            db.session.add(stmt)
            db.session.flush()

        if not BankTransaction.query.filter(BankTransaction.statement_id == stmt.id).first():
            tx1 = BankTransaction(
                bank_account_id=bank_ils.id,
                statement_id=stmt.id,
                transaction_date=st_date,
                reference=f"DEP-{seed_tag}",
                description="إيداع مرتبط ببيع نقدي",
                debit=_q2("0"),
                credit=_q2("150"),
                matched=True,
                payment_id=pay_sale_cash.id,
                notes="",
            )
            tx2 = BankTransaction(
                bank_account_id=bank_ils.id,
                statement_id=stmt.id,
                transaction_date=st_date,
                reference=f"WDR-{seed_tag}",
                description="سحب مرتبط بمصروف",
                debit=_q2("75"),
                credit=_q2("0"),
                matched=False,
                payment_id=pay_rent.id,
                notes="",
            )
            db.session.add_all([tx1, tx2])

        recon = BankReconciliation.query.filter(BankReconciliation.reconciliation_number == f"RECON-{seed_tag}-1").one_or_none()
        if not recon:
            recon = BankReconciliation(
                bank_account_id=bank_ils.id,
                reconciliation_number=f"RECON-{seed_tag}-1",
                period_start=(st_date - timedelta(days=7)),
                period_end=st_date,
                book_balance=_q2("10000"),
                bank_balance=_q2("10075"),
                unmatched_book_count=1,
                unmatched_bank_count=1,
                unmatched_book_amount=_q2("75"),
                unmatched_bank_amount=_q2("0"),
                reconciled_by=user.id,
                status="DRAFT",
                notes="",
            )
            db.session.add(recon)
            db.session.flush()

        cc_root = CostCenter.query.filter(CostCenter.code == f"CC-{seed_tag}-ROOT").one_or_none()
        if not cc_root:
            cc_root = CostCenter(code=f"CC-{seed_tag}-ROOT", name=f"مركز تكلفة رئيسي {seed_tag}", manager_id=user.id, gl_account_code="6900_PROJECT_COST", budget_amount=_q2("50000"), is_active=True, created_by=user.id, updated_by=user.id)
            db.session.add(cc_root)
            db.session.flush()
        cc_sales = CostCenter.query.filter(CostCenter.code == f"CC-{seed_tag}-SALES").one_or_none()
        if not cc_sales:
            cc_sales = CostCenter(code=f"CC-{seed_tag}-SALES", name=f"مركز مبيعات {seed_tag}", parent_id=cc_root.id, manager_id=user.id, gl_account_code="7900_PROJECT_REVENUE", budget_amount=_q2("20000"), is_active=True, created_by=user.id, updated_by=user.id)
            db.session.add(cc_sales)
            db.session.flush()

        if not CostCenterAllocation.query.filter(CostCenterAllocation.source_type == "SALE", CostCenterAllocation.source_id == sale_ils.id, CostCenterAllocation.cost_center_id == cc_sales.id).one_or_none():
            db.session.add(CostCenterAllocation(cost_center_id=cc_sales.id, source_type="SALE", source_id=sale_ils.id, amount=_q2("150"), percentage=_q2("100"), allocation_date=now.date(), notes=f"DemoSeed:{seed_tag}:CC_SALE"))
        if not CostCenterAllocation.query.filter(CostCenterAllocation.source_type == "EXPENSE", CostCenterAllocation.source_id == exp_rent.id, CostCenterAllocation.cost_center_id == cc_root.id).one_or_none():
            db.session.add(CostCenterAllocation(cost_center_id=cc_root.id, source_type="EXPENSE", source_id=exp_rent.id, amount=_q2("1200"), percentage=_q2("100"), allocation_date=now.date(), notes=f"DemoSeed:{seed_tag}:CC_RENT"))
        if not CostCenterAlert.query.filter(CostCenterAlert.cost_center_id == cc_root.id).first():
            db.session.add(CostCenterAlert(cost_center_id=cc_root.id, alert_type="BUDGET_WARNING", threshold_type="PERCENTAGE", threshold_value=_q2("80"), is_active=True, notify_manager=True, trigger_count=0))

        prj = Project.query.filter(Project.code == f"PRJ-{seed_tag}-1").one_or_none()
        if not prj:
            prj = Project(
                code=f"PRJ-{seed_tag}-1",
                name=f"مشروع ديمو {seed_tag}",
                client_id=customer.id,
                start_date=(now - timedelta(days=30)).date(),
                planned_end_date=(now + timedelta(days=30)).date(),
                budget_amount=_q2("30000"),
                estimated_cost=_q2("12000"),
                estimated_revenue=_q2("20000"),
                cost_center_id=cc_root.id,
                manager_id=user.id,
                branch_id=branch.id,
                status="ACTIVE",
                completion_percentage=_q2("35"),
                description="",
                notes=f"DemoSeed:{seed_tag}:PROJECT",
                is_active=True,
                created_by=user.id,
                updated_by=user.id,
            )
            db.session.add(prj)
            db.session.flush()

        phase = db.session.query(ProjectPhase).filter(ProjectPhase.project_id == prj.id, ProjectPhase.order == 1).one_or_none()
        if not phase:
            phase = ProjectPhase(project_id=prj.id, name="مرحلة 1", order=1, start_date=(now - timedelta(days=30)).date(), end_date=None, planned_budget=_q2("15000"), actual_cost=_q2("0"), status="IN_PROGRESS", completion_percentage=_q2("40"), description="")
            db.session.add(phase)
            db.session.flush()

        if not db.session.query(ProjectCost).filter(ProjectCost.project_id == prj.id, ProjectCost.source_id == exp_rent.id, ProjectCost.cost_type == "EXPENSE").first():
            db.session.add(ProjectCost(project_id=prj.id, phase_id=phase.id, cost_type="EXPENSE", source_id=exp_rent.id, amount=_q2("1200"), cost_date=now.date(), description="مصروف مشروع", notes=""))
        if not db.session.query(ProjectRevenue).filter(ProjectRevenue.project_id == prj.id, ProjectRevenue.source_id == sale_ils.id, ProjectRevenue.revenue_type == "SALE").first():
            db.session.add(ProjectRevenue(project_id=prj.id, phase_id=phase.id, revenue_type="SALE", source_id=sale_ils.id, amount=_q2("150"), revenue_date=now.date(), description="إيراد مشروع", notes=""))

        milestone = db.session.query(ProjectMilestone).filter(ProjectMilestone.project_id == prj.id, ProjectMilestone.milestone_number == f"MS-{seed_tag}-1").one_or_none()
        if not milestone:
            milestone = ProjectMilestone(
                project_id=prj.id,
                phase_id=phase.id,
                milestone_number=f"MS-{seed_tag}-1",
                name="معلم 1",
                description="",
                due_date=(now + timedelta(days=10)).date(),
                billing_amount=_q2("5000"),
                tax_rate=_q2("0"),
                tax_amount=_q2("0"),
                billing_percentage=_q2("25"),
                status="IN_PROGRESS",
                approval_required=False,
                notes="",
            )
            db.session.add(milestone)
            db.session.flush()

        change_order = db.session.query(ProjectChangeOrder).filter(ProjectChangeOrder.change_number == f"CO-{seed_tag}-1").one_or_none()
        if not change_order:
            change_order = ProjectChangeOrder(
                project_id=prj.id,
                change_number=f"CO-{seed_tag}-1",
                title="تغيير نطاق",
                description="",
                requested_by=user.id,
                requested_date=now.date(),
                reason="",
                scope_change="",
                cost_impact=_q2("750"),
                schedule_impact_days=2,
                status="SUBMITTED",
                notes="",
            )
            db.session.add(change_order)
            db.session.flush()

        risk = db.session.query(ProjectRisk).filter(ProjectRisk.risk_number == f"RSK-{seed_tag}-1").one_or_none()
        if not risk:
            risk = ProjectRisk(
                project_id=prj.id,
                risk_number=f"RSK-{seed_tag}-1",
                title="مخاطر تأخير",
                description="",
                category="SCHEDULE",
                probability="MEDIUM",
                impact="MODERATE",
                risk_score=_q2("7.5"),
                status="IDENTIFIED",
                mitigation_plan="",
                contingency_plan="",
                owner_id=user.id,
                identified_date=now.date(),
                notes="",
            )
            db.session.add(risk)
            db.session.flush()

        fy = int(now.year)
        budget = db.session.query(Budget).filter(Budget.fiscal_year == fy, Budget.account_code == "6200_RENT", Budget.branch_id == branch.id, Budget.site_id == site.id).one_or_none()
        if not budget:
            budget = Budget(fiscal_year=fy, account_code="6200_RENT", branch_id=branch.id, site_id=site.id, allocated_amount=_q2("120000"), notes="", is_active=True)
            db.session.add(budget)
            db.session.flush()
        if not db.session.query(BudgetCommitment).filter(BudgetCommitment.source_type == "EXPENSE", BudgetCommitment.source_id == exp_rent.id).first():
            db.session.add(BudgetCommitment(budget_id=budget.id, source_type="EXPENSE", source_id=exp_rent.id, committed_amount=_q2("1200"), commitment_date=now.date(), status="APPROVED", notes=""))

        fac = db.session.query(FixedAssetCategory).filter(FixedAssetCategory.code == f"FAC-{seed_tag}").one_or_none()
        if not fac:
            fac = FixedAssetCategory(code=f"FAC-{seed_tag}", name=f"فئة أصول {seed_tag}", account_code="1500_FIXED_ASSETS", depreciation_account_code="1600_ACCUM_DEPR", useful_life_years=5, depreciation_method="STRAIGHT_LINE", depreciation_rate=_q2("0"), is_active=True)
            db.session.add(fac)
            db.session.flush()

        asset = db.session.query(FixedAsset).filter(FixedAsset.asset_number == f"AST-{seed_tag}-1").one_or_none()
        if not asset:
            asset = FixedAsset(
                asset_number=f"AST-{seed_tag}-1",
                name=f"أصل ديمو {seed_tag}",
                category_id=fac.id,
                branch_id=branch.id,
                site_id=site.id,
                purchase_date=(now - timedelta(days=200)).date(),
                purchase_price=_q2("25000"),
                supplier_id=partner.id,
                serial_number=f"SN-{seed_tag}-1",
                barcode=f"ASTBC{seed_tag}",
                location="",
                status="ACTIVE",
                notes="",
            )
            db.session.add(asset)
            db.session.flush()

        dep = db.session.query(AssetDepreciation).filter(AssetDepreciation.asset_id == asset.id, AssetDepreciation.fiscal_year == fy, AssetDepreciation.fiscal_month == 1).one_or_none()
        if not dep:
            dep = AssetDepreciation(
                asset_id=asset.id,
                fiscal_year=fy,
                fiscal_month=1,
                depreciation_date=(now - timedelta(days=30)).date(),
                depreciation_amount=_q2("400"),
                accumulated_depreciation=_q2("400"),
                book_value=_q2("24600"),
                gl_batch_id=(db.session.query(GLBatch.id).order_by(GLBatch.id.asc()).limit(1).scalar() or None),
                notes="",
            )
            db.session.add(dep)

        maint = db.session.query(AssetMaintenance).filter(AssetMaintenance.asset_id == asset.id).order_by(AssetMaintenance.id.asc()).first()
        if not maint:
            maint = AssetMaintenance(
                asset_id=asset.id,
                maintenance_date=(now - timedelta(days=10)).date(),
                maintenance_type="فحص",
                cost=_q2("50"),
                expense_id=exp_util.id,
                description="",
                next_maintenance_date=(now + timedelta(days=20)).date(),
            )
            db.session.add(maint)

        wf_def = db.session.query(WorkflowDefinition).filter(WorkflowDefinition.workflow_code == f"WF-{seed_tag}-EXP").one_or_none()
        if not wf_def:
            wf_def = WorkflowDefinition(
                workflow_code=f"WF-{seed_tag}-EXP",
                workflow_name="Expense Approval",
                workflow_name_ar="اعتماد مصروف",
                description="",
                workflow_type="APPROVAL",
                entity_type="EXPENSE",
                steps_definition=[{"step": 1, "name": "مراجعة"}, {"step": 2, "name": "اعتماد"}],
                auto_start=False,
                is_active=True,
                version=1,
                timeout_hours=None,
                escalation_rules=None,
                created_by=user.id,
                updated_by=user.id,
            )
            db.session.add(wf_def)
            db.session.flush()

        wf_inst = db.session.query(WorkflowInstance).filter(WorkflowInstance.instance_code == f"WFI-{seed_tag}-1").one_or_none()
        if not wf_inst:
            wf_inst = WorkflowInstance(
                workflow_definition_id=wf_def.id,
                instance_code=f"WFI-{seed_tag}-1",
                entity_type="EXPENSE",
                entity_id=exp_rent.id,
                status="IN_PROGRESS",
                current_step=1,
                total_steps=2,
                started_by=user.id,
                started_at=now,
                due_date=(now + timedelta(days=3)),
                context_data={"seed_tag": seed_tag},
            )
            db.session.add(wf_inst)
            db.session.flush()
            db.session.add(WorkflowAction(workflow_instance_id=wf_inst.id, step_number=1, step_name="مراجعة", action_type="REVIEW", actor_id=user.id, action_date=now, decision="", comments="", attachments=None))

        if db.session.query(Archive.id).order_by(Archive.id.asc()).first() is None:
            Archive.archive_record(sale_ils, reason=f"DemoSeed:{seed_tag}:ARCHIVE_SALE", user_id=user.id)

        plan = db.session.query(SaaSPlan).filter(SaaSPlan.name == f"Demo Plan {seed_tag}").one_or_none()
        if not plan:
            plan = SaaSPlan(
                name=f"Demo Plan {seed_tag}",
                description="",
                price_monthly=_q2("49.99"),
                price_yearly=_q2("499.00"),
                currency="USD",
                max_users=5,
                max_invoices=1000,
                storage_gb=10,
                features="",
                is_active=True,
                is_popular=False,
                sort_order=1,
            )
            db.session.add(plan)
            db.session.flush()

        sub = db.session.query(SaaSSubscription).filter(SaaSSubscription.customer_id == customer.id, SaaSSubscription.plan_id == plan.id).first()
        if not sub:
            sub = SaaSSubscription(
                customer_id=customer.id,
                plan_id=plan.id,
                status="active",
                start_date=(now - timedelta(days=15)),
                end_date=(now + timedelta(days=15)),
                trial_end_date=None,
                auto_renew=True,
                cancelled_at=None,
                cancelled_by=None,
                cancellation_reason=None,
            )
            db.session.add(sub)
            db.session.flush()

        inv = db.session.query(SaaSInvoice).filter(SaaSInvoice.invoice_number == f"SAAS-{seed_tag}-1").one_or_none()
        if not inv:
            inv = SaaSInvoice(
                invoice_number=f"SAAS-{seed_tag}-1",
                subscription_id=sub.id,
                amount=plan.price_monthly,
                currency=plan.currency,
                status="pending",
                due_date=(now + timedelta(days=7)),
                paid_at=None,
                payment_method=None,
                notes="",
            )
            db.session.add(inv)

        extra_products_created = []
        numeric_barcode = f"{int(uuid.uuid4().hex[:13], 16) % 10**13:013d}"
        if not Product.query.filter(Product.barcode == numeric_barcode).first():
            p_num = Product(
                name=f"منتج باركود رقمي {seed_tag}",
                barcode=numeric_barcode,
                currency="ILS",
                price=_q2("25"),
                selling_price=_q2("25"),
                purchase_price=_q2("15"),
                tax_rate=_q2("0"),
                supplier_id=supplier.id,
            )
            db.session.add(p_num)
            extra_products_created.append(p_num)
        for i in range(scale_i):
            p = Product(
                name=f"منتج موسع {seed_tag}-{i+1}",
                barcode=f"EXT{seed_tag}{i+1:02d}",
                currency="ILS",
                price=_q2(str(50 + i * 5)),
                selling_price=_q2(str(50 + i * 5)),
                purchase_price=_q2(str(30 + i * 4)),
                tax_rate=_q2("0"),
                supplier_id=supplier.id,
            )
            db.session.add(p)
            extra_products_created.append(p)
        db.session.flush()

        extra_products = [p for p in extra_products_created if getattr(p, "id", None)] or [prod_ils]
        for i in range(scale_i * 3):
            s = Sale(customer_id=customer.id, seller_id=user.id, sale_date=now - timedelta(days=i), status="CONFIRMED", currency="ILS", tax_rate=_q2("0"), shipping_cost=_q2("0"), discount_total=_q2("0"))
            db.session.add(s)
            db.session.flush()
            pr = extra_products[i % len(extra_products)]
            db.session.add(SaleLine(sale_id=s.id, product_id=pr.id, warehouse_id=wh_main.id, quantity=1, unit_price=_q2(pr.selling_price or 0), discount_rate=_q2("0"), tax_rate=_q2("0")))
            pmt = Payment(
                payment_number=f"{payment_prefix}-SCALE-{i+1}",
                payment_date=now - timedelta(days=i),
                total_amount=_q2(pr.selling_price or 0),
                currency="ILS",
                method=PaymentMethod.CARD.value if i % 2 == 0 else PaymentMethod.CASH.value,
                status=PaymentStatus.COMPLETED.value,
                direction=PaymentDirection.IN.value,
                entity_type=PaymentEntityType.SALE.value,
                sale_id=s.id,
                created_by=user.id,
                reference=f"DemoSeed:{seed_tag}:SCALE_SALE_{i+1}",
            )
            if i % 3 == 0:
                _attach_splits(pmt, [(PaymentMethod.CARD.value, _q2(pr.selling_price or 0) - _q2("10"), {"brand": "VISA", "last4": "4242"}), (PaymentMethod.CASH.value, _q2("10"), {})])
            else:
                _attach_one_split(pmt)
            db.session.add(pmt)

    if update_balances:
        update_customer_balance_components(customer.id)
        update_supplier_balance_components(supplier.id)
        update_partner_balance_components(partner.id)

    return created
