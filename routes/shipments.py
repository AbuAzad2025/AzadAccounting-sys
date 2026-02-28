
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from extensions import db
from datetime import datetime, timezone
from models import (
    Shipment, ShipmentItem, ShipmentPartner,
    Partner, Product, Warehouse, _queue_partner_balance,
    GLBatch, GLEntry, GL_ACCOUNTS
)
import utils

shipments_bp = Blueprint("shipments_bp", __name__, url_prefix="/shipments")

def _compute_totals(sh):
    total = 0
    for item in sh.items:
        cost = (item.unit_cost or 0) * (item.quantity or 0)
        total += cost
    # Add extra costs if any (freight, customs, etc)
    total += (sh.shipping_cost or 0)
    total += (sh.customs or 0)
    total += (sh.vat or 0)
    total += (sh.insurance or 0)
    return total

def _create_shipment_gl_entries(sh: Shipment):
    """
    إنشاء قيود محاسبية للشحنة المستلمة (ARRIVED)
    """
    # 1. التحقق من عدم وجود قيد سابق
    existing_batch = GLBatch.query.filter_by(
        source_type='SHIPMENT',
        source_id=sh.id,
        status='POSTED'
    ).filter(GLBatch.purpose == None).first()
    
    if existing_batch:
        return # تم الإنشاء سابقاً

    # 2. إعداد الحسابات
    inventory_acc = GL_ACCOUNTS.get('INVENTORY', '1200_INVENTORY')
    ap_acc = GL_ACCOUNTS.get('AP', '2000_AP')
    partner_equity_acc = GL_ACCOUNTS.get('PARTNER_EQUITY', '3200_PARTNER_EQUITY')

    # 3. القيم
    total_cost = _compute_totals(sh)
    total_val = float(total_cost)
    
    if total_val <= 0:
        return

    batch = GLBatch(
        posted_at=sh.actual_arrival or sh.shipment_date or datetime.now(timezone.utc),
        source_type='SHIPMENT',
        source_id=sh.id,
        memo=f"استلام شحنة #{sh.shipment_number or sh.id}",
        currency=sh.currency,
        status='POSTED',
        entity_type='SUPPLIER', # مبدئياً
        entity_id=None # لا يوجد مورد محدد
    )
    db.session.add(batch)
    db.session.flush()

    # 4. الطرف المدين: المخزون
    debit_entry = GLEntry(
        batch_id=batch.id,
        account=inventory_acc,
        debit=total_val,
        credit=0,
        currency=sh.currency,
        ref=f"SH-{sh.id}"
    )
    db.session.add(debit_entry)

    # 5. الطرف الدائن: شركاء أو موردين
    if sh.partners:
        # توزيع على الشركاء
        total_partners_share = 0
        for sp in sh.partners:
            share_amt = float(sp.share_amount or 0)
            if share_amt > 0:
                credit_entry = GLEntry(
                    batch_id=batch.id,
                    account=partner_equity_acc,
                    debit=0,
                    credit=share_amt,
                    currency=sh.currency,
                    ref=f"PTR-{sp.partner_id}"
                )
                db.session.add(credit_entry)
                total_partners_share += share_amt
        
        # الفارق (إن وجد) يذهب للموردين
        remaining = total_val - total_partners_share
        if abs(remaining) > 0.01:
             credit_entry = GLEntry(
                batch_id=batch.id,
                account=ap_acc,
                debit=0,
                credit=remaining,
                currency=sh.currency,
                ref="SUPPLIER"
            )
             db.session.add(credit_entry)
    else:
        # كله للموردين
        credit_entry = GLEntry(
            batch_id=batch.id,
            account=ap_acc,
            debit=0,
            credit=total_val,
            currency=sh.currency,
            ref="SUPPLIER"
        )
        db.session.add(credit_entry)

    db.session.flush()

