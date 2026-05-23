/**
 * رسائل موحّدة — toasts، flashes، أخطاء AJAX، تحقق النماذج
 */
(function () {
  'use strict';

  const TITLES = {
    success: 'تم بنجاح',
    danger: 'خطأ',
    error: 'خطأ',
    warning: 'تنبيه',
    info: 'معلومة',
  };

  const ICONS = {
    success: 'fa-check-circle',
    danger: 'fa-times-circle',
    error: 'fa-times-circle',
    warning: 'fa-exclamation-triangle',
    info: 'fa-info-circle',
  };

  function normalizeType(type) {
    const t = String(type || 'info').toLowerCase();
    if (t === 'error' || t === 'fail' || t === 'danger') return 'danger';
    if (t === 'warn' || t === 'alert') return 'warning';
    return ['success', 'warning', 'info', 'danger'].includes(t) ? t : 'info';
  }

  function stripEmoji(text) {
    return String(text || '')
      .replace(/^[\s✅❌⚠️ℹ️🔴🟢🟡🔵⭐📌💡]+/, '')
      .trim();
  }

  function humanize(text) {
    const t = stripEmoji(text);
    if (!t || t === 'حدث خطأ داخلي' || t === 'حدث خطأ') {
      return 'تعذّر إكمال العملية. تحقق من البيانات وحاول مجدداً، أو تواصل مع مسؤول النظام إن استمر الخطأ.';
    }
    return t;
  }

  function escapeHtml(value) {
    return String(value ?? '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function ensureToastHost() {
    let host = document.getElementById('ux-toast-host');
    if (host) return host;
    host = document.createElement('div');
    host.id = 'ux-toast-host';
    host.className = 'ux-toast-host';
    host.setAttribute('aria-live', 'polite');
    host.setAttribute('aria-relevant', 'additions');
    document.body.appendChild(host);
    return host;
  }

  function notify(type, message, options) {
    options = options || {};
    const cat = normalizeType(type);
    const title = options.title || TITLES[cat] || 'إشعار';
    const body = humanize(message);
    const duration = options.duration != null ? options.duration : (cat === 'success' || cat === 'info' ? 6000 : 0);

    if (typeof Swal !== 'undefined' && options.modal) {
      Swal.fire({
        title: title,
        text: body,
        icon: cat === 'danger' ? 'error' : cat,
        confirmButtonText: options.confirmText || 'حسناً',
      });
      return;
    }

    if (typeof toastr !== 'undefined' && !options.inline) {
      const method = cat === 'danger' ? 'error' : cat;
      toastr.options = Object.assign(
        {
          closeButton: true,
          progressBar: true,
          positionClass: 'toast-top-left',
          timeOut: duration || 8000,
          extendedTimeOut: 2000,
          rtl: true,
        },
        options.toastr || {}
      );
      toastr[method](body, title);
      return;
    }

    const host = ensureToastHost();
    const toast = document.createElement('div');
    toast.className = 'ux-toast ux-toast--' + cat;
    toast.setAttribute('role', 'status');
    toast.innerHTML =
      '<div class="ux-toast__icon"><i class="fas ' +
      (ICONS[cat] || 'fa-info-circle') +
      '" aria-hidden="true"></i></div>' +
      '<div class="ux-toast__content">' +
      '<strong class="ux-toast__title">' +
      escapeHtml(title) +
      '</strong>' +
      '<p class="ux-toast__text">' +
      escapeHtml(body) +
      '</p></div>' +
      '<button type="button" class="ux-toast__close" aria-label="إغلاق">&times;</button>';
    host.appendChild(toast);
    requestAnimationFrame(function () {
      toast.classList.add('ux-toast--visible');
    });
    toast.querySelector('.ux-toast__close').addEventListener('click', function () {
      toast.classList.remove('ux-toast--visible');
      setTimeout(function () {
        toast.remove();
      }, 250);
    });
    if (duration > 0) {
      setTimeout(function () {
        if (toast.parentNode) {
          toast.classList.remove('ux-toast--visible');
          setTimeout(function () {
            toast.remove();
          }, 250);
        }
      }, duration);
    }
  }

  function enhanceInlineFlashes() {
    document.querySelectorAll('.ux-flash-stack .ux-flash').forEach(function (el) {
      const cat = el.dataset.category || 'info';
      if (cat === 'success' || cat === 'info') {
        setTimeout(function () {
          if (!el.classList.contains('ux-flash--dismissed')) {
            el.classList.add('ux-flash--fade');
            setTimeout(function () {
              el.remove();
            }, 400);
          }
        }, 9000);
      }
    });
  }

  function enhanceFormValidation() {
    document.querySelectorAll('form.needs-validation, form[data-ux-validate]').forEach(function (form) {
      if (form.dataset.uxValidateBound) return;
      form.dataset.uxValidateBound = '1';
      form.addEventListener(
        'submit',
        function (ev) {
          if (!form.checkValidity()) {
            ev.preventDefault();
            ev.stopPropagation();
            const firstInvalid = form.querySelector(':invalid');
            if (firstInvalid) {
              firstInvalid.focus({ preventScroll: false });
              firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
            notify('warning', 'يرجى مراجعة الحقول المظلّلة وتصحيحها قبل المتابعة.', { inline: true });
          }
          form.classList.add('was-validated');
        },
        false
      );
    });
  }

  function patchFetchErrors() {
    if (window.__UX_FETCH_PATCHED__) return;
    window.__UX_FETCH_PATCHED__ = true;
    const orig = window.fetch;
    if (typeof orig !== 'function') return;
    window.fetch = function () {
      return orig.apply(this, arguments).then(function (res) {
        if (!res.ok && res.status >= 500) {
          notify('danger', 'تعذّر إكمال العملية على الخادم. حاول لاحقاً.');
        }
        return res;
      });
    };
  }

  window.AzadUX = window.AzadUX || {};
  window.AzadUX.notify = notify;
  window.AzadUX.humanize = humanize;
  window.showToast = function (message, type) {
    notify(type || 'info', message);
  };

  function init() {
    enhanceInlineFlashes();
    enhanceFormValidation();
    patchFetchErrors();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
