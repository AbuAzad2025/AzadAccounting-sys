/**
 * ═══════════════════════════════════════════════════════════════════
 * 🔒 تأكيد مزدوج للعمليات الخطرة
 * ═══════════════════════════════════════════════════════════════════
 * 
 * يمنع الحذف أو التعديل العرضي للبيانات المهمة
 */

(function() {
  if (window.__CONFIRM_DANGEROUS_INIT__) return;
  window.__CONFIRM_DANGEROUS_INIT__ = true;

  'use strict';
  
  /**
   * تأكيد عملية خطرة مع تأكيد مزدوج
   * @param {string} message - رسالة التحذير
   * @param {function} callback - الدالة التي سيتم تنفيذها بعد التأكيد
   * @param {string} confirmText - نص زر التأكيد (اختياري)
   */
  window.confirmDangerousAction = function(message, callback, confirmText = 'نعم، متأكد 100%') {
    // التأكيد الأول
    if (!confirm(`⚠️ تحذير!\n\n${message}\n\nهل أنت متأكد من هذا الإجراء؟`)) {
      return false;
    }
    
    // التأكيد الثاني
    if (!confirm(`⚠️⚠️ تأكيد نهائي!\n\n${message}\n\n${confirmText}؟`)) {
      return false;
    }
    
    // تنفيذ العملية
    if (typeof callback === 'function') {
      callback();
    }
    
    return true;
  };
  
  /**
   * تأكيد حذف مستخدم
   */
  window.confirmDeleteUser = function(username, userId, formAction) {
    return confirmDangerousAction(
      `سيتم حذف المستخدم: ${username}\n\nلن يمكن التراجع عن هذا الإجراء!`,
      function() {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = formAction;
        
        // CSRF Token
        const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;
        if (csrfToken) {
          const csrfInput = document.createElement('input');
          csrfInput.type = 'hidden';
          csrfInput.name = 'csrf_token';
          csrfInput.value = csrfToken;
          form.appendChild(csrfInput);
        }
        
        document.body.appendChild(form);
        form.submit();
      },
      'نعم، احذف المستخدم نهائياً'
    );
  };
  
  /**
   * تأكيد مسح قاعدة البيانات
   */
  window.confirmClearDatabase = function(tableName, callback) {
    const message = tableName 
      ? `سيتم حذف جميع البيانات من الجدول: ${tableName}`
      : 'سيتم حذف جميع البيانات من قاعدة البيانات!';
    
    return confirmDangerousAction(
      `${message}\n\n⚠️ هذا الإجراء خطير جداً ولا يمكن التراجع عنه!`,
      callback,
      'نعم، احذف كل شيء'
    );
  };
  
  /**
   * تأكيد إيقاف النظام
   */
  window.confirmSystemShutdown = function(callback) {
    return confirmDangerousAction(
      'سيتم إيقاف النظام بالكامل!\n\nجميع المستخدمين سيتم قطع اتصالهم.',
      callback,
      'نعم، أوقف النظام'
    );
  };
  
  /**
   * تأكيد تفعيل وضع الصيانة
   */
  window.confirmMaintenanceMode = function(enable, callback) {
    const message = enable
      ? 'سيتم تفعيل وضع الصيانة\n\nجميع المستخدمين سيتم منعهم من الدخول (عدا المالك).'
      : 'سيتم تعطيل وضع الصيانة\n\nسيتمكن المستخدمون من الدخول مرة أخرى.';
    
    return confirmDangerousAction(
      message,
      callback,
      enable ? 'نعم، فعّل وضع الصيانة' : 'نعم، عطّل وضع الصيانة'
    );
  };
  
  /**
   * تأكيد مسح الكاش
   */
  window.confirmClearCache = function(callback) {
    return confirmDangerousAction(
      'سيتم مسح جميع البيانات المؤقتة (Cache)\n\nقد يؤدي هذا إلى بطء مؤقت في النظام.',
      callback,
      'نعم، امسح الكاش'
    );
  };
  
  /**
   * تأكيد إنهاء جميع الجلسات
   */
  window.confirmKillAllSessions = function(callback) {
    return confirmDangerousAction(
      'سيتم إنهاء جميع جلسات المستخدمين!\n\nجميع المستخدمين (بما فيك) سيحتاجون لتسجيل الدخول مرة أخرى.',
      callback,
      'نعم، أنهِ جميع الجلسات'
    );
  };
  
  /**
   * تأكيد استعادة نسخة احتياطية
   */
  window.confirmRestoreBackup = function(backupName, callback) {
    return confirmDangerousAction(
      `سيتم استعادة النسخة الاحتياطية: ${backupName}\n\n⚠️ سيتم استبدال البيانات الحالية بالكامل!`,
      callback,
      'نعم، استعد النسخة الاحتياطية'
    );
  };
  
  /**
   * تأكيد إعادة ضبط الإعدادات
   */
  window.confirmResetSettings = function(callback) {
    return confirmDangerousAction(
      'سيتم إعادة ضبط جميع الإعدادات إلى القيم الافتراضية!\n\nسيتم فقدان جميع التخصيصات.',
      callback,
      'نعم، أعد ضبط الإعدادات'
    );
  };
  
  /**
   * ربط تلقائي للأزرار الخطرة
   * تلقائياً يضيف تأكيد مزدوج لأي زر أو رابط يحتوي على:
   * - data-danger="true"
   * - class="btn-danger"
   * - onclick يحتوي على "delete" أو "remove"
   */
  document.addEventListener('DOMContentLoaded', function() {
    // العثور على جميع الأزرار والنماذج الخطرة
    const dangerousButtons = document.querySelectorAll(
      '[data-danger="true"], ' +
      'button[class*="btn-danger"], ' +
      'a[class*="btn-danger"], ' +
      '[data-confirm], ' +
      'form[action*="delete"], ' +
      'form[action*="remove"]'
    );
    
    dangerousButtons.forEach(element => {
      const confirmMessage = element.getAttribute('data-confirm') || 
                            element.getAttribute('title') ||
                            'هل أنت متأكد من هذا الإجراء؟';
      
      // إذا كان زر في نموذج
      if (element.tagName === 'BUTTON' && element.type === 'submit') {
        const form = element.closest('form');
        if (form && !form.hasAttribute('data-no-confirm')) {
          element.addEventListener('click', function(e) {
            e.preventDefault();
            
            confirmDangerousAction(confirmMessage, function() {
              form.submit();
            });
          });
        }
      }
      
      // إذا كان رابط
      if (element.tagName === 'A' && !element.hasAttribute('data-no-confirm')) {
        element.addEventListener('click', function(e) {
          const href = this.getAttribute('href');
          if (href && href !== '#' && href !== 'javascript:void(0)') {
            e.preventDefault();
            
            confirmDangerousAction(confirmMessage, function() {
              window.location.href = href;
            });
          }
        });
      }
    });
  });
  
})();

