function getCSRFToken() {
    return document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') 
        || document.getElementById('csrf_token')?.value 
        || '';
}

(function() {
    if (window.__CSRF_UTILS_INIT__) return;
    window.__CSRF_UTILS_INIT__ = true;

function setupGlobalCSRF() {
    const originalFetch = window.fetch;
    window.fetch = function(url, options = {}) {
        if (typeof url === 'string' && url.startsWith('/')) {
            options.headers = options.headers || {};
            if (options.method && ['POST', 'PUT', 'DELETE', 'PATCH'].includes(options.method.toUpperCase())) {
                if (!options.headers['X-CSRFToken'] && !options.headers['X-CSRF-Token']) {
                    const token = getCSRFToken();
                    if (token) {
                        options.headers['X-CSRFToken'] = token;
                    }
                }
            }
        }
        return originalFetch(url, options);
    };
}

if (typeof document !== 'undefined') {
    setupGlobalCSRF();
}
})();

