// Micro-interactions and subtle scroll effects
document.addEventListener('DOMContentLoaded', () => {
  const observerOptions = {
    threshold: 0.1
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('opacity-100', 'translate-y-0');
        entry.target.classList.remove('opacity-0', 'translate-y-8');
      }
    });
  }, observerOptions);

  document.querySelectorAll('section > div').forEach((el) => {
    el.classList.add('transition-all', 'duration-1000', 'opacity-0', 'translate-y-8');
    observer.observe(el);
  });
});
