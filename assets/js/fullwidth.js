document.addEventListener("DOMContentLoaded", function() {
  const fullWidthDivs = document.querySelectorAll('article section div.fullwidth');

  fullWidthDivs.forEach(div => {
    const bodyWidth = document.body.clientWidth;

    // Get the combined padding-left of article and section
    let totalPaddingLeft = 0;
    let currentElement = div; // Start with the div itself
    while (currentElement && currentElement.tagName.toLowerCase() !== 'body') {
      totalPaddingLeft += parseInt(getComputedStyle(currentElement).paddingLeft);
      currentElement = currentElement.parentElement; // Move up to the parent
    }

    // Calculate the adjusted width and margin-left
    const adjustedWidth = bodyWidth - 2 * totalPaddingLeft;
    const adjustedMarginLeft = -1 * totalPaddingLeft;

    // Apply the styles
    div.style.width = `${adjustedWidth}px`;
    div.style.marginLeft = `${adjustedMarginLeft}px`;

    // Height calculations (same as before)
    const divHeight = div.clientHeight;
    const nextElement = div.nextElementSibling;
    if (nextElement) {
      nextElement.style.marginTop = `${divHeight}px`;
    }
  });
});