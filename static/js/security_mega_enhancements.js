/**
 * ═══════════════════════════════════════════════════════════════════
 * 🚀 Security Module - Mega Enhancements
 * ═══════════════════════════════════════════════════════════════════
 * 
 * يحتوي على جميع التحسينات المتبقية:
 * - Tab Memory
 * - Favorites/Bookmarks
 * - Quick Actions Menu (Ctrl+Space)
 * - Notification Center
 * - Settings Search
 * - وأكثر...
 */

(function() {
  'use strict';
  
  // ═══════════════════════════════════════════════════════════════════
  // 📌 Tab Memory - حفظ التبويب الأخير
  // ═══════════════════════════════════════════════════════════════════
  
  function initTabMemory() {
    const TAB_MEMORY_KEY = 'security_tab_memory';
    
    // حفظ التبويب الحالي
    const currentPath = window.location.pathname;
    const currentTab = new URLSearchParams(window.location.search).get('tab');
    
    if (currentPath.startsWith('/security/') && currentTab) {
      const memory = JSON.parse(localStorage.getItem(TAB_MEMORY_KEY) || '{}');
      memory[currentPath] = currentTab;
      localStorage.setItem(TAB_MEMORY_KEY, JSON.stringify(memory));
    }
    
    // استعادة التبويب عند العودة
    document.querySelectorAll('a[href*="/security/"]').forEach(link => {
      const url = new URL(link.href, window.location.origin);
      const path = url.pathname;
      const memory = JSON.parse(localStorage.getItem(TAB_MEMORY_KEY) || '{}');
      
      if (memory[path] && !url.searchParams.has('tab')) {
        url.searchParams.set('tab', memory[path]);
        link.href = url.toString();
      }
    });
  }
  
  // ═══════════════════════════════════════════════════════════════════
  // ⭐ Favorites/Bookmarks
  // ═══════════════════════════════════════════════════════════════════
  
  function initFavorites() {
    const FAVORITES_KEY = 'security_favorites';
    
    // إضافة زر المفضلة في كل صفحة
    if (window.location.pathname.startsWith('/security/')) {
      addFavoriteButton();
    }
    
    // إضافة قائمة المفضلة في الصفحة الرئيسية
    if (window.location.pathname === '/security/' || window.location.pathname === '/security') {
      showFavoritesWidget();
    }
  }
  
  function addFavoriteButton() {
    const nav = document.querySelector('.mb-3.d-flex');
    if (!nav) return;
    
    const currentPage = {
      url: window.location.pathname + window.location.search,
      title: document.title,
      timestamp: new Date().toISOString()
    };
    
    const favorites = JSON.parse(localStorage.getItem('security_favorites') || '[]');
    const isFavorite = favorites.some(f => f.url === currentPage.url);
    
    const btn = document.createElement('button');
    updateFavoriteButton(btn, isFavorite);
    btn.onclick = () => toggleFavorite(currentPage, btn);
    
    nav.querySelector('div').appendChild(btn);
  }

  function updateFavoriteButton(btn, isFavorite) {
    btn.className = `btn btn-sm ${isFavorite ? 'btn-warning' : 'btn-outline-warning'}`;
    btn.textContent = '';
    const icon = document.createElement('i');
    icon.className = 'fas fa-star';
    btn.appendChild(icon);
    btn.appendChild(document.createTextNode(' ' + (isFavorite ? 'مفضل' : 'إضافة للمفضلة')));
  }
  
  function toggleFavorite(page, btn) {
    let favorites = JSON.parse(localStorage.getItem('security_favorites') || '[]');
    const index = favorites.findIndex(f => f.url === page.url);
    
    if (index >= 0) {
      favorites.splice(index, 1);
      updateFavoriteButton(btn, false);
    } else {
      favorites.push(page);
      updateFavoriteButton(btn, true);
    }
    
    localStorage.setItem('security_favorites', JSON.stringify(favorites));
  }
  
  function showFavoritesWidget() {
    const favorites = JSON.parse(localStorage.getItem('security_favorites') || '[]');
    if (favorites.length === 0) return;
    
    const widget = document.createElement('div');
    widget.className = 'card border-warning mb-4';
    const header = document.createElement('div');
    header.className = 'card-header bg-warning text-dark';
    const h6 = document.createElement('h6');
    h6.className = 'mb-0';
    const star = document.createElement('i');
    star.className = 'fas fa-star';
    h6.appendChild(star);
    h6.appendChild(document.createTextNode(' المفضلة (' + favorites.length + ')'));
    header.appendChild(h6);
    widget.appendChild(header);

    const body = document.createElement('div');
    body.className = 'card-body';
    const listGroup = document.createElement('div');
    listGroup.className = 'list-group';

    favorites.slice(0, 5).forEach(fav => {
      const a = document.createElement('a');
      a.className = 'list-group-item list-group-item-action';
      a.href = String(fav?.url || '#');
      const row = document.createElement('div');
      row.className = 'd-flex justify-content-between';

      const left = document.createElement('span');
      const bm = document.createElement('i');
      bm.className = 'fas fa-bookmark text-warning';
      left.appendChild(bm);
      const t = String(fav?.title || '').replace(' - وحدة الأمان المتقدمة', '');
      left.appendChild(document.createTextNode(' ' + t));

      const right = document.createElement('small');
      right.className = 'text-muted';
      const ts = fav?.timestamp ? new Date(fav.timestamp) : null;
      right.textContent = ts && !Number.isNaN(ts.getTime()) ? ts.toLocaleDateString('ar-EG') : '';

      row.appendChild(left);
      row.appendChild(right);
      a.appendChild(row);
      listGroup.appendChild(a);
    });

    body.appendChild(listGroup);
    if (favorites.length > 5) {
      const more = document.createElement('small');
      more.className = 'text-muted d-block mt-2';
      more.textContent = '... و ' + (favorites.length - 5) + ' أخرى';
      body.appendChild(more);
    }
    widget.appendChild(body);
    
    // إضافة في أول container-fluid
    const container = document.querySelector('.container-fluid');
    if (!container) return;
    const firstAlert = container.querySelector('.alert');
    container.insertBefore(widget, firstAlert);
  }
  
  // ═══════════════════════════════════════════════════════════════════
  // ⚡ Quick Actions Menu (Ctrl+Space)
  // ═══════════════════════════════════════════════════════════════════
  
  function initQuickActions() {
    document.addEventListener('keydown', function(e) {
      if (e.ctrlKey && e.key === ' ') {
        e.preventDefault();
        showQuickActionsMenu();
      }
    });
  }
  
  function showQuickActionsMenu() {
    // قائمة الإجراءات السريعة
    const actions = [
      {icon: '🗄️', name: 'Database Manager', url: '/security/database-manager', shortcut: 'Ctrl+Shift+D'},
      {icon: '🤖', name: 'AI Hub', url: '/security/ai-hub', shortcut: 'Ctrl+Shift+A'},
      {icon: '🛡️', name: 'Security Center', url: '/security/security-center', shortcut: 'Ctrl+Shift+S'},
      {icon: '👥', name: 'Users Center', url: '/security/users-center', shortcut: 'Ctrl+Shift+U'},
      {icon: '🔧', name: 'Tools Center', url: '/security/tools-center', shortcut: 'Ctrl+Shift+T'},
      {icon: '📊', name: 'Reports Center', url: '/security/reports-center', shortcut: 'Ctrl+Shift+R'},
      {icon: '⚙️', name: 'Settings Center', url: '/security/settings-center', shortcut: 'Ctrl+Shift+G'},
      {icon: '📒', name: 'Ledger Control', url: '/security/ledger-control/', shortcut: 'Ctrl+Shift+L'},
      {icon: '🔌', name: 'Integrations', url: '/security/integrations', shortcut: 'Ctrl+Shift+I'},
      {icon: '🚨', name: 'Emergency Tools', url: '/security/emergency-tools', shortcut: 'Ctrl+Shift+E'},
      {icon: '❓', name: 'Help', url: '/security/help', shortcut: 'Ctrl+Shift+H'},
      {icon: '🗺️', name: 'Sitemap', url: '/security/sitemap', shortcut: ''},
    ];
    
    const modal = document.createElement('div');
    modal.className = 'quick-actions-modal';
    const panel = document.createElement('div');
    panel.style.cssText = [
      'position: fixed',
      'top: 50%',
      'left: 50%',
      'transform: translate(-50%, -50%)',
      'background: white',
      'border-radius: 15px',
      'padding: 25px',
      'max-width: 600px',
      'width: 90%',
      'box-shadow: 0 20px 60px rgba(0,0,0,0.3)',
      'z-index: 99999'
    ].join(';');

    const head = document.createElement('div');
    head.className = 'text-center mb-3';
    const title = document.createElement('h4');
    const bolt = document.createElement('i');
    bolt.className = 'fas fa-bolt text-warning';
    title.appendChild(bolt);
    title.appendChild(document.createTextNode(' إجراءات سريعة'));
    head.appendChild(title);
    const input = document.createElement('input');
    input.type = 'text';
    input.id = 'quickActionsSearch';
    input.className = 'form-control mt-2';
    input.placeholder = '🔍 ابحث عن إجراء...';
    input.autofocus = true;
    head.appendChild(input);

    const list = document.createElement('div');
    list.id = 'quickActionsList';
    list.style.cssText = 'max-height: 400px; overflow-y: auto;';
    actions.forEach((action, index) => {
      const item = document.createElement('div');
      item.className = 'quick-action-item p-2 rounded mb-1';
      item.style.cssText = 'cursor: pointer; transition: all 0.2s;';
      item.dataset.name = String(action.name || '').toLowerCase();
      item.dataset.index = String(index);
      item.addEventListener('mouseenter', () => { item.style.background = '#f0f0f0'; });
      item.addEventListener('mouseleave', () => { item.style.background = ''; });
      item.addEventListener('click', () => {
        window.location.href = action.url;
        modal.remove();
      });

      const row = document.createElement('div');
      row.className = 'd-flex justify-content-between align-items-center';
      const left = document.createElement('div');
      const icon = document.createElement('span');
      icon.style.fontSize = '1.5rem';
      icon.textContent = action.icon;
      const name = document.createElement('strong');
      name.className = 'ms-2';
      name.textContent = action.name;
      left.appendChild(icon);
      left.appendChild(name);
      row.appendChild(left);
      if (action.shortcut) {
        const kbd = document.createElement('kbd');
        kbd.style.fontSize = '0.75rem';
        kbd.textContent = action.shortcut;
        row.appendChild(kbd);
      }
      item.appendChild(row);
      list.appendChild(item);
    });

    const foot = document.createElement('div');
    foot.className = 'text-center mt-3';
    const hint = document.createElement('small');
    hint.className = 'text-muted';
    hint.appendChild(document.createTextNode('↑↓ التنقل | Enter اختيار | Esc إغلاق'));
    foot.appendChild(hint);

    panel.appendChild(head);
    panel.appendChild(list);
    panel.appendChild(foot);
    modal.appendChild(panel);
    
    modal.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(0,0,0,0.5);
      z-index: 99998;
    `;
    
    modal.onclick = (e) => {
      if (e.target === modal) modal.remove();
    };
    
    document.body.appendChild(modal);
    
    // البحث في الإجراءات
    const searchInput = document.getElementById('quickActionsSearch');
    searchInput.addEventListener('input', function() {
      const query = this.value.toLowerCase();
      document.querySelectorAll('.quick-action-item').forEach(item => {
        const name = item.dataset.name;
        item.style.display = name.includes(query) ? '' : 'none';
      });
    });
    
    // التنقل بالأسهم
    let selectedIndex = 0;
    document.addEventListener('keydown', function handler(e) {
      const items = Array.from(document.querySelectorAll('.quick-action-item:not([style*="display: none"])'));
      
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        selectedIndex = Math.min(selectedIndex + 1, items.length - 1);
        highlightItem(items, selectedIndex);
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        selectedIndex = Math.max(selectedIndex - 1, 0);
        highlightItem(items, selectedIndex);
      } else if (e.key === 'Enter') {
        e.preventDefault();
        items[selectedIndex]?.click();
      } else if (e.key === 'Escape') {
        modal.remove();
        document.removeEventListener('keydown', handler);
      }
    });
    
    function highlightItem(items, index) {
      items.forEach((item, i) => {
        item.style.background = i === index ? '#667eea' : '';
        item.style.color = i === index ? 'white' : '';
      });
    }
  }
  
  // ═══════════════════════════════════════════════════════════════════
  // 🔔 Notification Center موحد
  // ═══════════════════════════════════════════════════════════════════
  
  function initNotificationCenter() {
    addNotificationBell();
  }
  
  function addNotificationBell() {
    const nav = document.querySelector('.mb-3.d-flex');
    if (!nav) return;
    
    const notifications = getNotifications();
    const unreadCount = notifications.filter(n => !n.read).length;
    
    const bell = document.createElement('button');
    bell.className = 'btn btn-sm btn-outline-primary position-relative';
    const icon = document.createElement('i');
    icon.className = 'fas fa-bell';
    bell.appendChild(icon);
    if (unreadCount > 0) {
      const badge = document.createElement('span');
      badge.className = 'position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger';
      badge.textContent = String(unreadCount);
      bell.appendChild(badge);
    }
    bell.onclick = showNotificationCenter;
    
    nav.querySelector('div').appendChild(bell);
  }
  
  function getNotifications() {
    // محاكاة - في الإنتاج تُجلب من API
    return JSON.parse(localStorage.getItem('security_notifications') || '[]');
  }
  
  function showNotificationCenter() {
    const notifications = getNotifications();
    
    const modal = document.createElement('div');
    modal.className = 'notification-center-modal';
    const panel = document.createElement('div');
    panel.style.cssText = [
      'position: fixed',
      'top: 70px',
      'left: 50%',
      'transform: translateX(-50%)',
      'background: white',
      'border-radius: 10px',
      'padding: 20px',
      'max-width: 500px',
      'width: 90%',
      'max-height: 500px',
      'overflow-y: auto',
      'box-shadow: 0 10px 40px rgba(0,0,0,0.3)',
      'z-index: 99999'
    ].join(';');

    const header = document.createElement('div');
    header.className = 'd-flex justify-content-between align-items-center mb-3';
    const h5 = document.createElement('h5');
    h5.className = 'mb-0';
    const bell = document.createElement('i');
    bell.className = 'fas fa-bell';
    h5.appendChild(bell);
    h5.appendChild(document.createTextNode(' الإشعارات'));
    header.appendChild(h5);

    const headerActions = document.createElement('div');
    const readAll = document.createElement('button');
    readAll.className = 'btn btn-sm btn-outline-secondary me-2';
    const chk = document.createElement('i');
    chk.className = 'fas fa-check';
    readAll.appendChild(chk);
    readAll.appendChild(document.createTextNode(' تحديد الكل كمقروء'));
    readAll.addEventListener('click', () => {
      if (typeof window.markAllAsRead === 'function') window.markAllAsRead();
    });
    const close = document.createElement('button');
    close.type = 'button';
    close.className = 'close';
    close.textContent = '';
    const closeSpan = document.createElement('span');
    closeSpan.setAttribute('aria-hidden', 'true');
    closeSpan.textContent = '×';
    close.appendChild(closeSpan);
    close.addEventListener('click', () => modal.remove());
    headerActions.appendChild(readAll);
    headerActions.appendChild(close);
    header.appendChild(headerActions);

    panel.appendChild(header);

    const allowedTypes = new Set(['primary','secondary','success','danger','warning','info','light','dark']);

    if (!notifications.length) {
      const empty = document.createElement('div');
      empty.className = 'alert alert-info text-center';
      const inbox = document.createElement('i');
      inbox.className = 'fas fa-inbox';
      empty.appendChild(inbox);
      empty.appendChild(document.createElement('br'));
      empty.appendChild(document.createTextNode('لا توجد إشعارات'));
      panel.appendChild(empty);
    } else {
      notifications.forEach(notif => {
        const typeRaw = String(notif?.type || 'info').toLowerCase();
        const type = allowedTypes.has(typeRaw) ? typeRaw : 'info';
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} ${notif?.read ? 'opacity-50' : ''} mb-2`;
        const row = document.createElement('div');
        row.className = 'd-flex justify-content-between';

        const left = document.createElement('div');
        const strong = document.createElement('strong');
        strong.textContent = String(notif?.title || '');
        left.appendChild(strong);
        left.appendChild(document.createElement('br'));
        const msg = document.createElement('small');
        msg.textContent = String(notif?.message || '');
        left.appendChild(msg);
        left.appendChild(document.createElement('br'));
        const ts = document.createElement('small');
        ts.className = 'text-muted';
        const dt = notif?.timestamp ? new Date(notif.timestamp) : null;
        ts.textContent = dt && !Number.isNaN(dt.getTime()) ? dt.toLocaleString('ar-EG') : '';
        left.appendChild(ts);

        row.appendChild(left);
        if (!notif?.read) {
          const b = document.createElement('span');
          b.className = 'badge bg-primary';
          b.textContent = 'جديد';
          row.appendChild(b);
        }
        alert.appendChild(row);
        panel.appendChild(alert);
      });
    }

    modal.appendChild(panel);
    
    modal.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(0,0,0,0.3);
      z-index: 99998;
    `;
    
    modal.onclick = (e) => {
      if (e.target === modal) modal.remove();
    };
    
    document.body.appendChild(modal);
  }
  
  window.markAllAsRead = function() {
    let notifications = getNotifications();
    notifications.forEach(n => n.read = true);
    localStorage.setItem('security_notifications', JSON.stringify(notifications));
    document.querySelector('.notification-center-modal')?.remove();
    location.reload();
  };
  
  // ═══════════════════════════════════════════════════════════════════
  // 🔍 Settings Search
  // ═══════════════════════════════════════════════════════════════════
  
  function initSettingsSearch() {
    // إذا كنا في Settings Center
    if (!window.location.pathname.includes('settings-center')) return;
    
    // إضافة شريط بحث
    const container = document.querySelector('.container-fluid');
    if (!container) return;
    
    const searchBox = document.createElement('div');
    searchBox.className = 'mb-3';
    const inputGroup = document.createElement('div');
    inputGroup.className = 'input-group';
    const prefix = document.createElement('span');
    prefix.className = 'input-group-text bg-primary text-white';
    const searchIcon = document.createElement('i');
    searchIcon.className = 'fas fa-search';
    prefix.appendChild(searchIcon);
    const input = document.createElement('input');
    input.type = 'text';
    input.id = 'settingsSearch';
    input.className = 'form-control';
    input.placeholder = '🔍 ابحث في الإعدادات...';
    inputGroup.appendChild(prefix);
    inputGroup.appendChild(input);
    searchBox.appendChild(inputGroup);
    
    const firstCard = container.querySelector('.card');
    if (firstCard) {
      firstCard.parentNode.insertBefore(searchBox, firstCard);
    }
    
    document.getElementById('settingsSearch')?.addEventListener('input', function() {
      const query = this.value.toLowerCase();
      document.querySelectorAll('.form-group, .card').forEach(item => {
        const text = item.textContent.toLowerCase();
        item.style.display = text.includes(query) || !query ? '' : 'none';
      });
    });
  }
  
  // ═══════════════════════════════════════════════════════════════════
  // 🎯 Recent Pages
  // ═══════════════════════════════════════════════════════════════════
  
  function trackRecentPages() {
    const RECENT_KEY = 'security_recent_pages';
    const currentPage = {
      url: window.location.pathname + window.location.search,
      title: document.title,
      timestamp: new Date().toISOString()
    };
    
    let recent = JSON.parse(localStorage.getItem(RECENT_KEY) || '[]');
    
    // إزالة إذا موجود
    recent = recent.filter(p => p.url !== currentPage.url);
    
    // إضافة في الأول
    recent.unshift(currentPage);
    
    // الاحتفاظ بآخر 10 صفحات
    recent = recent.slice(0, 10);
    
    localStorage.setItem(RECENT_KEY, JSON.stringify(recent));
  }
  
  // ═══════════════════════════════════════════════════════════════════
  // 📊 Enhanced Data Tables
  // ═══════════════════════════════════════════════════════════════════
  
  function enhanceDataTables() {
    const path = (window.location && window.location.pathname) ? window.location.pathname : '';
    const isCustomerStatement = /\/customers\/\d+\/account_statement/.test(path);
    if (isCustomerStatement) {
      document.querySelectorAll('.table-export-btn').forEach(btn => btn.remove());
    }
    
    document.querySelectorAll('table.table').forEach(table => {
      const attrNoExport = (table.getAttribute('data-no-export') === 'true');
      const classNoExport = table.classList.contains('no-export');
      const skipExport = attrNoExport || classNoExport || isCustomerStatement;
      if (!skipExport && !table.querySelector('.table-export-btn')) {
        addTableExportButton(table);
      }
      
      if (!table.querySelector('.column-visibility')) {
        addColumnVisibility(table);
      }
    });
  }
  
  function addTableExportButton(table) {
    const wrapper = table.parentElement;
    if (!wrapper) return;
    const skipExport = (table.getAttribute('data-no-export') === 'true') || table.classList.contains('no-export');
    if (skipExport) return;
    
    const btn = document.createElement('button');
    btn.className = 'btn btn-sm btn-outline-success table-export-btn mb-2';
    btn.classList.add('no-print');
    btn.textContent = '';
    const icon = document.createElement('i');
    icon.className = 'fas fa-file-excel';
    btn.appendChild(icon);
    btn.appendChild(document.createTextNode(' Export CSV'));
    btn.onclick = () => exportTableToCSV(table);
    
    wrapper.insertBefore(btn, table);
  }
  
  function exportTableToCSV(table) {
    let csv = [];
    const rows = table.querySelectorAll('tr');
    
    rows.forEach(row => {
      const cols = row.querySelectorAll('td, th');
      const rowData = Array.from(cols).map(col => {
        return '"' + col.textContent.trim().replace(/"/g, '""') + '"';
      });
      csv.push(rowData.join(','));
    });
    
    const csvContent = csv.join('\n');
    const blob = new Blob(['\ufeff' + csvContent], {type: 'text/csv;charset=utf-8;'});
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `export_${new Date().toISOString().split('T')[0]}.csv`;
    link.click();
  }
  
  function addColumnVisibility(table) {
    // يمكن إضافة لاحقاً
  }
  
  // ═══════════════════════════════════════════════════════════════════
  // 🎨 UI Enhancements
  // ═══════════════════════════════════════════════════════════════════
  
  function initUIEnhancements() {
    // Loading states
    addLoadingStates();
    
    // Copy to clipboard buttons
    addCopyButtons();
    
    // Collapse/Expand all
    addCollapseButtons();
  }
  
  function addLoadingStates() {
    document.querySelectorAll('form').forEach(form => {
      form.addEventListener('submit', function() {
        const submitBtn = this.querySelector('button[type="submit"]');
        if (submitBtn && !submitBtn.dataset.noLoading) {
          submitBtn.disabled = true;
          submitBtn.textContent = '';
          const spinner = document.createElement('span');
          spinner.className = 'spinner-border spinner-border-sm';
          submitBtn.appendChild(spinner);
          submitBtn.appendChild(document.createTextNode(' جاري المعالجة...'));
        }
      });
    });
  }
  
  function addCopyButtons() {
    document.querySelectorAll('pre, code').forEach(element => {
      if (element.textContent.trim().length > 20) {
        const btn = document.createElement('button');
        btn.className = 'btn btn-sm btn-outline-secondary position-absolute top-0 end-0 m-1';
        setCopyButtonIcon(btn, false);
        btn.onclick = () => {
          navigator.clipboard.writeText(element.textContent);
          setCopyButtonIcon(btn, true);
          setTimeout(() => setCopyButtonIcon(btn, false), 2000);
        };
        
        element.style.position = 'relative';
        element.appendChild(btn);
      }
    });
  }

  function setCopyButtonIcon(btn, isCopied) {
    btn.textContent = '';
    const icon = document.createElement('i');
    icon.className = isCopied ? 'fas fa-check text-success' : 'fas fa-copy';
    btn.appendChild(icon);
  }
  
  function addCollapseButtons() {
    // يمكن إضافة لاحقاً للأقسام الكبيرة
  }
  
  // ═══════════════════════════════════════════════════════════════════
  // 🚀 التهيئة الشاملة
  // ═══════════════════════════════════════════════════════════════════
  
  document.addEventListener('DOMContentLoaded', function() {
    // تفعيل جميع الميزات
    initTabMemory();
    initFavorites();
    initQuickActions();
    initNotificationCenter();
    initSettingsSearch();
    trackRecentPages();
    enhanceDataTables();
    initUIEnhancements();
  });
  
})();

