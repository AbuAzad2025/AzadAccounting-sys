/**
 * تحسين تجربة النماذج: قوائم منسدلة، أزرار، تسميات موحّدة.
 */
(function () {
  'use strict';

  function initSelect2Unified() {
    if (!window.jQuery || !$.fn.select2) return;
    $('select.form-control:not([data-no-select2])').each(function () {
      const $el = $(this);
      if ($el.data('select2')) return;
      $el.select2({
        dir: 'rtl',
        width: '100%',
        placeholder: $el.attr('placeholder') || '— اختر —',
        allowClear: !$el.prop('required'),
      });
    });
  }

  function normalizeEmptyOptions() {
    document.querySelectorAll('select.form-control').forEach(function (sel) {
      const first = sel.options[0];
      if (!first) return;
      const t = (first.textContent || '').trim();
      if (t === '' || t === 'اختر' || t === 'اختر...' || t === '—') {
        first.textContent = '— اختر —';
        first.value = first.value || '';
      }
    });
  }

  function bindSubmitLoading() {
    document.querySelectorAll('form[data-ux-submit]').forEach(function (form) {
      if (form.dataset.uxBound) return;
      form.dataset.uxBound = '1';
      form.addEventListener('submit', function () {
        const btn = form.querySelector('[type="submit"]');
        if (!btn || btn.disabled) return;
        btn.dataset.uxOrig = btn.innerHTML;
        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> جاري الحفظ…';
      });
    });
  }

  function init() {
    normalizeEmptyOptions();
    initSelect2Unified();
    bindSubmitLoading();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
