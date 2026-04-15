// Repositions an "initial" non-numbered margin note so it is associated with
// the first sentence of the first paragraph after any epigraph, rather than
// floating before the epigraph where it overlaps the blockquote border on mobile.
//
// An "initial" margin note is defined as: a non-numbered margin-toggle label
// that is the sole meaningful content of the first <p> in its section.

document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('article section').forEach(function (section) {
    // Collect only top-level <p> elements (not inside blockquotes or figures)
    var allPs = Array.from(section.querySelectorAll('p')).filter(function (p) {
      return p.parentElement === section;
    });
    if (!allPs.length) return;

    // Only consider a note whose paragraph is the very first top-level <p> in the section
    var candidateP = allPs[0];
    var label = candidateP.querySelector('label.margin-toggle:not(.sidenote-number)');
    if (!label) return;

    var input = label.nextElementSibling;
    var span = input && input.nextElementSibling;
    if (!input || !span || !span.classList.contains('marginnote')) return;

    // Find the first paragraph after all blockquotes in this section
    var blockquotes = section.querySelectorAll('blockquote');
    var targetP = null;

    if (blockquotes.length > 0) {
      var lastBQ = blockquotes[blockquotes.length - 1];
      for (var i = 0; i < allPs.length; i++) {
        // Must come after the blockquote AND not be inside it
        if (!lastBQ.contains(allPs[i]) &&
            (lastBQ.compareDocumentPosition(allPs[i]) & Node.DOCUMENT_POSITION_FOLLOWING)) {
          targetP = allPs[i];
          break;
        }
      }
    } else {
      // No epigraph: target the second paragraph (the first real content paragraph)
      if (allPs.length > 1) {
        targetP = allPs[1];
      } else {
        // Note is alone in its section — look in the next sibling section
        var nextSection = section.nextElementSibling;
        while (nextSection && nextSection.tagName !== 'SECTION') {
          nextSection = nextSection.nextElementSibling;
        }
        if (nextSection) {
          var nextPs = Array.from(nextSection.querySelectorAll('p')).filter(function (p) {
            return p.parentElement === nextSection;
          });
          if (nextPs.length) targetP = nextPs[0];
        }
      }
    }

    if (!targetP) return;

    // Walk text nodes in targetP to find the end of the first sentence (". ")
    var insertNode = null;
    var insertOffset = 0;

    function findSentenceEnd(node) {
      if (insertNode) return;
      if (node.nodeType === Node.TEXT_NODE) {
        var text = node.textContent;
        var idx = text.search(/\.\s/);
        if (idx !== -1) {
          insertNode = node;
          insertOffset = idx + 1; // position after the period, before the space
        } else if (/\.$/.test(text)) {
          // Period at the very end of the text node (e.g. before an inline footnote element)
          insertNode = node;
          insertOffset = text.length;
        }
      } else {
        for (var i = 0; i < node.childNodes.length; i++) {
          findSentenceEnd(node.childNodes[i]);
          if (insertNode) break;
        }
      }
    }

    findSentenceEnd(targetP);
    if (!insertNode) return;

    // Split the text node and insert the note trio (label, input, span) at that point
    var afterNode = insertNode.splitText(insertOffset);
    var parent = insertNode.parentNode;
    parent.insertBefore(label, afterNode);
    parent.insertBefore(input, afterNode);
    parent.insertBefore(span, afterNode);

    // Remove the original paragraph if it is now empty
    if (!candidateP.textContent.trim()) {
      candidateP.parentNode.removeChild(candidateP);
    }
  });
});
