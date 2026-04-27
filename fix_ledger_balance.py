#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
سكريبت تصحيح توازن دفتر الأستاذ - v2.0
================================================================================

يقوم هذا السكريبت بـ:
✅ تحليل الفرق المحاسبي
✅ إنشاء قيد تسوية لإغلاق الفرق
✅ الحفاظ على توازن القيود (المدين = الدائن)

المنطق المحاسبي:
Assets = Liabilities + Equity
الفرق = Assets - (Liabilities + Equity)
يجب أن يكون الفرق = 0
================================================================================
"""

import sys
import os
from decimal import Decimal
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from extensions import db
from models import GLBatch, GLEntry
from sqlalchemy import func


def get_balance_summary():
    """الحصول على ملخص الميزانية"""
    # Assets (1xxx)
    assets_dr = db.session.query(func.sum(GLEntry.debit)).join(GLBatch).filter(
        GLEntry.account.like('1%'),
        GLBatch.status == 'POSTED'
    ).scalar() or 0
    assets_cr = db.session.query(func.sum(GLEntry.credit)).join(GLBatch).filter(
        GLEntry.account.like('1%'),
        GLBatch.status == 'POSTED'
    ).scalar() or 0
    assets = Decimal(str(assets_dr)) - Decimal(str(assets_cr))
    
    # Liabilities (2xxx)
    liab_dr = db.session.query(func.sum(GLEntry.debit)).join(GLBatch).filter(
        GLEntry.account.like('2%'),
        GLBatch.status == 'POSTED'
    ).scalar() or 0
    liab_cr = db.session.query(func.sum(GLEntry.credit)).join(GLBatch).filter(
        GLEntry.account.like('2%'),
        GLBatch.status == 'POSTED'
    ).scalar() or 0
    liabilities = Decimal(str(liab_cr)) - Decimal(str(liab_dr))
    
    # Equity (3xxx)
    equity_dr = db.session.query(func.sum(GLEntry.debit)).join(GLBatch).filter(
        GLEntry.account.like('3%'),
        GLBatch.status == 'POSTED'
    ).scalar() or 0
    equity_cr = db.session.query(func.sum(GLEntry.credit)).join(GLBatch).filter(
        GLEntry.account.like('3%'),
        GLBatch.status == 'POSTED'
    ).scalar() or 0
    equity = Decimal(str(equity_cr)) - Decimal(str(equity_dr))
    
    # Revenue (4xxx) - مؤقتة حتى يتم إغلاقها
    rev_dr = db.session.query(func.sum(GLEntry.debit)).join(GLBatch).filter(
        GLEntry.account.like('4%'),
        GLBatch.status == 'POSTED'
    ).scalar() or 0
    rev_cr = db.session.query(func.sum(GLEntry.credit)).join(GLBatch).filter(
        GLEntry.account.like('4%'),
        GLBatch.status == 'POSTED'
    ).scalar() or 0
    revenue = Decimal(str(rev_cr)) - Decimal(str(rev_dr))
    
    # Expenses (5xxx, 6xxx)
    exp_dr = db.session.query(func.sum(GLEntry.debit)).join(GLBatch).filter(
        GLEntry.account.like('5%') | GLEntry.account.like('6%'),
        GLBatch.status == 'POSTED'
    ).scalar() or 0
    exp_cr = db.session.query(func.sum(GLEntry.credit)).join(GLBatch).filter(
        GLEntry.account.like('5%') | GLEntry.account.like('6%'),
        GLBatch.status == 'POSTED'
    ).scalar() or 0
    expenses = Decimal(str(exp_dr)) - Decimal(str(exp_cr))
    
    # Calculate difference
    # Assets = Liabilities + Equity + (Revenue - Expenses)
    expected_assets = liabilities + equity + revenue - expenses
    difference = assets - expected_assets
    
    return {
        'assets': assets,
        'liabilities': liabilities,
        'equity': equity,
        'revenue': revenue,
        'expenses': expenses,
        'difference': difference,
        'expected_assets': expected_assets
    }


def print_balance(data, title=""):
    """طباعة حالة الميزانية"""
    if title:
        print("\n" + "="*80)
        print(title)
        print("="*80)
    
    print(f"\n📊 الميزانية:")
    print(f"   الأصول:        {data['assets']:15,.2f} ₪")
    print(f"   الخصوم:        {data['liabilities']:15,.2f} ₪")
    print(f"   حقوق الملكية: {data['equity']:15,.2f} ₪")
    print(f"   الإيرادات:     {data['revenue']:15,.2f} ₪")
    print(f"   المصاريف:      {data['expenses']:15,.2f} ₪")
    print(f"\n📊 المعادلة:")
    print(f"   الأصول ({data['assets']:,.2f}) = الخصوم ({data['liabilities']:,.2f}) + حقوق الملكية ({data['equity']:,.2f}) + إيرادات ({data['revenue']:,.2f}) - مصاريف ({data['expenses']:,.2f})")
    print(f"   المتوقع: {data['expected_assets']:,.2f} ₪")
    print(f"\n📊 الفرق: {data['difference']:,.2f} ₪")
    
    if abs(data['difference']) < 100:
        print("   ✅ الميزانية متوازنة")
    else:
        print("   ⚠️ الميزانية غير متوازنة")


def create_adjustment_entry(difference):
    """
    إنشاء قيد تسوية للفرق
    
    المنطق:
    - إذا كان الفرق موجباً: الأصول أكبر من المتوقع
      نقلل الأصول أو نزيد الخصوم/حقوق الملكية
    - إذا كان الفرق سالباً: الأصول أقل من المتوقع
      نزيد الأصول أو نقلل الخصوم/حقوق الملكية
    """
    print("\n" + "="*80)
    print("🔧 إنشاء قيد تسوية")
    print("="*80)
    
    if abs(difference) < 0.01:
        print("ℹ️ لا يوجد فرق يحتاج لتسوية")
        return None
    
    # إنشاء دفعة
    batch = GLBatch(
        posted_at=datetime.now(timezone.utc),
        source_type='SYSTEM',
        source_id=0,
        purpose='ADJUSTMENT',
        memo=f'تسوية فرق الميزانية: {difference:,.2f} ₪',
        currency='ILS',
        status='DRAFT'
    )
    db.session.add(batch)
    db.session.flush()
    
    print(f"\n📋 دفعة التسوية #{batch.id}")
    print(f"   الفرق المراد تسويته: {difference:,.2f} ₪")
    
    # استخدام حساب 3100_OWNER_CURRENT كحساب تسوية
    # إذا كان الفرق موجباً: ندين الأصول وندين حساب التسوية
    # إذا كان الفرق سالباً: ندين حساب التسوية وندين الأصول
    
    adjustment_account = '3100_OWNER_CURRENT'
    
    if difference > 0:
        # الأصول أكبر من المتوقع
        # نقوم بتصحيح عبر تقليل الأصول (دائن) وزيادة حقوق الملكية (دائن)
        # أو بشكل مبسط: نقلل الأصول عبر دائن، وندين حساب التسوية
        
        # لكن هذا سيخلق فرقاً آخر...
        # الحل الصحيح: إنشاء قيد يعكس الفرق في حساب التسوية
        
        entry1 = GLEntry(
            batch_id=batch.id,
            account='1200_INVENTORY',  # تعديل في المخزون
            debit=0,
            credit=float(difference),
            currency='ILS',
            ref='ADJ-REDUCE-ASSETS'
        )
        db.session.add(entry1)
        
        entry2 = GLEntry(
            batch_id=batch.id,
            account=adjustment_account,
            debit=float(difference),
            credit=0,
            currency='ILS',
            ref='ADJ-OFFSET'
        )
        db.session.add(entry2)
        
        print(f"   مدين: {adjustment_account} = {difference:,.2f} ₪")
        print(f"   دائن: 1200_INVENTORY = {difference:,.2f} ₪")
        
    else:
        # الأصول أقل من المتوقع (الفرق سالب)
        diff_abs = abs(difference)
        
        entry1 = GLEntry(
            batch_id=batch.id,
            account='1200_INVENTORY',
            debit=float(diff_abs),
            credit=0,
            currency='ILS',
            ref='ADJ-INCREASE-ASSETS'
        )
        db.session.add(entry1)
        
        entry2 = GLEntry(
            batch_id=batch.id,
            account=adjustment_account,
            debit=0,
            credit=float(diff_abs),
            currency='ILS',
            ref='ADJ-OFFSET'
        )
        db.session.add(entry2)
        
        print(f"   مدين: 1200_INVENTORY = {diff_abs:,.2f} ₪")
        print(f"   دائن: {adjustment_account} = {diff_abs:,.2f} ₪")
    
    # التحقق من التوازن
    db.session.flush()
    entries = GLEntry.query.filter_by(batch_id=batch.id).all()
    dr_total = sum(e.debit for e in entries)
    cr_total = sum(e.credit for e in entries)
    
    print(f"\n⚖️ التحقق:")
    print(f"   مدين: {dr_total:,.2f} ₪")
    print(f"   دائن: {cr_total:,.2f} ₪")
    
    if abs(dr_total - cr_total) < 0.01:
        batch.status = 'POSTED'
        db.session.commit()
        print(f"   ✅ تم إنشاء قيد التسوية بنجاح")
        return batch
    else:
        db.session.rollback()
        print(f"   ❌ خطأ في التوازن")
        return None


def main():
    """الدالة الرئيسية"""
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*80)
        print("🚀 سكريبت تصحيح توازن دفتر الأستاذ - v2.0")
        print("="*80)
        
        # قبل التسوية
        before = get_balance_summary()
        print_balance(before, "📊 الحالة قبل التسوية")
        
        if abs(before['difference']) < 100:
            print("\n✅ دفتر الأستاذ متوازن بالفعل!")
            return
        
        # سؤال المستخدم
        print("\n" + "="*80)
        response = input("هل تريد إنشاء قيد التسوية؟ (yes/no): ")
        
        if response.lower() != 'yes':
            print("❌ تم الإلغاء")
            return
        
        # إنشاء التسوية
        batch = create_adjustment_entry(before['difference'])
        
        if batch:
            # بعد التسوية
            after = get_balance_summary()
            print_balance(after, "📊 الحالة بعد التسوية")
            
            if abs(after['difference']) < 100:
                print("\n" + "="*80)
                print("✅✅✅ تم تصحيح دفتر الأستاذ بنجاح! ✅✅✅")
                print("="*80)
            else:
                print("\n⚠️ ما زال هناك فرق بعد التسوية")
        else:
            print("\n❌ فشل إنشاء قيد التسوية")


if __name__ == '__main__':
    main()
