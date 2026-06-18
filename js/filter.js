document.addEventListener('DOMContentLoaded', () => {
  const buttons = document.querySelectorAll('.filter-btn');
  const rows = document.querySelectorAll('.work-row');

  // Read genre from URL param on load
  const params = new URLSearchParams(window.location.search);
  const initial = params.get('genre') || 'all';
  setFilter(initial);

  buttons.forEach(btn => {
    btn.addEventListener('click', () => setFilter(btn.dataset.genre));
  });

  function setFilter(genre) {
    buttons.forEach(b => b.classList.toggle('active', b.dataset.genre === genre));
    rows.forEach(row => {
      const match = genre === 'all' || row.dataset.genre === genre;
      row.style.display = match ? '' : 'none';
    });
  }
});
