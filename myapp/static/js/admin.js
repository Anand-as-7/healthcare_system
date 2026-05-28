(() => {
  function setupSidebarActiveState() {
    const navLinks = document.querySelectorAll('[data-desktop-nav-link]');

    navLinks.forEach((link) => {
      link.addEventListener('click', function () {
        // Keep desktop sidebar active-link behavior unchanged.
        if (window.innerWidth >= 768) {
          navLinks.forEach((navLink) => {
            navLink.classList.remove(
              'text-primary',
              'dark:text-primary-fixed',
              'font-bold',
              'border-r-4',
              'border-primary',
              'dark:border-primary-fixed',
              'bg-primary/5'
            );
            navLink.classList.add('text-on-surface-variant', 'dark:text-outline');
          });

          this.classList.add(
            'text-primary',
            'dark:text-primary-fixed',
            'font-bold',
            'border-r-4',
            'border-primary',
            'dark:border-primary-fixed',
            'bg-primary/5'
          );
          this.classList.remove('text-on-surface-variant', 'dark:text-outline');
        }
      });
    });
  }

  function setupDashboardSimulation() {
    // Retained simulation hook (UI remains static).
    setInterval(() => {
      const uptime = document.querySelector('h3');
      if (uptime && uptime.innerText.includes('99.98')) {
        const newVal = (99.98 + Math.random() * 0.01).toFixed(2);
        // uptime.innerText = `${newVal}%`;
        void newVal;
      }
    }, 5000);
  }

  function initUsersDataTable() {
    const tables = document.querySelectorAll('table.js-admin-datatable');
    if (!tables.length || !window.jQuery) return false;

    const $ = window.jQuery;
    if (!$.fn || (!$.fn.DataTable && !$.fn.dataTable)) return false;

    tables.forEach((table) => {
      const selector = `#${table.id}`;
      if (!table.id || $.fn.dataTable.isDataTable(selector)) return;

      const entityLabel = table.dataset.entityLabel || 'records';
      const nowrapTargets = (table.dataset.nowrapTargets || '')
        .split(',')
        .map((item) => Number(item.trim()))
        .filter((item) => !Number.isNaN(item));
      const columnWidths = (table.dataset.columnWidths || '')
        .split(',')
        .map((item) => item.trim());
      const thCount = table.querySelectorAll('thead th').length;
      const columns = columnWidths.length
        ? Array.from({ length: thCount }, (_, index) => {
            const width = columnWidths[index];
            return width ? { width } : {};
          })
        : undefined;

      const dt = $(selector).DataTable({
        dom: '<"dt-top-bar mb-3"<"dt-length"l><"dt-search"f>>t<"dt-bottom-bar mt-4"<"dt-info"i><"dt-pagination"p>>',
        scrollX: true,
        pageLength: 10,
        lengthMenu: [[10, 25, 50, -1], [10, 25, 50, 'All']],
        order: [[0, 'desc']],
        autoWidth: false,
        columns,
        columnDefs: nowrapTargets.length ? [{ targets: nowrapTargets, className: 'dt-body-nowrap' }] : [],
        language: {
          search: `Search ${entityLabel}:`,
          lengthMenu: 'Show _MENU_ entries',
          info: `Showing _START_ to _END_ of _TOTAL_ ${entityLabel.toLowerCase()}`,
          paginate: {
            previous: 'Prev',
            next: 'Next'
          }
        }
      });

      dt.columns.adjust();
      window.addEventListener('load', () => dt.columns.adjust());
      $(window).on('resize', () => dt.columns.adjust());
    });

    return true;
  }

  function bootAdminUi() {
    setupSidebarActiveState();
    setupDashboardSimulation();

    // Try immediately, then retry briefly to handle CDN/script timing delays.
    if (!initUsersDataTable()) {
      let attempts = 0;
      const maxAttempts = 20;
      const retryTimer = setInterval(() => {
        attempts += 1;
        if (initUsersDataTable() || attempts >= maxAttempts) {
          clearInterval(retryTimer);
        }
      }, 150);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', bootAdminUi);
  } else {
    bootAdminUi();
  }
})();
