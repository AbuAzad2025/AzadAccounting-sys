(function() {
  if (window.__UX_ENHANCEMENTS_INIT__) return;
  window.__UX_ENHANCEMENTS_INIT__ = true;
  'use strict';

  // --- Lightweight Progress Loader (NProgress alternative) ---
  const ProgressLoader = {
    settings: {
      minimum: 0.08,
      easing: 'ease',
      speed: 200,
      trickle: true,
      trickleRate: 0.02,
      trickleSpeed: 800,
      parent: 'body',
    },
    status: null,
    
    init() {
      // Check if real NProgress exists
      if (typeof NProgress !== 'undefined') {
        this.lib = NProgress;
        this.lib.configure({ showSpinner: false });
        return;
      }
      // Otherwise use internal logic (simplified)
      this.lib = null;
    },
    
    start() {
      if (this.lib) return this.lib.start();
      if (!this.status) this.set(0);
      
      const work = () => {
        setTimeout(() => {
          if (!this.status) return;
          this.trickle();
          work();
        }, this.settings.trickleSpeed);
      };
      if (this.settings.trickle) work();
    },
    
    done(force) {
      if (this.lib) return this.lib.done(force);
      if (!force && !this.status) return;
      this.inc(0.3 + 0.5 * Math.random());
      this.set(1);
    },
    
    set(n) {
      if (this.lib) return this.lib.set(n);
      
      n = this.clamp(n, this.settings.minimum, 1);
      this.status = (n === 1 ? null : n);
      
      let progress = document.getElementById('gm-progress');
      if (!progress) {
        progress = document.createElement('div');
        progress.id = 'gm-progress';
        progress.innerHTML = '<div class="bar" role="bar"><div class="peg"></div></div>';
        document.body.appendChild(progress);
        
        // Basic Styles for internal loader
        const style = document.createElement('style');
        style.innerHTML = `
          #gm-progress { pointer-events: none; position: fixed; z-index: 1031; top: 0; left: 0; width: 100%; height: 3px; }
          #gm-progress .bar { background: var(--primary-cyan, #06b6d4); width: 100%; height: 100%; transform: translate3d(-100%,0,0); transition: all 200ms ease; }
          #gm-progress .peg { display: block; position: absolute; right: 0px; width: 100px; height: 100%; box-shadow: 0 0 10px var(--primary-cyan, #06b6d4), 0 0 5px var(--primary-cyan, #06b6d4); opacity: 1.0; transform: rotate(3deg) translate(0px, -4px); }
        `;
        document.head.appendChild(style);
      }
      
      const bar = progress.querySelector('.bar');
      const percentage = ((-1 + n) * 100);
      bar.style.transform = 'translate3d(' + percentage + '%,0,0)';
      
      if (n === 1) {
        setTimeout(() => {
          if (progress) progress.style.opacity = '0';
          setTimeout(() => {
            if (progress) {
              progress.remove();
              this.status = null;
            }
          }, 200);
        }, 200);
      }
    },
    
    inc(amount) {
      if (this.lib) return this.lib.inc(amount);
      let n = this.status;
      if (!n) return this.start();
      if (n > 1) return;
      if (typeof amount !== 'number') {
        if (n >= 0 && n < 0.2) amount = 0.1;
        else if (n >= 0.2 && n < 0.5) amount = 0.04;
        else if (n >= 0.5 && n < 0.8) amount = 0.02;
        else if (n >= 0.8 && n < 0.99) amount = 0.005;
        else amount = 0;
      }
      n = this.clamp(n + amount, 0, 0.994);
      return this.set(n);
    },
    
    trickle() {
      return this.inc(Math.random() * this.settings.trickleRate);
    },
    
    clamp(n, min, max) {
      if (n < min) return min;
      if (n > max) return max;
      return n;
    }
  };

  const UXEnhancements = {
    init() {
      ProgressLoader.init();
      this.initTooltips();
      this.initToasts();
      this.initQuickActionsFAB();
      this.initPasswordStrength();
      this.initLoadingStates();
      this.initMobileNav();
      this.initGlobalNavigation();
      
      // Bind global loader
      window.startLoader = () => ProgressLoader.start();
      window.stopLoader = () => ProgressLoader.done();
    },

    initTooltips() {
      if (typeof $ !== 'undefined' && $.fn.tooltip) {
        $('[data-toggle="tooltip"], [title]').tooltip();
      }
    },

    // --- Toast Notification System ---
    showToast(message, type = 'info', duration = 3000) {
      let container = document.querySelector('.gm-toast-container');
      if (!container) {
        container = document.createElement('div');
        container.className = 'gm-toast-container';
        document.body.appendChild(container);
      }
      
      const toast = document.createElement('div');
      toast.className = `gm-toast ${type}`;
      
      let icon = 'info-circle';
      if (type === 'success') icon = 'check-circle';
      if (type === 'error') icon = 'exclamation-circle';
      if (type === 'warning') icon = 'exclamation-triangle';
      
      toast.innerHTML = `
        <i class="fas fa-${icon} gm-toast-icon"></i>
        <div class="gm-toast-message">${message}</div>
      `;
      
      container.appendChild(toast);
      
      // Animate in
      requestAnimationFrame(() => {
        toast.classList.add('show');
      });
      
      // Auto dismiss
      if (duration > 0) {
        setTimeout(() => {
          toast.classList.remove('show');
          setTimeout(() => toast.remove(), 300);
        }, duration);
      }
      
      return toast;
    },

    initToasts() {
      window.showToast = this.showToast.bind(this);
      
      // Hijack Flask Flashed messages if possible (optional enhancement)
      // This would require parsing existing alerts on page load
      const alerts = document.querySelectorAll('.alert-dismissible');
      alerts.forEach(alert => {
        if (alert.classList.contains('alert-success')) this.showToast(alert.innerText.trim(), 'success');
        if (alert.classList.contains('alert-danger')) this.showToast(alert.innerText.trim(), 'error');
        if (alert.classList.contains('alert-warning')) this.showToast(alert.innerText.trim(), 'warning');
        if (alert.classList.contains('alert-info')) this.showToast(alert.innerText.trim(), 'info');
        // Optionally hide the original alert? alert.style.display = 'none';
      });
    },

    initQuickActionsFAB() {
      // Existing FAB logic... (preserved but simplified check)
      if (document.querySelector('.quick-actions-fab')) return;
      
      const fabHTML = `
        <div class="quick-actions-fab">
          <button class="fab-trigger" onclick="UXEnhancements.toggleFAB()" aria-label="Quick Actions">
            <i class="fas fa-plus"></i>
          </button>
          <div class="fab-menu" id="fabMenu">
            ${this.getFABMenuItems()}
          </div>
        </div>
      `;
      // Only add if not strictly mobile mode or controlled by settings
      // document.body.insertAdjacentHTML('beforeend', fabHTML);
    },

    getFABMenuItems() {
      return [
        '<a href="/customers/create"><i class="fas fa-user-plus"></i> عميل جديد</a>',
        '<a href="/sales/new"><i class="fas fa-shopping-cart"></i> فاتورة جديدة</a>',
        '<a href="/service/new"><i class="fas fa-wrench"></i> طلب صيانة</a>'
      ].join('');
    },

    toggleFAB() {
      const menu = document.getElementById('fabMenu');
      if (menu) menu.classList.toggle('active');
    },

    initPasswordStrength() {
      // Existing logic preserved...
      const passwordInputs = document.querySelectorAll('input[type="password"][name="password"]');
      passwordInputs.forEach(input => {
        if (input.closest('form[action*="login"]')) return;
        if (input.nextElementSibling && input.nextElementSibling.classList.contains('password-strength')) return;
        
        const strengthDiv = document.createElement('div');
        strengthDiv.className = 'password-strength';
        strengthDiv.innerHTML = '<div class="strength-bar weak"></div><small class="text-muted">ضعيف</small>';
        input.parentElement.appendChild(strengthDiv);
        
        input.addEventListener('input', (e) => {
          const val = e.target.value;
          const s = this.calculatePasswordStrength(val);
          const bar = strengthDiv.querySelector('.strength-bar');
          const text = strengthDiv.querySelector('small');
          bar.className = `strength-bar ${s.class}`;
          text.textContent = s.text;
          text.className = `text-${s.color}`;
        });
      });
    },

    calculatePasswordStrength(password) {
      let score = 0;
      if (password.length >= 8) score++;
      if (password.length >= 12) score++;
      if (/[a-z]/.test(password)) score++;
      if (/[A-Z]/.test(password)) score++;
      if (/[0-9]/.test(password)) score++;
      if (/[^a-zA-Z0-9]/.test(password)) score++;
      
      if (score <= 2) return { class: 'weak', text: 'ضعيف', color: 'danger' };
      if (score <= 4) return { class: 'medium', text: 'متوسط', color: 'warning' };
      return { class: 'strong', text: 'قوي', color: 'success' };
    },

    initLoadingStates() {
      // Global Form Submit Handler
      document.addEventListener('submit', function(e) {
        const form = e.target;
        if (!form || form.getAttribute('data-no-loading') === 'true') return;
        
        // Skip if form is invalid (browser validation)
        if (form.checkValidity && !form.checkValidity()) return;
        
        const btn = form.querySelector('button[type="submit"]:not(.no-loading)');
        if (btn) {
            // Check if already loading
            if (btn.classList.contains('loading')) {
                e.preventDefault();
                return;
            }
            
            // Add loading state
            const originalText = btn.innerHTML;
            btn.setAttribute('data-original-text', originalText);
            btn.classList.add('loading');
            
            if (!btn.querySelector('.btn-spinner')) {
                const spinner = document.createElement('span');
                spinner.className = 'btn-spinner';
                spinner.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
                btn.appendChild(spinner);
            }
            
            // Safety timeout: remove loading after 15s if page doesn't reload
            setTimeout(() => {
                btn.classList.remove('loading');
            }, 15000);
        }
        
        ProgressLoader.start();
      }, true); // Use capture to catch it early
    },

    initGlobalNavigation() {
      // Handle Link Clicks for Progress Bar
      document.addEventListener('click', function(e) {
        const link = e.target.closest('a');
        if (!link) return;
        
        const href = link.getAttribute('href');
        
        // Ignore specific links
        if (!href || 
            href.startsWith('#') || 
            href.startsWith('javascript:') || 
            href.startsWith('mailto:') ||
            href.startsWith('tel:') ||
            link.getAttribute('target') === '_blank' ||
            link.classList.contains('no-nprogress') ||
            e.ctrlKey || e.metaKey || e.shiftKey
        ) return;

        // Start loader
        ProgressLoader.start();
      });

      // Handle Browser Back/Forward
      window.addEventListener('popstate', () => {
        ProgressLoader.start();
      });
      
      // Stop loader when page loads (if using AJAX navigation or just in case)
      window.addEventListener('load', () => {
        ProgressLoader.done();
      });
      
      // Stop loader if page is shown from bfcache
      window.addEventListener('pageshow', (e) => {
        if (e.persisted) {
            ProgressLoader.done(true);
            // Restore buttons
            document.querySelectorAll('.btn.loading').forEach(btn => btn.classList.remove('loading'));
        }
      });
    },

    initMobileNav() {
      // Placeholder for mobile nav logic if needed
    },

    showLoading() {
      if (!document.querySelector('.loading-overlay')) {
        const overlay = document.createElement('div');
        overlay.className = 'loading-overlay';
        overlay.innerHTML = '<div class="loading-spinner"></div>';
        document.body.appendChild(overlay);
        requestAnimationFrame(() => overlay.classList.add('active'));
      }
    },

    hideLoading() {
      const overlay = document.querySelector('.loading-overlay');
      if (overlay) {
        overlay.classList.remove('active');
        setTimeout(() => overlay.remove(), 300);
      }
    }
  };

  // Expose Global API
  window.UXEnhancements = UXEnhancements;
  window.showToast = UXEnhancements.showToast.bind(UXEnhancements);
  window.showLoading = UXEnhancements.showLoading.bind(UXEnhancements);
  window.hideLoading = UXEnhancements.hideLoading.bind(UXEnhancements);

  // Auto Init
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => UXEnhancements.init());
  } else {
    UXEnhancements.init();
  }

})();
