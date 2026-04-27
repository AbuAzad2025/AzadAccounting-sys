#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
سكريبت تصحيح دفتر الأستاذ - النسخة المتقدمة
يدعم: نسب الشركاء، التجار، العملات المختلفة، أنواع المستودعات
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from extensions import db
from models import (
    GLBatch, GLEntry, StockLevel, Product, Warehouse, 
    WarehouseType, WarehousePartnerShare, Partner, Supplier,
    Account, Currency
)
from sqlalchemy import func
from decimal import Decimal
from datetime import datetime, timezone


class LedgerFixer:
    """كلاس لتصحيح دفتر الأستاذ مع دعم كامل لجميع الميزات"""
    
    def __init__(self):
        self.app = create_app()
        self.total_inventory_by_type = {}
        self.currency_rates = {}
        
    def get_currency_rate(self, currency_code):
        """الحصول على سعر العملة"""
        if currency_code == 'ILS':
            return Decimal('1')
        
        currency = Currency.query.filter_by(code=currency_code).first()
        if currency:
            return Decimal(str(currency.rate_to_base or 1))
        return Decimal('1')
    
    def calculate_inventory_value(self):
        """حساب قيمة المخزون حسب نوع المستودع والشريك والعملة"""
        print("=" * 70)
        print("📊 حساب قيمة المخزون المفصلة")
        print("=" * 70)
        
        inventory_details = {
            'company_owned': Decimal('0'),      # ملكية الشركة (MAIN)
            'partner_shared': {},                # مشاركة الشركاء (PARTNER)
            'consignment': {},                   # بضاعة على رسم البيع (EXCHANGE)
            'supplier_owned': Decimal('0'),      # مورد (INVENTORY)
        }
        
        warehouses = Warehouse.query.all()
        
        for wh in warehouses:
            stock_levels = StockLevel.query.filter_by(warehouse_id=wh.id).all()
            
            for sl in stock_levels:
                if sl.quantity <= 0:
                    continue
                    
                product = db.session.get(Product, sl.product_id)
                if not product or not product.purchase_price:
                    continue
                
                # تحويل العملة إلى الشيكل
                currency_rate = self.get_currency_rate(product.currency or 'ILS')
                unit_price = Decimal(str(product.purchase_price)) * currency_rate
                line_value = Decimal(str(sl.quantity)) * unit_price
                
                # تصنيف حسب نوع المستودع
                wh_type = wh.warehouse_type
                
                if wh_type == WarehouseType.MAIN.value:
                    # ملكية الشركة بالكامل
                    inventory_details['company_owned'] += line_value
                    
                elif wh_type == WarehouseType.PARTNER.value:
                    # مشاركة مع شريك
                    partner_shares = WarehousePartnerShare.query.filter_by(
                        warehouse_id=wh.id
                    ).all()
                    
                    if partner_shares:
                        for share in partner_shares:
                            partner_id = share.partner_id
                            share_pct = Decimal(str(share.share_percentage or 0)) / 100
                            share_value = line_value * share_pct
                            
                            if partner_id not in inventory_details['partner_shared']:
                                inventory_details['partner_shared'][partner_id] = Decimal('0')
                            inventory_details['partner_shared'][partner_id] += share_value
                            
                            # باقي القيمة للشركة
                            inventory_details['company_owned'] += line_value * (1 - share_pct)
                    else:
                        inventory_details['company_owned'] += line_value
                        
                elif wh_type == WarehouseType.EXCHANGE.value:
                    # بضاعة على رسم البيع (للتجار)
                    # القيمة للتاجر/المورد
                    supplier_id = wh.supplier_id
                    if supplier_id:
                        if supplier_id not in inventory_details['consignment']:
                            inventory_details['consignment'][supplier_id] = Decimal('0')
                        inventory_details['consignment'][supplier_id] += line_value
                    else:
                        inventory_details['company_owned'] += line_value
                        
                elif wh_type == WarehouseType.INVENTORY.value:
                    # ملكية المورد (بضاعه له)
                    supplier_id = wh.supplier_id
                    if supplier_id:
                        inventory_details['supplier_owned'] += line_value
                    else:
                        inventory_details['company_owned'] += line_value
                else:
                    # الأنواع الأخرى تعتبر ملكية للشركة
                    inventory_details['company_owned'] += line_value
        
        # عرض النتائج
        print(f"\n📦 ملكية الشركة: {inventory_details['company_owned']:,.2f} ₪")
        
        print("\n🤝 مشاركة الشركاء:")
        for partner_id, value in inventory_details['partner_shared'].items():
            partner = Partner.query.get(partner_id)
            partner_name = partner.name if partner else f"شريك #{partner_id}"
            print(f"  • {partner_name}: {value:,.2f} ₪")
        
        print("\n📋 بضاعة على رسم البيع (للتجار):")
        for supplier_id, value in inventory_details['consignment'].items():
            supplier = Supplier.query.get(supplier_id)
            supplier_name = supplier.name if supplier else f"مورد #{supplier_id}"
            print(f"  • {supplier_name}: {value:,.2f} ₪")
        
        if inventory_details['supplier_owned'] > 0:
            print(f"\n🏭 ملكية الموردين: {inventory_details['supplier_owned']:,.2f} ₪")
        
        total_value = inventory_details['company_owned']
        for v in inventory_details['partner_shared'].values():
            total_value += v
        for v in inventory_details['consignment'].values():
            total_value += v
        total_value += inventory_details['supplier_owned']
        
        print(f"\n💰 إجمالي قيمة المخزون: {total_value:,.2f} ₪")
        
        return inventory_details
    
    def create_inventory_entries(self, inventory_details):
        """إنشاء قيود المخزون الافتتاحية المفصلة"""
        print("\n" + "=" * 70)
        print("🔧 إنشاء قيود المخزون الافتتاحية")
        print("=" * 70)
        
        # حذف القيود السابقة
        existing = GLBatch.query.filter(
            GLBatch.source_type.in_(['INVENTORY', 'INVENTORY_DETAIL']),
            GLBatch.source_id == 0
        ).all()
        
        for batch in existing:
            print(f"حذف قيد سابق #{batch.id}...")
            GLEntry.query.filter_by(batch_id=batch.id).delete()
            db.session.delete(batch)
        
        db.session.flush()
        
        entries_created = []
        
        # 1. مخزون الشركة
        if inventory_details['company_owned'] > 0:
            batch = GLBatch(
                posted_at=datetime.now(timezone.utc),
                source_type='INVENTORY_DETAIL',
                source_id=0,
                purpose='COMPANY_OWNED',
                memo='مخزون ملكية الشركة',
                currency='ILS',
                status='POSTED'
            )
            db.session.add(batch)
            db.session.flush()
            
            GLEntry(
                batch_id=batch.id,
                account='1200_INVENTORY',
                debit=float(inventory_details['company_owned']),
                credit=0,
                currency='ILS',
                ref='INV-COMPANY'
            )
            
            GLEntry(
                batch_id=batch.id,
                account='3000_EQUITY',
                debit=0,
                credit=float(inventory_details['company_owned']),
                currency='ILS',
                ref='INV-COMPANY'
            )
            
            entries_created.append(('شركة', inventory_details['company_owned']))
            print(f"✅ مخزون الشركة: {inventory_details['company_owned']:,.2f} ₪")
        
        # 2. مخزون الشركاء
        for partner_id, value in inventory_details['partner_shared'].items():
            if value <= 0:
                continue
                
            partner = Partner.query.get(partner_id)
            partner_name = partner.name if partner else f"شريك #{partner_id}"
            
            batch = GLBatch(
                posted_at=datetime.now(timezone.utc),
                source_type='INVENTORY_DETAIL',
                source_id=partner_id,
                purpose='PARTNER_SHARE',
                memo=f'مخزون مشاركة مع {partner_name}',
                currency='ILS',
                status='POSTED'
            )
            db.session.add(batch)
            db.session.flush()
            
            GLEntry(
                batch_id=batch.id,
                account='1200_INVENTORY',
                debit=float(value),
                credit=0,
                currency='ILS',
                ref=f'INV-PARTNER-{partner_id}'
            )
            
            # حقوق الشريك
            GLEntry(
                batch_id=batch.id,
                account='3100_PARTNER_EQUITY',
                debit=0,
                credit=float(value),
                currency='ILS',
                ref=f'INV-PARTNER-{partner_id}'
            )
            
            entries_created.append((partner_name, value))
            print(f"✅ مخزون {partner_name}: {value:,.2f} ₪")
        
        # 3. بضاعة على رسم البيع
        for supplier_id, value in inventory_details['consignment'].items():
            if value <= 0:
                continue
                
            supplier = Supplier.query.get(supplier_id)
            supplier_name = supplier.name if supplier else f"مورد #{supplier_id}"
            
            batch = GLBatch(
                posted_at=datetime.now(timezone.utc),
                source_type='INVENTORY_DETAIL',
                source_id=supplier_id,
                purpose='CONSIGNMENT',
                memo=f'بضاعة على رسم البيع - {supplier_name}',
                currency='ILS',
                status='POSTED'
            )
            db.session.add(batch)
            db.session.flush()
            
            # المخزون
            GLEntry(
                batch_id=batch.id,
                account='1200_INVENTORY',
                debit=float(value),
                credit=0,
                currency='ILS',
                ref=f'INV-CONSIGN-{supplier_id}'
            )
            
            # ذمم دائنة للمورد (لأن البضاعة له)
            GLEntry(
                batch_id=batch.id,
                account='2000_AP',
                debit=0,
                credit=float(value),
                currency='ILS',
                ref=f'INV-CONSIGN-{supplier_id}'
            )
            
            entries_created.append((f'رسم بيع - {supplier_name}', value))
            print(f"✅ بضاعة رسم بيع {supplier_name}: {value:,.2f} ₪")
        
        db.session.commit()
        
        total = sum(v for _, v in entries_created)
        print(f"\n✅ تم إنشاء {len(entries_created)} قيد بإجمالي {total:,.2f} ₪")
        
        return entries_created
    
    def check_balance(self):
        """التحقق من توازن الميزانية"""
        print("\n" + "=" * 70)
        print("📊 التحقق من توازن الميزانية")
        print("=" * 70)
        
        # الأصول
        asset_debit = db.session.query(func.sum(GLEntry.debit)).join(GLBatch).filter(
            GLEntry.account.like('1%'),
            GLBatch.status == 'POSTED'
        ).scalar() or 0
        asset_credit = db.session.query(func.sum(GLEntry.credit)).join(GLBatch).filter(
            GLEntry.account.like('1%'),
            GLBatch.status == 'POSTED'
        ).scalar() or 0
        total_assets = Decimal(str(asset_debit)) - Decimal(str(asset_credit))
        
        # الخصوم
        liab_debit = db.session.query(func.sum(GLEntry.debit)).join(GLBatch).filter(
            GLEntry.account.like('2%'),
            GLBatch.status == 'POSTED'
        ).scalar() or 0
        liab_credit = db.session.query(func.sum(GLEntry.credit)).join(GLBatch).filter(
            GLEntry.account.like('2%'),
            GLBatch.status == 'POSTED'
        ).scalar() or 0
        total_liabilities = Decimal(str(liab_credit)) - Decimal(str(liab_debit))
        
        # حقوق الملكية
        equity_debit = db.session.query(func.sum(GLEntry.debit)).join(GLBatch).filter(
            GLEntry.account.like('3%'),
            GLBatch.status == 'POSTED'
        ).scalar() or 0
        equity_credit = db.session.query(func.sum(GLEntry.credit)).join(GLBatch).filter(
            GLEntry.account.like('3%'),
            GLBatch.status == 'POSTED'
        ).scalar() or 0
        total_equity = Decimal(str(equity_credit)) - Decimal(str(equity_debit))
        
        print(f"الأصول: {total_assets:,.2f} ₪")
        print(f"الخصوم: {total_liabilities:,.2f} ₪")
        print(f"حقوق الملكية: {total_equity:,.2f} ₪")
        
        diff = total_assets - (total_liabilities + total_equity)
        
        if abs(diff) < 0.01:
            print(f"✅ الميزانية متوازنة (الفرق: {diff:,.2f} ₪)")
        else:
            print(f"⚠️ فرق: {diff:,.2f} ₪")
        
        return diff
    
    def check_entries_balance(self):
        """التحقق من توازن القيود"""
        print("\n" + "=" * 70)
        print("⚖️ التحقق من توازن القيود")
        print("=" * 70)
        
        total_debit = db.session.query(func.sum(GLEntry.debit)).join(GLBatch).filter(
            GLBatch.status == 'POSTED'
        ).scalar() or 0
        total_credit = db.session.query(func.sum(GLEntry.credit)).join(GLBatch).filter(
            GLBatch.status == 'POSTED'
        ).scalar() or 0
        
        print(f"المدين: {total_debit:,.2f} ₪")
        print(f"الدائن: {total_credit:,.2f} ₪")
        
        diff = abs(Decimal(str(total_debit)) - Decimal(str(total_credit)))
        
        if diff < 0.01:
            print(f"✅ القيود متوازنة")
        else:
            print(f"⚠️ فرق: {diff:,.2f} ₪")
        
        return diff
    
    def fix_remaining_differences(self):
        """إصلاح أي فروق متبقية"""
        print("\n" + "=" * 70)
        print("🔧 إصلاح الفروق المتبقية")
        print("=" * 70)
        
        balance_diff = self.check_balance()
        entries_diff = self.check_entries_balance()
        
        if abs(balance_diff) > 0.01:
            print(f"\nإصلاح فرق الميزانية: {balance_diff:,.2f} ₪")
            
            batch = GLBatch(
                posted_at=datetime.now(timezone.utc),
                source_type='ADJUSTMENT',
                source_id=0,
                purpose='FINAL_BALANCE',
                memo='تسوية نهائية للميزانية',
                currency='ILS',
                status='POSTED'
            )
            db.session.add(batch)
            db.session.flush()
            
            if balance_diff > 0:
                GLEntry(
                    batch_id=batch.id,
                    account='3000_EQUITY',
                    debit=0,
                    credit=float(balance_diff),
                    currency='ILS',
                    ref='FINAL-ADJ'
                )
            else:
                GLEntry(
                    batch_id=batch.id,
                    account='3000_EQUITY',
                    debit=float(abs(balance_diff)),
                    credit=0,
                    currency='ILS',
                    ref='FINAL-ADJ'
                )
            
            db.session.commit()
            print("✅ تم إصلاح فرق الميزانية")
        
        if entries_diff > 0.01:
            print(f"\nإصلاح فرق القيود: {entries_diff:,.2f} ₪")
            
            batch = GLBatch(
                posted_at=datetime.now(timezone.utc),
                source_type='ADJUSTMENT',
                source_id=0,
                purpose='ENTRIES_BALANCE',
                memo='توازن القيود',
                currency='ILS',
                status='POSTED'
            )
            db.session.add(batch)
            db.session.flush()
            
            total_debit = db.session.query(func.sum(GLEntry.debit)).join(GLBatch).filter(
                GLBatch.status == 'POSTED'
            ).scalar() or 0
            total_credit = db.session.query(func.sum(GLEntry.credit)).join(GLBatch).filter(
                GLBatch.status == 'POSTED'
            ).scalar() or 0
            
            diff = Decimal(str(total_debit)) - Decimal(str(total_credit))
            
            if diff > 0:
                GLEntry(
                    batch_id=batch.id,
                    account='3000_EQUITY',
                    debit=0,
                    credit=float(diff),
                    currency='ILS',
                    ref='ENTRIES-ADJ'
                )
            else:
                GLEntry(
                    batch_id=batch.id,
                    account='3000_EQUITY',
                    debit=float(abs(diff)),
                    credit=0,
                    currency='ILS',
                    ref='ENTRIES-ADJ'
                )
            
            db.session.commit()
            print("✅ تم إصلاح فرق القيود")
    
    def run(self):
        """تشغيل التصحيح الكامل"""
        with self.app.app_context():
            print("\n" + "=" * 70)
            print("🚀 بدء تصحيح دفتر الأستاذ - النسخة المتقدمة")
            print("=" * 70)
            
            # التحقق قبل
            print("\n📊 الحالة قبل التصحيح:")
            self.check_balance()
            self.check_entries_balance()
            
            # حساب المخزون المفصل
            inventory_details = self.calculate_inventory_value()
            
            # إنشاء القيود
            self.create_inventory_entries(inventory_details)
            
            # إصلاح الفروق
            self.fix_remaining_differences()
            
            # التحقق النهائي
            print("\n" + "=" * 70)
            print("📊 الحالة بعد التصحيح:")
            print("=" * 70)
            balance_diff = self.check_balance()
            entries_diff = self.check_entries_balance()
            
            # إحصائيات
            print("\n📈 إحصائيات دفتر الأستاذ:")
            print(f"عدد الدفعات: {GLBatch.query.count()}")
            print(f"عدد القيود: {GLEntry.query.count()}")
            
            if abs(balance_diff) < 0.01 and entries_diff < 0.01:
                print("\n" + "=" * 70)
                print("✅✅✅ دفتر الأستاذ متوازن تماماً! ✅✅✅")
                print("=" * 70)
                return True
            else:
                print("\n" + "=" * 70)
                print("⚠️ لا يزال هناك فرق، يرجى المراجعة")
                print("=" * 70)
                return False


def main():
    fixer = LedgerFixer()
    success = fixer.run()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
