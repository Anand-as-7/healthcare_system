// Micro-interactions and subtle effects
document.addEventListener('DOMContentLoaded', () => {
  // Log successful render
  console.log('MedTech Dashboard UI Initialized');

  // Interaction logic for progress ring (simulated update)
  const ring = document.querySelector('.progress-ring');
  if (ring) {
    const radius = ring.r.baseVal.value;
    const circumference = radius * 2 * Math.PI;
    ring.style.strokeDasharray = `${circumference} ${circumference}`;

    // 88% calculation
    const offset = circumference - (88 / 100) * circumference;
    ring.style.strokeDashoffset = offset;
  }

  const dropdownToggle = document.querySelector('.hospital-dropdown-toggle');
  const dropdownMenu = document.querySelector('.hospital-dropdown-menu');
  if (dropdownToggle && dropdownMenu) {
    dropdownToggle.addEventListener('click', () => {
      const isHidden = dropdownMenu.classList.contains('hidden');
      dropdownMenu.classList.toggle('hidden');
      dropdownToggle.setAttribute('aria-expanded', isHidden ? 'true' : 'false');

      const icon = dropdownToggle.querySelector('[data-icon="expand_more"]');
      if (icon) {
        icon.style.transform = isHidden ? 'rotate(180deg)' : 'rotate(0deg)';
      }
    });
  }
});
