// Florin Management — shared behavior
document.addEventListener('DOMContentLoaded', () => {
  const io = new IntersectionObserver((entries) => {
    entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
  }, { threshold: 0.12 });
  document.querySelectorAll('.rv').forEach(el => io.observe(el));

  const burger = document.querySelector('.burger');
  const menu = document.querySelector('.mobile-menu');
  if (burger && menu) {
    burger.addEventListener('click', () => {
      burger.classList.toggle('open');
      menu.classList.toggle('open');
      document.body.style.overflow = menu.classList.contains('open') ? 'hidden' : '';
    });
  }
});
