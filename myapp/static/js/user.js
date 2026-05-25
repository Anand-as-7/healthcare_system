// Micro-interaction for vitals update
setInterval(() => {
  const hrElement = document.querySelector('.text-3xl.font-bold');
  if (hrElement) {
    const current = parseInt(hrElement.innerText);
    const variance = Math.floor(Math.random() * 3) - 1; // -1, 0, or 1
    hrElement.innerText = (current + variance).toString();
  }
}, 3000);

// Simple smooth scroll for nav
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function (e) {
    e.preventDefault();
    document.querySelector(this.getAttribute('href')).scrollIntoView({
      behavior: 'smooth'
    });
  });
});
