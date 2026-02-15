from __future__ import annotations

import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


ROOT = str(Path(__file__).resolve().parents[1])
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
os.chdir(ROOT)


TOKENS = [
    "test",
    "demo",
    "sample",
    "dummy",
    "fake",
    "tmp",
    "temp",
    "qa",
    "sandbox",
    "staging",
    "dev",
    "اختبار",
    "تجربة",
    "تجريبي",
    "ديمو",
    "وهمي",
    "مؤقت",
]

TOKEN_RE = re.compile(r"(" + "|".join(re.escape(t) for t in TOKENS) + r")", re.IGNORECASE)


@dataclass(frozen=True)
class CandidateRow:
    kind: str
    id: int
    label: str


def _env_bool(name: str, default: bool = False) -> bool:
    raw = str(os.getenv(name, "") or "").strip().lower()
    if raw in ("1", "true", "yes", "y", "on"):
        return True
    if raw in ("0", "false", "no", "n", "off"):
        return False
    return default


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except Exception:
        return default


def _norm(s: str | None) -> str:
    return (s or "").strip()


def _matches_any(*values: str | None) -> bool:
    for v in values:
        if v and TOKEN_RE.search(v):
            return True
    return False


def _print_section(title: str) -> None:
    print("")
    print("=" * len(title))
    print(title)
    print("=" * len(title))


def _chunked_ids(ids: list[int], size: int = 1000) -> Iterable[list[int]]:
    for i in range(0, len(ids), size):
        yield ids[i : i + size]


