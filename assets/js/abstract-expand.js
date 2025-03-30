document.addEventListener('DOMContentLoaded', function() {
  const abstractContainers = document.querySelectorAll('.abstract-container');

  abstractContainers.forEach(container => {
    const abstractShort = container.querySelector('.abstract-short');
    const abstractFull = container.querySelector('.abstract-full');
    const readMore = container.querySelector('.read-more');
    const readLess = container.querySelector('.read-less');
    const arrows = container.querySelectorAll('.arrow');

    if (readMore && readLess) {
      readMore.addEventListener('click', () => {
        abstractFull.classList.add('visible');
        abstractShort.style.display = 'none';
        arrows.forEach((element) => {element.classList.add('rotate-up')});
      });

      readLess.addEventListener('click', () => {
        abstractFull.classList.remove('visible');
        abstractShort.style.display = 'block';
        arrows.forEach((element) => {element.classList.remove('rotate-up')});
      });
    }
  });
});