def _create_shipment_return_gl_entries(sh: Shipment):
    """
    إنشاء قيود عكسية عند إرجاع الشحنة (RETURNED)
    Debit: AP / Partner
    Credit: Inventory
    """
    # 1. Check for existing return batch
    existing_batch = GLBatch.query.filter_by(
        source_type='SHIPMENT',
        source_id=sh.id,
        purpose='RETURN',
        status='POSTED'
    ).first()
    if existing_batch:
        return

    # 2. Accounts
    inventory_acc = GL_ACCOUNTS.get('INVENTORY', '1200_INVENTORY')
    ap_acc = GL_ACCOUNTS.get('AP', '2000_AP')
    partner_equity_acc = GL_ACCOUNTS.get('PARTNER_EQUITY', '3200_PARTNER_EQUITY')

    # 3. Values
    total_cost = _compute_totals(sh)
    total_val = float(total_cost)
    
    if total_val <= 0:
        return

    batch = GLBatch(
        posted_at=datetime.now(timezone.utc),
        source_type='SHIPMENT',
        source_id=sh.id,
        purpose='RETURN',
        memo=f"إرجاع شحنة #{sh.shipment_number or sh.id}",
        currency=sh.currency,
        status='POSTED',
        entity_type='SUPPLIER',
        entity_id=None
    )
    db.session.add(batch)
    db.session.flush()

    # 4. Credit Inventory (Decrease Asset)
    credit_entry = GLEntry(
        batch_id=batch.id,
        account=inventory_acc,
        debit=0,
        credit=total_val,
        currency=sh.currency,
        ref=f"SH-{sh.id}"
    )
    db.session.add(credit_entry)

    # 5. Debit AP/Partner (Decrease Liability)
    if sh.partners:
        total_partners_share = 0
        for sp in sh.partners:
            share_amt = float(sp.share_amount or 0)
            if share_amt > 0:
                debit_entry = GLEntry(
                    batch_id=batch.id,
                    account=partner_equity_acc,
                    debit=share_amt,
                    credit=0,
                    currency=sh.currency,
                    ref=f"PTR-{sp.partner_id}"
                )
                db.session.add(debit_entry)
                total_partners_share += share_amt
        
        remaining = total_val - total_partners_share
        if abs(remaining) > 0.01:
             debit_entry = GLEntry(
                batch_id=batch.id,
                account=ap_acc,
                debit=remaining,
                credit=0,
                currency=sh.currency,
                ref="SUPPLIER"
            )
             db.session.add(debit_entry)
    else:
        debit_entry = GLEntry(
            batch_id=batch.id,
            account=ap_acc,
            debit=total_val,
            credit=0,
            currency=sh.currency,
            ref="SUPPLIER"
        )
        db.session.add(debit_entry)

    db.session.flush()

@shipments_bp.app_context_processor
def _inject_utils():
    return dict(format_currency=utils.format_currency)

from utils import D as _D, _q2

def _norm_currency(v):
    return (v or "USD").strip().upper()

def _items_snapshot(sh):
    return [
        {"product_id": it.product_id, "warehouse_id": it.warehouse_id, "quantity": it.quantity}
        for it in sh.items
    ]

def _snapshot_key(items):
    return tuple(sorted((it["product_id"], it["warehouse_id"], float(it["quantity"])) for it in items))

def _status_applies_stock(st):
    return (st or "").upper() in ("ARRIVED", "RECEIVED")

def _apply_arrival_items(items):
    for it in items:
        pid = it["product_id"]
        wid = it["warehouse_id"]
        qty = float(it["quantity"])
        if qty > 0:
            utils.stock_update(pid, wid, qty, reason="Shipment Arrived")

def _reverse_arrival_items(items):
    for it in items:
        pid = it["product_id"]
        wid = it["warehouse_id"]
        qty = float(it["quantity"])
        if qty > 0:
            utils.stock_update(pid, wid, -qty, reason="Shipment Returned")

def _ensure_partner_warehouse(wh_id, shipment):
    if not wh_id: return
    if not shipment.partners: return
    
    # ... (Keep existing logic)
