"""أوامر الشراء — دورة AP خفيفة مكمّلة للشحنات."""
from datetime import date, datetime

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import login_required
from decimal import Decimal

from extensions import db
from models import PurchaseOrder, PurchaseOrderLine, Supplier, Branch, Product
from permissions_config.enums import SystemPermissions
from utils import permission_required
from utils.company_scope import filter_by_branches, default_company

purchases_bp = Blueprint("purchases_bp", __name__, url_prefix="/purchases")


def _next_po_number():
    n = PurchaseOrder.query.count() + 1
    return f"PO-{datetime.now().year}-{n:05d}"


@purchases_bp.route("/")
@login_required
@permission_required(SystemPermissions.MANAGE_SHIPMENTS)
def index():
    q = PurchaseOrder.query.order_by(PurchaseOrder.order_date.desc())
    q = filter_by_branches(q, PurchaseOrder.branch_id)
    status = request.args.get("status", "")
    if status:
        q = q.filter(PurchaseOrder.status == status.upper())
    orders = q.limit(200).all()
    return render_template("purchases/index.html", orders=orders, status=status)


@purchases_bp.route("/add", methods=["GET", "POST"])
@login_required
@permission_required(SystemPermissions.MANAGE_SHIPMENTS)
def add():
    suppliers = Supplier.query.filter(Supplier.is_archived == False).order_by(Supplier.name).all()  # noqa: E712
    branches = Branch.query.filter_by(is_active=True).order_by(Branch.name).all()
    products = Product.query.filter_by(is_active=True).order_by(Product.name).limit(500).all()

    if request.method == "POST":
        try:
            supplier_id = request.form.get("supplier_id", type=int)
            branch_id = request.form.get("branch_id", type=int)
            if not supplier_id or not branch_id:
                raise ValueError("المورد والفرع مطلوبان")
            raw_date = request.form.get("order_date")
            if raw_date:
                try:
                    order_date = date.fromisoformat(str(raw_date)[:10])
                except ValueError:
                    order_date = date.today()
            else:
                order_date = date.today()
            po = PurchaseOrder(
                number=_next_po_number(),
                supplier_id=supplier_id,
                branch_id=branch_id,
                order_date=order_date,
                expected_date=request.form.get("expected_date") or None,
                status="ORDERED",
                currency=request.form.get("currency") or "ILS",
                notes=request.form.get("notes"),
            )
            db.session.add(po)
            db.session.flush()
            total = Decimal("0")
            pids = request.form.getlist("product_id")
            qtys = request.form.getlist("quantity")
            prices = request.form.getlist("unit_price")
            for i, pid in enumerate(pids):
                if not pid:
                    continue
                qty = Decimal(str(qtys[i] if i < len(qtys) else 1))
                price = Decimal(str(prices[i] if i < len(prices) else 0))
                if qty <= 0:
                    continue
                db.session.add(
                    PurchaseOrderLine(
                        purchase_order_id=po.id,
                        product_id=int(pid),
                        quantity=qty,
                        unit_price=price,
                    )
                )
                total += qty * price
            po.total_amount = total
            db.session.commit()
            flash(f"تم إنشاء أمر الشراء {po.number}", "success")
            return redirect(url_for("purchases_bp.detail", id=po.id))
        except Exception as e:
            db.session.rollback()
            flash(str(e), "danger")
    return render_template(
        "purchases/form.html",
        suppliers=suppliers,
        branches=branches,
        products=products,
        order=None,
    )


@purchases_bp.route("/<int:id>")
@login_required
@permission_required(SystemPermissions.MANAGE_SHIPMENTS)
def detail(id):
    order = db.session.get(PurchaseOrder, id) or abort(404)
    return render_template("purchases/detail.html", order=order)


@purchases_bp.route("/<int:id>/status", methods=["POST"])
@login_required
@permission_required(SystemPermissions.MANAGE_SHIPMENTS)
def set_status(id):
    from flask import abort
    order = db.session.get(PurchaseOrder, id) or abort(404)
    st = (request.form.get("status") or "").upper()
    if st in ("DRAFT", "ORDERED", "PARTIAL", "RECEIVED", "CANCELLED"):
        order.status = st
        db.session.commit()
        flash("تم تحديث الحالة", "success")
    return redirect(url_for("purchases_bp.detail", id=id))
