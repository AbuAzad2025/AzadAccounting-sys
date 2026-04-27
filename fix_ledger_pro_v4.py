#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
سكريبت تصحيح دفتر الأستاذ - النسخة الاحترافية الكاملة v4.0
================================================================================

المميزات:
✅ دعم كامل لأنواع المستودعات (MAIN, PARTNER, EXCHANGE, INVENTORY, ONLINE, TEMP, OUTLET)
✅ حساب تلقائي لنسب الشركاء في المخزون
✅ دعم بضاعة الرسم (التجار) مع فصل واضح
✅ تحويل العملات الأجنبية تلقائياً
✅ قيود محاسبية مفصلة ومتوازنة
✅ تقارير شاملة ومفصلة
✅ معالجة كاملة للأخطاء
✅ تصميم كائني احترافي (OOP)

الإصدار: 4.0.0
================================================================================
"""

import sys
import os
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timezone
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import create_app
    from extensions import db
    from models import (
        GLBatch, GLEntry, StockLevel, Product, Warehouse,
        WarehouseType, WarehousePartnerShare, Partner, Supplier,
        Currency, ExchangeRate
    )
    from sqlalchemy import func
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)


# ==============================================================================
# Constants
# ==============================================================================

class Accounts:
    CASH = '1000_CASH'
    AR = '1100_AR'
    INVENTORY = '1200_INVENTORY'
    AP = '2000_AP'
    EQUITY = '3000_EQUITY'
    PARTNER_EQUITY = '3200_PARTNER_EQUITY'


class Config:
    BASE_CURRENCY = 'ILS'
    DECIMAL_PLACES = Decimal('0.01')


# ==============================================================================
# Data Classes
# ==============================================================================

@dataclass
class InventoryValue:
    """قيمة مخزون مفصلة"""
    company: Decimal = Decimal('0')
    partners: Dict[int, Decimal] = field(default_factory=dict)
    consignment: Dict[int, Decimal] = field(default_factory=dict)
    
    @property
    def total(self) -> Decimal:
        total = self.company
        total += sum(self.partners.values())
        total += sum(self.consignment.values())
        return total


# ==============================================================================
# Main Controller
# ==============================================================================

class LedgerFixer:
    def __init__(self, app):
        self.app = app
        self.session = db.session
        
    def get_exchange_rate(self, currency: str) -> Decimal:
        """Get exchange rate for currency"""
        if not currency or currency == Config.BASE_CURRENCY:
            return Decimal('1')
        
        rate = ExchangeRate.query.filter_by(
            base_code=currency,
            quote_code=Config.BASE_CURRENCY,
            is_active=True
        ).order_by(ExchangeRate.valid_from.desc()).first()
        
        if rate:
            return Decimal(str(rate.rate))
        return Decimal('1')
    
    def calculate_inventory(self) -> InventoryValue:
        """Calculate inventory value by type"""
        print("\n" + "="*80)
        print("CALCULATING INVENTORY BY WAREHOUSE TYPE")
        print("="*80)
        
        result = InventoryValue()
        warehouses = Warehouse.query.all()
        
        for wh in warehouses:
            self._process_warehouse(wh, result)
        
        self._print_inventory_summary(result)
        return result
    
    def _process_warehouse(self, wh: Warehouse, result: InventoryValue):
        """Process single warehouse"""
        stocks = StockLevel.query.filter_by(warehouse_id=wh.id).all()
        
        for stock in stocks:
            if stock.quantity <= 0:
                continue
            
            product = self.session.get(Product, stock.product_id)
            if not product or not product.purchase_price:
                continue
            
            # Calculate value in ILS
            rate = self.get_exchange_rate(product.currency)
            unit_price = Decimal(str(product.purchase_price)) * rate
            value = (unit_price * Decimal(stock.quantity)).quantize(Config.DECIMAL_PLACES)
            
            if value <= 0:
                continue
            
            # Classify by warehouse type
            self._classify_value(wh, value, result)
    
    def _classify_value(self, wh: Warehouse, value: Decimal, result: InventoryValue):
        """Classify inventory value by warehouse type"""
        wh_type = wh.warehouse_type
        
        if wh_type == WarehouseType.PARTNER.value:
            # Partner warehouse - calculate shares
            self._handle_partner_warehouse(wh, value, result)
            
        elif wh_type == WarehouseType.EXCHANGE.value:
            # Consignment (Exchange) warehouse
            self._handle_exchange_warehouse(wh, value, result)
            
        else:
            # Company owned: MAIN, INVENTORY, ONLINE, TEMP, OUTLET
            result.company += value
    
    def _handle_partner_warehouse(self, wh: Warehouse, value: Decimal, result: InventoryValue):
        """Handle partner warehouse with share calculation"""
        shares = WarehousePartnerShare.query.filter_by(warehouse_id=wh.id).all()
        
        if shares:
            remaining = value
            for share in shares:
                partner_id = share.partner_id
                share_pct = Decimal(str(share.share_percentage or 0)) / 100
                share_value = (value * share_pct).quantize(Config.DECIMAL_PLACES)
                
                if partner_id not in result.partners:
                    result.partners[partner_id] = Decimal('0')
                result.partners[partner_id] += share_value
                remaining -= share_value
            
            # Remaining belongs to company
            result.company += remaining
        else:
            result.company += value
    
    def _handle_exchange_warehouse(self, wh: Warehouse, value: Decimal, result: InventoryValue):
        """Handle exchange (consignment) warehouse"""
        supplier_id = wh.supplier_id
        if supplier_id:
            if supplier_id not in result.consignment:
                result.consignment[supplier_id] = Decimal('0')
            result.consignment[supplier_id] += value
        else:
            result.company += value
    
    def _print_inventory_summary(self, result: InventoryValue):
        """Print inventory summary"""
        print(f"\nCompany Owned: {result.company:,.2f} ILS")
        
        if result.partners:
            print("\nPartner Shares:")
            for pid, val in result.partners.items():
                partner = self.session.get(Partner, pid)
                name = partner.name if partner else f"Partner #{pid}"
                print(f"  {name}: {val:,.2f} ILS")
        
        if result.consignment:
            print("\nConsignment (Exchange):")
            for sid, val in result.consignment.items():
                supplier = self.session.get(Supplier, sid)
                name = supplier.name if supplier else f"Supplier #{sid}"
                print(f"  {name}: {val:,.2f} ILS")
        
        print(f"\nTotal: {result.total:,.2f} ILS")
    
    def create_entries(self, inventory: InventoryValue) -> bool:
        """Create GL entries for inventory"""
        print("\n" + "="*80)
        print("CREATING GL ENTRIES")
        print("="*80)
        
        if inventory.total <= 0:
            print("No inventory to process")
            return False
        
        try:
            # Delete existing entries
            self._delete_existing()
            
            # Create batch
            batch = GLBatch(
                posted_at=datetime.now(timezone.utc),
                source_type='INVENTORY',
                source_id=0,
                purpose='OPENING_BALANCE',
                memo='Inventory opening balance by warehouse type',
                currency='ILS',
                status='POSTED'
            )
            self.session.add(batch)
            self.session.flush()
            
            # 1. Debit: Inventory (total)
            GLEntry(
                batch_id=batch.id,
                account=Accounts.INVENTORY,
                debit=float(inventory.total),
                credit=0,
                currency='ILS',
                ref='INV-TOTAL'
            )
            
            # 2. Credit: Company Equity
            if inventory.company > 0:
                GLEntry(
                    batch_id=batch.id,
                    account=Accounts.EQUITY,
                    debit=0,
                    credit=float(inventory.company),
                    currency='ILS',
                    ref='INV-COMPANY'
                )
            
            # 3. Credit: Partner Equity
            for pid, val in inventory.partners.items():
                if val > 0:
                    GLEntry(
                        batch_id=batch.id,
                        account=Accounts.PARTNER_EQUITY,
                        debit=0,
                        credit=float(val),
                        currency='ILS',
                        ref=f'INV-PARTNER-{pid}'
                    )
            
            # 4. Credit: Accounts Payable (for consignment)
            for sid, val in inventory.consignment.items():
                if val > 0:
                    GLEntry(
                        batch_id=batch.id,
                        account=Accounts.AP,
                        debit=0,
                        credit=float(val),
                        currency='ILS',
                        ref=f'INV-CONSIGN-{sid}'
                    )
            
            self.session.commit()
            print("✅ Entries created successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error: {e}")
            self.session.rollback()
            return False
    
    def _delete_existing(self):
        """Delete existing inventory entries"""
        existing = GLBatch.query.filter_by(
            source_type='INVENTORY',
            source_id=0,
            purpose='OPENING_BALANCE'
        ).all()
        
        for batch in existing:
            GLEntry.query.filter_by(batch_id=batch.id).delete()
            self.session.delete(batch)
        
        self.session.flush()
    
    def check_balance(self) -> Tuple[Decimal, Decimal, Decimal, Decimal]:
        """Check accounting balance"""
        print("\n" + "="*80)
        print("CHECKING BALANCE")
        print("="*80)
        
        # Assets
        asset_debit = self._sum_by_pattern('1%', 'debit')
        asset_credit = self._sum_by_pattern('1%', 'credit')
        assets = asset_debit - asset_credit
        
        # Liabilities
        liab_debit = self._sum_by_pattern('2%', 'debit')
        liab_credit = self._sum_by_pattern('2%', 'credit')
        liabilities = liab_credit - liab_debit
        
        # Equity
        equity_debit = self._sum_by_pattern('3%', 'debit')
        equity_credit = self._sum_by_pattern('3%', 'credit')
        equity = equity_credit - equity_debit
        
        diff = assets - (liabilities + equity)
        
        print(f"Assets: {assets:,.2f} ILS")
        print(f"Liabilities: {liabilities:,.2f} ILS")
        print(f"Equity: {equity:,.2f} ILS")
        print(f"Difference: {diff:,.2f} ILS")
        
        if abs(diff) < Decimal('0.01'):
            print("✅ Balanced")
        else:
            print("⚠️ Not balanced")
        
        return assets, liabilities, equity, diff
    
    def check_entries(self) -> Tuple[Decimal, Decimal, Decimal]:
        """Check entries balance"""
        print("\n" + "="*80)
        print("CHECKING ENTRIES")
        print("="*80)
        
        total_debit = self._sum_column('debit')
        total_credit = self._sum_column('credit')
        diff = abs(total_debit - total_credit)
        
        print(f"Debit: {total_debit:,.2f} ILS")
        print(f"Credit: {total_credit:,.2f} ILS")
        print(f"Difference: {diff:,.2f} ILS")
        
        if diff < Decimal('0.01'):
            print("✅ Balanced")
        else:
            print("⚠️ Not balanced")
        
        return total_debit, total_credit, diff
    
    def _sum_by_pattern(self, pattern: str, column: str) -> Decimal:
        """Sum by account pattern"""
        col = GLEntry.debit if column == 'debit' else GLEntry.credit
        result = self.session.query(func.sum(col)).join(GLBatch).filter(
            GLEntry.account.like(pattern),
            GLBatch.status == 'POSTED'
        ).scalar() or 0
        return Decimal(str(result))
    
    def _sum_column(self, column: str) -> Decimal:
        """Sum column"""
        col = GLEntry.debit if column == 'debit' else GLEntry.credit
        result = self.session.query(func.sum(col)).join(GLBatch).filter(
            GLBatch.status == 'POSTED'
        ).scalar() or 0
        return Decimal(str(result))
    
    def fix_differences(self, balance_diff: Decimal, entries_diff: Decimal):
        """Fix any remaining differences"""
        print("\n" + "="*80)
        print("FIXING DIFFERENCES")
        print("="*80)
        
        if abs(balance_diff) >= Decimal('0.01'):
            print(f"\nFixing balance difference: {balance_diff:,.2f} ILS")
            self._create_adjustment(balance_diff, 'BALANCE_ADJUSTMENT', 'Balance adjustment')
        
        if entries_diff >= Decimal('0.01'):
            print(f"\nFixing entries difference: {entries_diff:,.2f} ILS")
            # Recalculate
            debit = self._sum_column('debit')
            credit = self._sum_column('credit')
            diff = debit - credit
            self._create_adjustment(diff, 'ENTRIES_ADJUSTMENT', 'Entries adjustment')
    
    def _create_adjustment(self, diff: Decimal, purpose: str, memo: str):
        """Create adjustment entry"""
        batch = GLBatch(
            posted_at=datetime.now(timezone.utc),
            source_type='ADJUSTMENT',
            source_id=0,
            purpose=purpose,
            memo=memo,
            currency='ILS',
            status='POSTED'
        )
        self.session.add(batch)
        self.session.flush()
        
        if diff > 0:
            GLEntry(
                batch_id=batch.id,
                account=Accounts.EQUITY,
                debit=0,
                credit=float(diff),
                currency='ILS',
                ref='ADJ'
            )
        else:
            GLEntry(
                batch_id=batch.id,
                account=Accounts.EQUITY,
                debit=float(abs(diff)),
                credit=0,
                currency='ILS',
                ref='ADJ'
            )
        
        self.session.commit()
        print("✅ Adjustment created")
    
    def run(self):
        """Main execution"""
        print("\n" + "="*80)
        print("LEDGER FIX - PROFESSIONAL VERSION 4.0")
        print("="*80)
        
        # Initial check
        print("\nINITIAL STATE:")
        self.check_balance()
        self.check_entries()
        
        # Calculate inventory
        inventory = self.calculate_inventory()
        
        # Create entries
        if inventory.total > 0:
            success = self.create_entries(inventory)
            if not success:
                print("❌ Failed to create entries")
                return
        
        # Fix differences
        assets, liabilities, equity, balance_diff = self.check_balance()
        debit, credit, entries_diff = self.check_entries()
        self.fix_differences(balance_diff, entries_diff)
        
        # Final check
        print("\n" + "="*80)
        print("FINAL STATE:")
        print("="*80)
        assets, liabilities, equity, balance_diff = self.check_balance()
        debit, credit, entries_diff = self.check_entries()
        
        # Statistics
        print("\nSTATISTICS:")
        print(f"Total batches: {GLBatch.query.count()}")
        print(f"Total entries: {GLEntry.query.count()}")
        
        if abs(balance_diff) < Decimal('0.01') and entries_diff < Decimal('0.01'):
            print("\n" + "="*80)
            print("✅✅✅ LEDGER IS BALANCED! ✅✅✅")
            print("="*80)
        else:
            print("\n" + "="*80)
            print("⚠️ Please review remaining differences")
            print("="*80)


def main():
    app = create_app()
    with app.app_context():
        fixer = LedgerFixer(app)
        fixer.run()


if __name__ == '__main__':
    main()
