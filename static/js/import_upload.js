(function() {
  if (window.__IMPORT_UPLOAD_INIT__) return;
  window.__IMPORT_UPLOAD_INIT__ = true;

  document.addEventListener('DOMContentLoaded', function () {
    const input = document.querySelector('#upload-form input[type="file"]');
  if (!input) return;

  const MAX_SIZE_MB = 5;
  const MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024;

  input.addEventListener('change', function () {
    const file = input.files[0];
    if (!file) return;

    const ext = file.name.split('.').pop().toLowerCase();
    const mime = file.type;

    const allowedExtensions = ['csv', 'xls', 'xlsx'];
    const allowedMimeTypes = [
      'text/csv',
      'application/vnd.ms-excel',
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    ];

    if (!allowedExtensions.includes(ext) || !allowedMimeTypes.includes(mime)) {
      showNotification('❌ الرجاء اختيار ملف بصيغة CSV أو Excel فقط', 'danger');
      input.value = '';
      return;
    }

    if (file.size > MAX_SIZE_BYTES) {
      showNotification(`❌ حجم الملف كبير جدًا. الحد الأقصى ${MAX_SIZE_MB}MB`, 'danger');
      input.value = '';
      return;
    }

    showNotification('✅ تم اختيار ملف صالح.', 'success');
  });

  var showNotification = window.showNotification || function(message, type) {
    type = type || 'info';
    var el = document.createElement('div');
    el.className = 'alert alert-' + type + ' position-fixed top-0 end-0 m-3 shadow';
    el.style.zIndex = 2000;
    el.textContent = message;
    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'close';
    btn.setAttribute('data-dismiss', 'alert');
    btn.innerHTML = '<span aria-hidden="true">&times;</span>';
    el.appendChild(btn);
    document.body.appendChild(el);
    setTimeout(function() { if (el && el.parentNode) el.remove(); }, 5000);
  };
});
})();
