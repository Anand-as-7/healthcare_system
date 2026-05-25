// Micro-interaction: Update shift progress randomly for demo effect
const progressBar = document.querySelector('.bg-primary.w-\\[65\\%\\]');
if (progressBar) {
  let progress = 65;
  setInterval(() => {
    progress = Math.min(100, progress + Math.random() * 0.1);
    progressBar.style.width = `${progress}%`;
  }, 5000);
}

// Ripple-like effect on quick action buttons
const buttons = document.querySelectorAll('button');
buttons.forEach((button) => {
  button.addEventListener('mousedown', function () {
    this.style.transform = 'scale(0.97)';
  });
  button.addEventListener('mouseup', function () {
    this.style.transform = 'scale(1)';
  });
});
