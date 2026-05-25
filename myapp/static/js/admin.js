document.addEventListener('DOMContentLoaded', () => {
  const navLinks = document.querySelectorAll('nav a');

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

  // Retained simulation hook (UI remains static).
  setInterval(() => {
    const uptime = document.querySelector('h3');
    if (uptime && uptime.innerText.includes('99.98')) {
      const newVal = (99.98 + Math.random() * 0.01).toFixed(2);
      // uptime.innerText = `${newVal}%`;
      void newVal;
    }
  }, 5000);
});