def run() -> None:
    from app import create_app
    from extensions import db
    from models import (
        Check,
        Customer,
        Expense,
        GLBatch,
        Invoice,
        InvoiceLine,
        OnlineCart,
        OnlineCartItem,
        OnlinePayment,
        OnlinePreOrder,
        OnlinePreOrderItem,
        PartnerSettlementLine,
        Payment,
        PreOrder,
        Product,
        ProductPartner,
        ProductPartnerShare,
        ProductRating,
        ProductSupplierLoan,
        ProjectResource,
        Sale,
        SaleLine,
        SaleReturn,
        SaleReturnLine,
        Shipment,
        ShipmentItem,
        ShipmentPartner,
        ServicePart,
        ServiceRequest,
        ServiceTask,
        StockLevel,
        StockAdjustmentItem,
        Supplier,
        SupplierSettlementLine,
        TaxEntry,
        Partner,
        Transfer,
        ExchangeTransaction,
        Warehouse,
        WarehousePartnerShare,
    )
    from sqlalchemy import delete as sa_delete, func, or_, select, update as sa_update

    limit = _env_int("LIMIT", 50)
    confirm_delete = _env_bool("CONFIRM_DELETE", False)
    require_phrase = str(os.getenv("CONFIRM_PHRASE", "") or "").strip()
    require_phrase_ok = (require_phrase == "DELETE_TEST_DATA")

    app = create_app()
    with app.app_context():
        try:
            db.session.execute(select(1)).scalar()
        except Exception as e:
            try:
                from sqlalchemy.exc import OperationalError
            except Exception:
                OperationalError = None
            if OperationalError is not None and isinstance(e, OperationalError):
                print("DB connection failed.")
                print(f"SQLALCHEMY_DATABASE_URI={app.config.get('SQLALCHEMY_DATABASE_URI')}")
                print("Set DATABASE_URL / PGHOST / PGPORT to a reachable database and retry.")
                sys.exit(1)
            raise

        def like_any(col):
            return or_(*[func.lower(col).like(f"%{t.lower()}%") for t in TOKENS])

        customers = (
            db.session.query(Customer)
            .filter(
                or_(
                    like_any(Customer.name),
                    like_any(Customer.email),
                    like_any(Customer.phone),
                    like_any(Customer.whatsapp),
                    like_any(Customer.notes),
                    like_any(Customer.address),
                )
            )
            .order_by(Customer.id)
            .all()
        )
        products = (
            db.session.query(Product)
            .filter(
                or_(
                    like_any(Product.name),
                    like_any(Product.sku),
                    like_any(Product.barcode),
                    like_any(Product.part_number),
                    like_any(Product.brand),
                    like_any(Product.notes),
                    like_any(Product.description),
                    like_any(Product.online_name),
                )
            )
            .order_by(Product.id)
            .all()
        )
        suppliers = (
            db.session.query(Supplier)
            .filter(
                or_(
                    like_any(Supplier.name),
                    like_any(Supplier.email),
                    like_any(Supplier.phone),
                    like_any(Supplier.contact),
                    like_any(Supplier.notes),
                    like_any(Supplier.address),
                    like_any(Supplier.identity_number),
                )
            )
            .order_by(Supplier.id)
            .all()
        )
        partners = (
            db.session.query(Partner)
            .filter(or_(like_any(Partner.name), like_any(Partner.notes)))
            .order_by(Partner.id)
            .all()
        )

        sales = (
            db.session.query(Sale)
            .filter(
                or_(
                    like_any(Sale.sale_number),
                    like_any(Sale.notes),
                    like_any(Sale.receiver_name),
                    like_any(Sale.shipping_address),
                    like_any(Sale.billing_address),
                    like_any(Sale.cancel_reason),
                    like_any(Sale.archive_reason),
                )
            )
            .order_by(Sale.id)
            .all()
        )
        invoices = (
            db.session.query(Invoice)
            .filter(
                or_(
                    like_any(Invoice.invoice_number),
                    like_any(Invoice.notes),
                    like_any(Invoice.terms),
                    like_any(Invoice.cancel_reason),
                )
            )
            .order_by(Invoice.id)
            .all()
        )
        service_requests = (
            db.session.query(ServiceRequest)
            .filter(
                or_(
                    like_any(ServiceRequest.service_number),
                    like_any(ServiceRequest.vehicle_vrn),
                    like_any(ServiceRequest.vehicle_model),
                    like_any(ServiceRequest.chassis_number),
                    like_any(ServiceRequest.engineer_notes),
                    like_any(ServiceRequest.description),
                    like_any(ServiceRequest.problem_description),
                    like_any(ServiceRequest.diagnosis),
                    like_any(ServiceRequest.resolution),
                    like_any(ServiceRequest.notes),
                    like_any(ServiceRequest.cancel_reason),
                    like_any(ServiceRequest.archive_reason),
                )
            )
            .order_by(ServiceRequest.id)
            .all()
        )
        preorders = (
            db.session.query(PreOrder)
            .filter(or_(like_any(PreOrder.reference), like_any(PreOrder.notes), like_any(PreOrder.cancel_reason)))
            .order_by(PreOrder.id)
            .all()
        )
        online_preorders = (
            db.session.query(OnlinePreOrder)
            .filter(
                or_(
                    like_any(OnlinePreOrder.order_number),
                    like_any(OnlinePreOrder.notes),
                    like_any(OnlinePreOrder.shipping_address),
                    like_any(OnlinePreOrder.billing_address),
                )
            )
            .order_by(OnlinePreOrder.id)
            .all()
        )
        payments = (
            db.session.query(Payment)
            .filter(
                or_(
                    like_any(Payment.payment_number),
                    like_any(Payment.reference),
                    like_any(Payment.receipt_number),
                    like_any(Payment.notes),
                    like_any(Payment.receiver_name),
                    like_any(Payment.deliverer_name),
                    like_any(Payment.check_number),
                    like_any(Payment.bank_transfer_ref),
                    like_any(Payment.archive_reason),
                )
            )
            .order_by(Payment.id)
            .all()
        )
        expenses = (
            db.session.query(Expense)
            .filter(
                or_(
                    like_any(Expense.description),
                    like_any(Expense.notes),
                    like_any(Expense.tax_invoice_number),
                    like_any(Expense.payment_details),
                    like_any(Expense.bank_transfer_ref),
                    like_any(Expense.online_ref),
                )
            )
            .order_by(Expense.id)
            .all()
        )
        shipments = (
            db.session.query(Shipment)
            .filter(or_(like_any(Shipment.number), like_any(Shipment.shipment_number), like_any(Shipment.tracking_number), like_any(Shipment.notes)))
            .order_by(Shipment.id)
            .all()
        )

        customer_ids = [int(c.id) for c in customers]
        product_ids = [int(p.id) for p in products]
        supplier_ids = [int(s.id) for s in suppliers]
        partner_ids = [int(p.id) for p in partners]
        sale_token_ids = [int(s.id) for s in sales]
        invoice_token_ids = [int(i.id) for i in invoices]
        service_token_ids = [int(s.id) for s in service_requests]
        preorder_token_ids = [int(p.id) for p in preorders]
        online_preorder_token_ids = [int(o.id) for o in online_preorders]
        payment_token_ids = [int(p.id) for p in payments]
        expense_token_ids = [int(e.id) for e in expenses]
        shipment_token_ids = [int(s.id) for s in shipments]

        _print_section("المطابقات المحتملة (للمراجعة فقط)")
        print(f"DB={app.config.get('SQLALCHEMY_DATABASE_URI')}")
        print(f"LIMIT={limit}  CONFIRM_DELETE={int(confirm_delete)}  CONFIRM_PHRASE_OK={int(require_phrase_ok)}")
        print(
            " ".join(
                [
                    f"customers={len(customer_ids)}",
                    f"products={len(product_ids)}",
                    f"suppliers={len(supplier_ids)}",
                    f"partners={len(partner_ids)}",
                    f"sales={len(sale_token_ids)}",
                    f"invoices={len(invoice_token_ids)}",
                    f"services={len(service_token_ids)}",
                    f"preorders={len(preorder_token_ids)}",
                    f"online_preorders={len(online_preorder_token_ids)}",
                    f"payments={len(payment_token_ids)}",
                    f"expenses={len(expense_token_ids)}",
                    f"shipments={len(shipment_token_ids)}",
                ]
            )
        )

        def show_rows(kind: str, rows: list[CandidateRow]) -> None:
            _print_section(kind)
            if not rows:
                print("(لا يوجد)")
                return
            for r in rows[:limit]:
                print(f"- id={r.id}\t{r.label}")
            if len(rows) > limit:
                print(f"... ({len(rows) - limit} مخفي)")

        customer_rows: list[CandidateRow] = []
        for c in customers:
            customer_rows.append(
                CandidateRow(
                    kind="Customer",
                    id=int(c.id),
                    label=" | ".join(
                        [
                            _norm(c.name),
                            _norm(c.phone),
                            _norm(c.email),
                            _norm(c.whatsapp),
                        ]
                    ).strip(" |"),
                )
            )
        product_rows: list[CandidateRow] = []
        for p in products:
            product_rows.append(
                CandidateRow(
                    kind="Product",
                    id=int(p.id),
                    label=" | ".join(
                        [
                            _norm(p.name),
                            _norm(p.sku),
                            _norm(p.barcode),
                            _norm(p.part_number),
                        ]
                    ).strip(" |"),
                )
            )
        supplier_rows: list[CandidateRow] = []
        for s in suppliers:
            supplier_rows.append(
                CandidateRow(
                    kind="Supplier",
                    id=int(s.id),
                    label=" | ".join(
                        [
                            _norm(s.name),
                            _norm(s.phone),
                            _norm(s.email),
                            _norm(s.identity_number),
                        ]
                    ).strip(" |"),
                )
            )
        partner_rows: list[CandidateRow] = []
        for p in partners:
            partner_rows.append(CandidateRow(kind="Partner", id=int(p.id), label=_norm(p.name)))

        show_rows("العملاء (Customers)", customer_rows)
        show_rows("المنتجات (Products)", product_rows)
        show_rows("الموردون (Suppliers)", supplier_rows)
        show_rows("الشركاء (Partners)", partner_rows)

        show_rows(
            "المبيعات (Sales)",
            [
                CandidateRow(
                    kind="Sale",
                    id=int(s.id),
                    label=" | ".join([_norm(s.sale_number), _norm(s.receiver_name), _norm((s.notes or "").replace("\n", " "))[:80]]).strip(" |"),
                )
                for s in sales
            ],
        )
        show_rows(
            "الفواتير (Invoices)",
            [
                CandidateRow(
                    kind="Invoice",
                    id=int(i.id),
                    label=" | ".join([_norm(i.invoice_number), _norm((i.notes or "").replace("\n", " "))[:80]]).strip(" |"),
                )
                for i in invoices
            ],
        )
        show_rows(
            "طلبات الصيانة (Service Requests)",
            [
                CandidateRow(
                    kind="ServiceRequest",
                    id=int(s.id),
                    label=" | ".join([_norm(s.service_number), _norm(s.vehicle_vrn), _norm((s.notes or s.description or "").replace("\n", " "))[:80]]).strip(" |"),
                )
                for s in service_requests
            ],
        )
        show_rows(
            "الطلبات المسبقة (PreOrders)",
            [CandidateRow(kind="PreOrder", id=int(p.id), label=" | ".join([_norm(p.reference), _norm((p.notes or "").replace("\n", " "))[:80]]).strip(" |")) for p in preorders],
        )
        show_rows(
            "طلبات الأونلاين (Online PreOrders)",
            [
                CandidateRow(
                    kind="OnlinePreOrder",
                    id=int(o.id),
                    label=" | ".join([_norm(o.order_number), _norm((o.notes or "").replace("\n", " "))[:80]]).strip(" |"),
                )
                for o in online_preorders
            ],
        )
        show_rows(
            "الدفعات (Payments)",
            [
                CandidateRow(
                    kind="Payment",
                    id=int(p.id),
                    label=" | ".join([_norm(p.payment_number), _norm(p.reference), _norm((p.notes or "").replace("\n", " "))[:80]]).strip(" |"),
                )
                for p in payments
            ],
        )
        show_rows(
            "المصاريف (Expenses)",
            [
                CandidateRow(
                    kind="Expense",
                    id=int(e.id),
                    label=" | ".join([_norm(e.description), _norm(e.tax_invoice_number), _norm((e.notes or "").replace("\n", " "))[:80]]).strip(" |"),
                )
                for e in expenses
            ],
        )
        show_rows(
            "الشحنات (Shipments)",
            [
                CandidateRow(
                    kind="Shipment",
                    id=int(s.id),
                    label=" | ".join([_norm(s.shipment_number or s.number), _norm(s.tracking_number), _norm((s.notes or "").replace("\n", " "))[:80]]).strip(" |"),
                )
                for s in shipments
            ],
        )

        def count_q(model, clause):
            return int(db.session.execute(select(func.count()).select_from(model).where(clause)).scalar_one() or 0)

        _print_section("ملخص ارتباطات (لتفهم حجم الحذف)")
        if customer_ids:
            print("Customers:")
            print("  sales:", count_q(Sale, Sale.customer_id.in_(customer_ids)))
            print("  invoices:", count_q(Invoice, Invoice.customer_id.in_(customer_ids)))
            print("  service_requests:", count_q(ServiceRequest, ServiceRequest.customer_id.in_(customer_ids)))
            print("  payments:", count_q(Payment, Payment.customer_id.in_(customer_ids)))
            print("  expenses:", count_q(Expense, Expense.customer_id.in_(customer_ids)))
            print("  preorders:", count_q(PreOrder, PreOrder.customer_id.in_(customer_ids)))
            print("  online_carts:", count_q(OnlineCart, OnlineCart.customer_id.in_(customer_ids)))
            print("  online_preorders:", count_q(OnlinePreOrder, OnlinePreOrder.customer_id.in_(customer_ids)))
        if product_ids:
            print("Products:")
            print("  sale_lines:", count_q(SaleLine, SaleLine.product_id.in_(product_ids)))
            print("  invoice_lines:", count_q(InvoiceLine, InvoiceLine.product_id.in_(product_ids)))
            print("  service_parts:", count_q(ServicePart, ServicePart.part_id.in_(product_ids)))
            print("  stock_levels:", count_q(StockLevel, StockLevel.product_id.in_(product_ids)))
            print("  preorders:", count_q(PreOrder, PreOrder.product_id.in_(product_ids)))
            print("  online_cart_items:", count_q(OnlineCartItem, OnlineCartItem.product_id.in_(product_ids)))
            print("  online_preorder_items:", count_q(OnlinePreOrderItem, OnlinePreOrderItem.product_id.in_(product_ids)))
        if supplier_ids:
            print("Suppliers:")
            print("  invoices:", count_q(Invoice, Invoice.supplier_id.in_(supplier_ids)))
            print("  payments:", count_q(Payment, Payment.supplier_id.in_(supplier_ids)))
            print("  expenses:", count_q(Expense, Expense.supplier_id.in_(supplier_ids)))
            print("  preorders:", count_q(PreOrder, PreOrder.supplier_id.in_(supplier_ids)))
        if partner_ids:
            print("Partners:")
            print("  payments:", count_q(Payment, Payment.partner_id.in_(partner_ids)))
            print("  preorders:", count_q(PreOrder, PreOrder.partner_id.in_(partner_ids)))
            print("  service_parts:", count_q(ServicePart, ServicePart.partner_id.in_(partner_ids)))
            print("  service_tasks:", count_q(ServiceTask, ServiceTask.partner_id.in_(partner_ids)))

        if not (confirm_delete and require_phrase_ok):
            _print_section("تنبيه")
            print("لن يتم حذف أي شيء.")
            print("للحذف فعلياً: شغّل مع CONFIRM_DELETE=1 و CONFIRM_PHRASE=DELETE_TEST_DATA")
            return

        _print_section("بدء الحذف (مؤكد)")

        deleted = {}

        def exec_del(name: str, stmt) -> int:
            res = db.session.execute(stmt)
            deleted[name] = int(res.rowcount or 0)
            return deleted[name]

        def exec_upd(name: str, stmt) -> int:
            res = db.session.execute(stmt)
            deleted[name] = int(res.rowcount or 0)
            return deleted[name]

        sale_ids: list[int] = []
        invoice_ids: list[int] = []
        service_ids: list[int] = []
        expense_ids: list[int] = []
        preorder_ids: list[int] = []
        online_cart_ids: list[int] = []
        online_preorder_ids: list[int] = []
        payment_ids: list[int] = []
        exchange_ids: list[int] = []
        shipment_ids: list[int] = []

        if customer_ids:
            sale_ids = [int(x) for x in db.session.execute(select(Sale.id).where(Sale.customer_id.in_(customer_ids))).scalars().all()]
            invoice_ids = [int(x) for x in db.session.execute(select(Invoice.id).where(Invoice.customer_id.in_(customer_ids))).scalars().all()]
            service_ids = [int(x) for x in db.session.execute(select(ServiceRequest.id).where(ServiceRequest.customer_id.in_(customer_ids))).scalars().all()]
            expense_ids = [int(x) for x in db.session.execute(select(Expense.id).where(Expense.customer_id.in_(customer_ids))).scalars().all()]
            preorder_ids = [int(x) for x in db.session.execute(select(PreOrder.id).where(PreOrder.customer_id.in_(customer_ids))).scalars().all()]
            online_cart_ids = [int(x) for x in db.session.execute(select(OnlineCart.id).where(OnlineCart.customer_id.in_(customer_ids))).scalars().all()]
            online_preorder_ids = [int(x) for x in db.session.execute(select(OnlinePreOrder.id).where(OnlinePreOrder.customer_id.in_(customer_ids))).scalars().all()]

        if supplier_ids:
            invoice_ids = sorted(set(invoice_ids + [int(x) for x in db.session.execute(select(Invoice.id).where(Invoice.supplier_id.in_(supplier_ids))).scalars().all()]))
            expense_ids = sorted(set(expense_ids + [int(x) for x in db.session.execute(select(Expense.id).where(Expense.supplier_id.in_(supplier_ids))).scalars().all()]))
            preorder_ids = sorted(set(preorder_ids + [int(x) for x in db.session.execute(select(PreOrder.id).where(PreOrder.supplier_id.in_(supplier_ids))).scalars().all()]))
            product_ids = sorted(set(product_ids + [int(x) for x in db.session.execute(select(Product.id).where(Product.supplier_id.in_(supplier_ids))).scalars().all()]))

        if partner_ids:
            preorder_ids = sorted(set(preorder_ids + [int(x) for x in db.session.execute(select(PreOrder.id).where(PreOrder.partner_id.in_(partner_ids))).scalars().all()]))

        if product_ids:
            preorder_ids = sorted(set(preorder_ids + [int(x) for x in db.session.execute(select(PreOrder.id).where(PreOrder.product_id.in_(product_ids))).scalars().all()]))
            exchange_ids = [int(x) for x in db.session.execute(select(ExchangeTransaction.id).where(ExchangeTransaction.product_id.in_(product_ids))).scalars().all()]

        sale_ids = sorted(set(sale_ids + sale_token_ids))
        invoice_ids = sorted(set(invoice_ids + invoice_token_ids))
        service_ids = sorted(set(service_ids + service_token_ids))
        preorder_ids = sorted(set(preorder_ids + preorder_token_ids))
        online_preorder_ids = sorted(set(online_preorder_ids + online_preorder_token_ids))
        expense_ids = sorted(set(expense_ids + expense_token_ids))

        if sale_ids:
            shipment_ids = sorted(
                set(
                    shipment_ids
                    + [int(x) for x in db.session.execute(select(Shipment.id).where(Shipment.sale_id.in_(sale_ids))).scalars().all()]
                )
            )
        shipment_ids = sorted(set(shipment_ids + shipment_token_ids))

        sale_return_ids: list[int] = []
        if sale_ids:
            sale_return_ids = [int(x) for x in db.session.execute(select(SaleReturn.id).where(SaleReturn.sale_id.in_(sale_ids))).scalars().all()]

        tax_sale_ids = sale_ids[:]
        tax_service_ids = service_ids[:]

        if online_cart_ids:
            exec_del("online_cart_items", sa_delete(OnlineCartItem).where(OnlineCartItem.cart_id.in_(online_cart_ids)))
        if online_preorder_ids:
            exec_del("online_preorder_items", sa_delete(OnlinePreOrderItem).where(OnlinePreOrderItem.order_id.in_(online_preorder_ids)))
            exec_del("online_payments", sa_delete(OnlinePayment).where(OnlinePayment.order_id.in_(online_preorder_ids)))

        if sale_return_ids:
            exec_del("sale_return_lines", sa_delete(SaleReturnLine).where(SaleReturnLine.return_id.in_(sale_return_ids)))
            exec_del("sale_returns", sa_delete(SaleReturn).where(SaleReturn.id.in_(sale_return_ids)))

        if sale_ids:
            exec_del("sale_lines_by_sale", sa_delete(SaleLine).where(SaleLine.sale_id.in_(sale_ids)))
        if invoice_ids:
            exec_del("invoice_lines_by_invoice", sa_delete(InvoiceLine).where(InvoiceLine.invoice_id.in_(invoice_ids)))

        if service_ids:
            exec_del("service_parts_by_service", sa_delete(ServicePart).where(ServicePart.service_id.in_(service_ids)))
            exec_del("service_tasks_by_service", sa_delete(ServiceTask).where(ServiceTask.service_id.in_(service_ids)))

        if shipment_ids:
            exec_del("shipment_items_by_shipment", sa_delete(ShipmentItem).where(ShipmentItem.shipment_id.in_(shipment_ids)))
            exec_del("shipment_partners_by_shipment", sa_delete(ShipmentPartner).where(ShipmentPartner.shipment_id.in_(shipment_ids)))

        if product_ids:
            exec_del("sale_lines_by_product", sa_delete(SaleLine).where(SaleLine.product_id.in_(product_ids)))
            exec_del("invoice_lines_by_product", sa_delete(InvoiceLine).where(InvoiceLine.product_id.in_(product_ids)))
            exec_del("service_parts_by_product", sa_delete(ServicePart).where(ServicePart.part_id.in_(product_ids)))
            exec_del("stock_levels", sa_delete(StockLevel).where(StockLevel.product_id.in_(product_ids)))
            exec_del("warehouse_partner_shares_by_product", sa_delete(WarehousePartnerShare).where(WarehousePartnerShare.product_id.in_(product_ids)))
            exec_del("supplier_settlement_lines_by_product", sa_delete(SupplierSettlementLine).where(SupplierSettlementLine.product_id.in_(product_ids)))
            exec_del("partner_settlement_lines_by_product", sa_delete(PartnerSettlementLine).where(PartnerSettlementLine.product_id.in_(product_ids)))
            exec_del("shipment_items_by_product", sa_delete(ShipmentItem).where(ShipmentItem.product_id.in_(product_ids)))
            exec_del("stock_adjustment_items_by_product", sa_delete(StockAdjustmentItem).where(StockAdjustmentItem.product_id.in_(product_ids)))
            exec_del("transfers_by_product", sa_delete(Transfer).where(Transfer.product_id.in_(product_ids)))
            if exchange_ids:
                exec_del("exchange_transactions", sa_delete(ExchangeTransaction).where(ExchangeTransaction.id.in_(exchange_ids)))
            exec_del("product_supplier_loans_by_product", sa_delete(ProductSupplierLoan).where(ProductSupplierLoan.product_id.in_(product_ids)))
            exec_del("product_ratings_by_product", sa_delete(ProductRating).where(ProductRating.product_id.in_(product_ids)))
            exec_del("project_resources_by_product", sa_delete(ProjectResource).where(ProjectResource.product_id.in_(product_ids)))
            exec_del("preorders_by_product", sa_delete(PreOrder).where(PreOrder.product_id.in_(product_ids)))
            exec_del("online_cart_items_by_product", sa_delete(OnlineCartItem).where(OnlineCartItem.product_id.in_(product_ids)))
            exec_del("online_preorder_items_by_product", sa_delete(OnlinePreOrderItem).where(OnlinePreOrderItem.product_id.in_(product_ids)))

        if preorder_ids:
            payment_ids = sorted(set(payment_ids + [int(x) for x in db.session.execute(select(Payment.id).where(Payment.preorder_id.in_(preorder_ids))).scalars().all()]))
        if preorder_ids:
            exec_del("payments_preorder", sa_delete(Payment).where(Payment.preorder_id.in_(preorder_ids)))
        if sale_ids:
            payment_ids = sorted(set(payment_ids + [int(x) for x in db.session.execute(select(Payment.id).where(Payment.sale_id.in_(sale_ids))).scalars().all()]))
            exec_del("payments_sale", sa_delete(Payment).where(Payment.sale_id.in_(sale_ids)))
        if invoice_ids:
            payment_ids = sorted(set(payment_ids + [int(x) for x in db.session.execute(select(Payment.id).where(Payment.invoice_id.in_(invoice_ids))).scalars().all()]))
            exec_del("payments_invoice", sa_delete(Payment).where(Payment.invoice_id.in_(invoice_ids)))
        if service_ids:
            payment_ids = sorted(set(payment_ids + [int(x) for x in db.session.execute(select(Payment.id).where(Payment.service_id.in_(service_ids))).scalars().all()]))
            exec_del("payments_service", sa_delete(Payment).where(Payment.service_id.in_(service_ids)))
        if expense_ids:
            payment_ids = sorted(set(payment_ids + [int(x) for x in db.session.execute(select(Payment.id).where(Payment.expense_id.in_(expense_ids))).scalars().all()]))
            exec_del("payments_expense", sa_delete(Payment).where(Payment.expense_id.in_(expense_ids)))
        if customer_ids:
            payment_ids = sorted(set(payment_ids + [int(x) for x in db.session.execute(select(Payment.id).where(Payment.customer_id.in_(customer_ids))).scalars().all()]))
            exec_del("payments_customer", sa_delete(Payment).where(Payment.customer_id.in_(customer_ids)))
        if supplier_ids:
            payment_ids = sorted(set(payment_ids + [int(x) for x in db.session.execute(select(Payment.id).where(Payment.supplier_id.in_(supplier_ids))).scalars().all()]))
            exec_del("payments_supplier", sa_delete(Payment).where(Payment.supplier_id.in_(supplier_ids)))
        if partner_ids:
            payment_ids = sorted(set(payment_ids + [int(x) for x in db.session.execute(select(Payment.id).where(Payment.partner_id.in_(partner_ids))).scalars().all()]))
            exec_del("payments_partner", sa_delete(Payment).where(Payment.partner_id.in_(partner_ids)))
        if shipment_ids:
            payment_ids = sorted(set(payment_ids + [int(x) for x in db.session.execute(select(Payment.id).where(Payment.shipment_id.in_(shipment_ids))).scalars().all()]))
            exec_del("payments_shipment", sa_delete(Payment).where(Payment.shipment_id.in_(shipment_ids)))

        if payment_token_ids:
            payment_ids = sorted(set(payment_ids + payment_token_ids))
            exec_del("payments_by_token", sa_delete(Payment).where(Payment.id.in_(payment_token_ids)))

        if tax_sale_ids:
            exec_del("tax_entries_sales", sa_delete(TaxEntry).where(TaxEntry.transaction_type == "SALE", TaxEntry.transaction_id.in_(tax_sale_ids)))
        if tax_service_ids:
            exec_del("tax_entries_services", sa_delete(TaxEntry).where(TaxEntry.transaction_type == "SERVICE", TaxEntry.transaction_id.in_(tax_service_ids)))
        if payment_ids:
            exec_del("tax_entries_payments", sa_delete(TaxEntry).where(TaxEntry.transaction_type == "PAYMENT", TaxEntry.transaction_id.in_(payment_ids)))
        if customer_ids:
            exec_del("tax_entries_customers", sa_delete(TaxEntry).where(TaxEntry.customer_id.in_(customer_ids)))
        if supplier_ids:
            exec_del("tax_entries_suppliers", sa_delete(TaxEntry).where(TaxEntry.supplier_id.in_(supplier_ids)))

        if payment_ids:
            exec_upd("checks_null_payment_id", sa_update(Check).where(Check.payment_id.in_(payment_ids)).values(payment_id=None))
        if customer_ids:
            exec_del("checks_customer", sa_delete(Check).where(Check.customer_id.in_(customer_ids)))
        if supplier_ids:
            exec_del("checks_supplier", sa_delete(Check).where(Check.supplier_id.in_(supplier_ids)))
        if partner_ids:
            exec_del("checks_partner", sa_delete(Check).where(Check.partner_id.in_(partner_ids)))

        def del_gl_for(source_type: str, ids: list[int]) -> None:
            if not ids:
                return
            for chunk in _chunked_ids(ids, 1000):
                exec_del(f"gl_batches_{source_type.lower()}", sa_delete(GLBatch).where(GLBatch.source_type == source_type, GLBatch.source_id.in_(chunk)))

        del_gl_for("PAYMENT", payment_ids)
        del_gl_for("SALE", sale_ids)
        del_gl_for("INVOICE", invoice_ids)
        del_gl_for("SERVICE", service_ids)
        del_gl_for("EXPENSE", expense_ids)
        del_gl_for("PREORDER", preorder_ids)
        del_gl_for("ONLINE_PREORDER", online_preorder_ids)
        del_gl_for("EXCHANGE", exchange_ids)
        del_gl_for("SHIPMENT", shipment_ids)

        if online_preorder_ids:
            exec_del("online_preorders", sa_delete(OnlinePreOrder).where(OnlinePreOrder.id.in_(online_preorder_ids)))
        if online_cart_ids:
            exec_del("online_carts", sa_delete(OnlineCart).where(OnlineCart.id.in_(online_cart_ids)))

        if invoice_ids:
            exec_del("invoices", sa_delete(Invoice).where(Invoice.id.in_(invoice_ids)))
        if shipment_ids:
            exec_del("shipments", sa_delete(Shipment).where(Shipment.id.in_(shipment_ids)))
        if sale_ids:
            exec_del("sales", sa_delete(Sale).where(Sale.id.in_(sale_ids)))
        if preorder_ids:
            exec_del("preorders", sa_delete(PreOrder).where(PreOrder.id.in_(preorder_ids)))
        if service_ids:
            exec_del("service_requests", sa_delete(ServiceRequest).where(ServiceRequest.id.in_(service_ids)))
        if expense_ids:
            exec_del("expenses", sa_delete(Expense).where(Expense.id.in_(expense_ids)))

        if product_ids:
            exec_del("product_partner_links", sa_delete(ProductPartner).where(ProductPartner.product_id.in_(product_ids)))
            exec_del("product_partner_shares", sa_delete(ProductPartnerShare).where(ProductPartnerShare.product_id.in_(product_ids)))
            exec_del("products", sa_delete(Product).where(Product.id.in_(product_ids)))
        if customer_ids:
            exec_upd("supplier_customer_links_null", sa_update(Supplier).where(Supplier.customer_id.in_(customer_ids)).values(customer_id=None))
            exec_upd("partner_customer_links_null", sa_update(Partner).where(Partner.customer_id.in_(customer_ids)).values(customer_id=None))
            exec_del("customers", sa_delete(Customer).where(Customer.id.in_(customer_ids)))

        if supplier_ids:
            supplier_blockers = int(
                db.session.execute(
                    select(func.count()).select_from(Product).where(Product.supplier_id.in_(supplier_ids))
                ).scalar_one()
                or 0
            )
            supplier_wh_blockers = int(
                db.session.execute(
                    select(func.count()).select_from(Warehouse).where(Warehouse.supplier_id.in_(supplier_ids))
                ).scalar_one()
                or 0
            )
            if supplier_blockers == 0 and supplier_wh_blockers == 0:
                exec_del("suppliers", sa_delete(Supplier).where(Supplier.id.in_(supplier_ids)))
            else:
                print("")
                print(f"تخطّي حذف suppliers بسبب علاقات متبقية: products={supplier_blockers} warehouses={supplier_wh_blockers}")

        if partner_ids:
            partner_wh_blockers = int(
                db.session.execute(
                    select(func.count()).select_from(Warehouse).where(Warehouse.partner_id.in_(partner_ids))
                ).scalar_one()
                or 0
            )
            partner_share_blockers = int(
                db.session.execute(
                    select(func.count()).select_from(WarehousePartnerShare).where(WarehousePartnerShare.partner_id.in_(partner_ids))
                ).scalar_one()
                or 0
            )
            if partner_wh_blockers == 0 and partner_share_blockers == 0:
                exec_del("partners", sa_delete(Partner).where(Partner.id.in_(partner_ids)))
            else:
                print("")
                print(f"تخطّي حذف partners بسبب علاقات متبقية: warehouses={partner_wh_blockers} shares={partner_share_blockers}")

        db.session.commit()

        _print_section("نتائج الحذف")
        for k in sorted(deleted.keys()):
            print(f"- {k}: {deleted[k]}")


if __name__ == "__main__":
    run()
