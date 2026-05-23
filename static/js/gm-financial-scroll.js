(function (window) {
  "use strict";
  if (window.GMScrollFilters && typeof window.GMScrollFilters.init === "function") {
    window.GMFinancialScroll = window.GMFinancialScroll || {
      init: function () {
        window.GMScrollFilters.init();
      },
      bind: window.GMScrollFilters.bind,
    };
  }
})(window);
