import re

file_path = "D:/karaj/garage_manager_project/garage_manager/templates/security/saas_manager.html"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

replacements = [
    ("alert('باقة غير موجودة');", "if(typeof showToast!=='undefined')showToast('باقة غير موجودة','warning');else alert('باقة غير موجودة');"),
    ("alert('فشل جلب البيانات');", "if(typeof showToast!=='undefined')showToast('فشل جلب البيانات','error');else alert('فشل جلب البيانات');"),
    ("alert('تم التحديث بنجاح');", "if(typeof showToast!=='undefined')showToast('تم التحديث بنجاح','success');else alert('تم التحديث بنجاح');"),
    ("alert('تم إلغاء الاشتراك بنجاح');", "if(typeof showToast!=='undefined')showToast('تم إلغاء الاشتراك بنجاح','success');else alert('تم إلغاء الاشتراك بنجاح');"),
    ("alert('تم تجديد الاشتراك بنجاح');", "if(typeof showToast!=='undefined')showToast('تم تجديد الاشتراك بنجاح','success');else alert('تم تجديد الاشتراك بنجاح');"),
    ("alert('تم تأكيد الدفع بنجاح');", "if(typeof showToast!=='undefined')showToast('تم تأكيد الدفع بنجاح','success');else alert('تم تأكيد الدفع بنجاح');"),
    ("alert('تم إنشاء الفاتورة بنجاح');", "if(typeof showToast!=='undefined')showToast('تم إنشاء الفاتورة بنجاح','success');else alert('تم إنشاء الفاتورة بنجاح');"),
    ("alert('يرجى ملء جميع الحقول المطلوبة');", "if(typeof showToast!=='undefined')showToast('يرجى ملء جميع الحقول المطلوبة','warning');else alert('يرجى ملء جميع الحقول المطلوبة');"),
    ("alert('خطأ: فشل التأكيد');", "if(typeof showToast!=='undefined')showToast('خطأ: فشل التأكيد','error');else alert('خطأ: فشل التأكيد');"),
    ("alert('خطأ: فشل الإلغاء');", "if(typeof showToast!=='undefined')showToast('خطأ: فشل الإلغاء','error');else alert('خطأ: فشل الإلغاء');"),
    ("alert('خطأ: Modal غير موجود');", "if(typeof showToast!=='undefined')showToast('خطأ: Modal غير موجود','error');else alert('خطأ: Modal غير موجود');"),
    
    # Variable alerts
    ("alert('خطأ: ' + e.message);", "if(typeof showToast!=='undefined')showToast('خطأ: '+e.message,'error');else alert('خطأ: '+e.message);"),
    ("alert('خطأ: ' + (data.error || 'فشل التحديث'));", "if(typeof showToast!=='undefined')showToast('خطأ: '+(data.error||'فشل التحديث'),'error');else alert('خطأ: '+(data.error||'فشل التحديث'));"),
    ("alert('خطأ: ' + (result.error || 'فشل التجديد'));", "if(typeof showToast!=='undefined')showToast('خطأ: '+(result.error||'فشل التجديد'),'error');else alert('خطأ: '+(result.error||'فشل التجديد'));"),
    ("alert('خطأ: ' + (result.error || 'فشل الإرسال'));", "if(typeof showToast!=='undefined')showToast('خطأ: '+(result.error||'فشل الإرسال'),'error');else alert('خطأ: '+(result.error||'فشل الإرسال'));"),
    ("alert('خطأ: ' + (result.error || 'فشل الحفظ'));", "if(typeof showToast!=='undefined')showToast('خطأ: '+(result.error||'فشل الحفظ'),'error');else alert('خطأ: '+(result.error||'فشل الحفظ'));"),
    ("alert(result.message || 'تم إرسال التذكير بنجاح');", "if(typeof showToast!=='undefined')showToast(result.message||'تم إرسال التذكير بنجاح','success');else alert(result.message||'تم إرسال التذكير بنجاح');")
]

for old, new in replacements:
    content = content.replace(old, new)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed saas_manager.html safely")
