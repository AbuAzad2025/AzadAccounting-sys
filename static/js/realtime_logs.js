/**
 * ═══════════════════════════════════════════════════════════════════
 * 📋 Real-time Logs Viewer مع Filters
 * ═══════════════════════════════════════════════════════════════════
 */

(function() {
  if (window.__REALTIME_LOGS_INIT__) return;
  window.__REALTIME_LOGS_INIT__ = true;
  'use strict';
  
  let logsAutoRefresh = null;
  const REFRESH_INTERVAL = 5000; // 5 ثوان
  
  /**
   * تهيئة Real-time Logs
   */
  function initRealtimeLogs() {
    const logsContainer = document.getElementById('logsContainer');
    if (!logsContainer) return;
    
    // إضافة Filters
    addLogFilters();
    
    // إضافة Auto-refresh toggle
    addAutoRefreshToggle();
    
    // إضافة Export button
    addExportButton();
    
    addClearButton();
  }
  
  /**
   * إضافة Filters
   */
  function addLogFilters() {
    const container = document.querySelector('[data-logs-filters]');
    if (!container) return;
    
    const filtersHTML = `
      <div class="card mb-3">
        <div class="card-body">
          <div class="row g-2">
            <div class="col-md-3">
              <label class="form-label">المستوى:</label>
              <select class="form-select form-select-sm" id="logLevelFilter">
                <option value="">الكل</option>
                <option value="ERROR">ERROR</option>
                <option value="WARNING">WARNING</option>
                <option value="INFO">INFO</option>
                <option value="DEBUG">DEBUG</option>
              </select>
            </div>
            <div class="col-md-3">
              <label class="form-label">التاريخ:</label>
              <input type="date" class="form-control form-control-sm" id="logDateFilter">
            </div>
            <div class="col-md-4">
              <label class="form-label">بحث:</label>
              <input type="text" class="form-control form-control-sm" id="logSearchFilter" 
                     placeholder="ابحث في اللوجات...">
            </div>
            <div class="col-md-2">
              <label class="form-label">&nbsp;</label>
              <button class="btn btn-sm btn-outline-secondary w-100" onclick="clearLogFilters()">
                <i class="fas fa-times"></i> مسح
              </button>
            </div>
          </div>
        </div>
      </div>
    `;
    
    container.innerHTML = filtersHTML;
    
    // تطبيق الفلاتر عند التغيير
    document.getElementById('logLevelFilter').addEventListener('change', filterLogs);
    document.getElementById('logDateFilter').addEventListener('change', filterLogs);
    document.getElementById('logSearchFilter').addEventListener('input', filterLogs);
  }
  
  /**
   * تطبيق الفلاتر
   */
  function filterLogs() {
    const level = document.getElementById('logLevelFilter')?.value.toLowerCase();
    const date = document.getElementById('logDateFilter')?.value;
    const search = document.getElementById('logSearchFilter')?.value.toLowerCase();
    
    const logItems = document.querySelectorAll('.log-entry');
    let visibleCount = 0;
    
    logItems.forEach(item => {
      const itemLevel = item.dataset.level?.toLowerCase() || '';
      const itemDate = item.dataset.date || '';
      const itemText = item.textContent.toLowerCase();
      
      let show = true;
      
      // فلتر المستوى
      if (level && !itemLevel.includes(level)) show = false;
      
      // فلتر التاريخ
      if (date && !itemDate.startsWith(date)) show = false;
      
      // فلتر البحث
      if (search && !itemText.includes(search)) show = false;
      
      item.style.display = show ? '' : 'none';
      if (show) visibleCount++;
    });
    
    // عرض عدد النتائج
    updateResultsCount(visibleCount, logItems.length);
  }
  
  /**
   * مسح الفلاتر
   */
  window.clearLogFilters = function() {
    document.getElementById('logLevelFilter').value = '';
    document.getElementById('logDateFilter').value = '';
    document.getElementById('logSearchFilter').value = '';
    filterLogs();
  };
  
  /**
   * تحديث عدد النتائج
   */
  function updateResultsCount(visible, total) {
    let counter = document.getElementById('logResultsCounter');
    if (!counter) {
      counter = document.createElement('div');
      counter.id = 'logResultsCounter';
      counter.className = 'alert alert-info';
      document.querySelector('[data-logs-filters]')?.appendChild(counter);
    }
    
    counter.innerHTML = `
      <i class="fas fa-info-circle"></i>
      عرض <strong>${visible}</strong> من <strong>${total}</strong> سجل
    `;
    
    counter.style.display = visible !== total ? '' : 'none';
  }
  
  /**
   * Auto-refresh
   */
  function addAutoRefreshToggle() {
    const container = document.querySelector('[data-logs-actions]');
    if (!container) return;
    
    const toggle = document.createElement('div');
    toggle.className = 'form-check form-switch d-inline-block me-3';
    toggle.innerHTML = `
      <input class="form-check-input" type="checkbox" id="autoRefreshLogs">
      <label class="form-check-label" for="autoRefreshLogs">
        <i class="fas fa-sync"></i> تحديث تلقائي (5 ثانية)
      </label>
    `;
    
    container.appendChild(toggle);
    
    document.getElementById('autoRefreshLogs').addEventListener('change', function() {
      if (this.checked) {
        startAutoRefresh();
      } else {
        stopAutoRefresh();
      }
    });
  }
  
  /**
   * بدء التحديث التلقائي
   */
  function startAutoRefresh() {
    stopAutoRefresh(); // إيقاف أي refresh سابق
    
    logsAutoRefresh = setInterval(() => {
      refreshLogs();
    }, REFRESH_INTERVAL);
  }
  
  /**
   * إيقاف التحديث التلقائي
   */
  function stopAutoRefresh() {
    if (logsAutoRefresh) {
      clearInterval(logsAutoRefresh);
      logsAutoRefresh = null;
    }
  }
  
  /**
   * تحديث اللوجات
   */
  function refreshLogs() {
    // reload الصفحة أو استخدام AJAX
    window.location.reload();
  }
  
  /**
   * Export Logs
   */
  function addExportButton() {
    const container = document.querySelector('[data-logs-actions]');
    if (!container) return;
    
    const btn = document.createElement('button');
    btn.className = 'btn btn-sm btn-outline-primary me-2';
    btn.innerHTML = '<i class="fas fa-download"></i> تصدير';
    btn.onclick = exportLogs;
    
    container.appendChild(btn);
  }
  
  /**
   * تصدير اللوجات
   */
  function exportLogs() {
    const logs = [];
    document.querySelectorAll('.log-entry:not([style*="display: none"])').forEach(item => {
      logs.push({
        level: item.dataset.level,
        date: item.dataset.date,
        message: item.textContent.trim()
      });
    });
    
    // تصدير كـ JSON
    const dataStr = JSON.stringify(logs, null, 2);
    const dataBlob = new Blob([dataStr], {type: 'application/json'});
    
    const link = document.createElement('a');
    link.href = URL.createObjectURL(dataBlob);
    link.download = `logs_${new Date().toISOString().split('T')[0]}.json`;
    link.click();
  }
  
  /**
   * Clear Logs
   */
  function addClearButton() {
    const container = document.querySelector('[data-logs-actions]');
    if (!container) return;
    
    const btn = document.createElement('button');
    btn.className = 'btn btn-sm btn-outline-danger';
    btn.innerHTML = '<i class="fas fa-trash"></i> مسح';
    btn.onclick = () => {
      if (confirmDangerousAction('سيتم مسح جميع اللوجات المعروضة', clearDisplayedLogs)) {
        clearDisplayedLogs();
      }
    };
    
    container.appendChild(btn);
  }
  
  /**
   * مسح اللوجات المعروضة
   */
  function clearDisplayedLogs() {
    const logsContainer = document.getElementById('logsContainer');
    if (logsContainer) {
      logsContainer.innerHTML = '<div class="alert alert-info">تم مسح اللوجات</div>';
    }
  }
  
  // التهيئة
  document.addEventListener('DOMContentLoaded', initRealtimeLogs);
  
  // إيقاف auto-refresh عند مغادرة الصفحة
  window.addEventListener('beforeunload', stopAutoRefresh);
  
})();

