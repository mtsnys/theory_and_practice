(function () {
  'use strict';

  var citMap = window.articleCitations;
  if (!citMap || !Object.keys(citMap).length) return;

  // -----------------------------------------------------------------------
  // Fuzzy lookup: given "Author Year" (or "Author et al. Year" etc.),
  // return the citation HTML, or null if no match.
  // Mirrors the Python check_citations.py try_match() logic.
  // -----------------------------------------------------------------------
  function fuzzyLookup(authorYear) {
    // 1. Exact
    if (citMap[authorYear]) return citMap[authorYear];

    // 2. Strip "et al." → "Mehr et al. 2021" → "Mehr 2021"
    var stripped = authorYear.replace(/\s+et\s+al\.?\s*(\d)/, ' $1').trim();
    if (stripped !== authorYear) {
      if (citMap[stripped]) return citMap[stripped];
      // Also try last word of the stripped author + year
      // (handles "Julie Traub Eichhorn et al. 2018" → "Eichhorn 2018")
      var mStrip = stripped.match(/(\S+)\s+(\d{4}[a-z]?|forthcoming)\s*$/);
      if (mStrip && citMap[mStrip[1] + ' ' + mStrip[2]]) return citMap[mStrip[1] + ' ' + mStrip[2]];
    }

    // 3. First-author + year (handles "Lerdahl and Jackendoff 1983" → "Lerdahl 1983",
    //    "Riverin-Coutlée, Roy, and Gubian 2023" → "Riverin-Coutlée 2023")
    // Skip compound "Author orig pub" queries — the caller handles year-by-year fallback,
    // and step 3's last-year extraction would match the wrong entry (e.g. "Mitchell 2000" album
    // instead of the "[1997] 2000" interview).
    if (/\d{4}[a-z]?\s+\d{4}/.test(authorYear)) return null;
    var m3 = authorYear.match(/^(\S+).*?(\d{4}[a-z]?|forthcoming)\s*$/);
    if (m3) {
      var first = m3[1].replace(/,$/, ''), yr = m3[2];
      var firstNorm = first.replace(/[\u2019']/g, '');
      for (var key in citMap) {
        var parts = key.split(' ');
        var keyFirst = parts[0].replace(/[\u2019']/g, '');
        if (keyFirst === firstNorm && parts[parts.length - 1] === yr) {
          return citMap[key];
        }
      }
    }

    // 4. Last-word of author + year (handles "See Earp 1991", "Justin London 2012",
    //    "Matt BaileyShea 2021", full-name narrative forms, etc.)
    var m4 = authorYear.match(/(\S+)\s+(\d{4}[a-z]?)$/);
    if (m4 && authorYear.indexOf(' ') !== -1) {
      var candidate = m4[1] + ' ' + m4[2];
      if (citMap[candidate]) return citMap[candidate];
    }

    return null;
  }

  // -----------------------------------------------------------------------
  // Regexes for finding citations in text nodes
  // -----------------------------------------------------------------------

  // Parenthetical/inline: "Vande Moortele 2013", "Lerdahl and Jackendoff 1983",
  //   "Mehr et al. 2021", "Bach [1753] 1762"
  var AUTHOR_YEAR_RE = new RegExp(
    '((?:[A-Z]\\.\\s+)?[A-Z\u00C0-\u00D6\u00D8-\u00DE][a-zA-Z\u00C0-\u00FF\\-\u2019\']+' +
    '(?:\\s+[A-Z\u00C0-\u00D6\u00D8-\u00DE][a-zA-Z\u00C0-\u00FF\\-\u2019\']+)*' +
    '(?:,\\s+[A-Z\u00C0-\u00D6\u00D8-\u00DE][a-zA-Z\u00C0-\u00FF\\-\u2019\']+(?:\\s+[A-Z\u00C0-\u00D6\u00D8-\u00DE][a-zA-Z\u00C0-\u00FF\\-\u2019\']+)*)*' +
    '(?:,?\\s*and\\s+[A-Z\u00C0-\u00D6\u00D8-\u00DE][a-zA-Z\u00C0-\u00FF\\-\u2019\']+' +
      '(?:\\s+[A-Z\u00C0-\u00D6\u00D8-\u00DE][a-zA-Z\u00C0-\u00FF\\-\u2019\']+)*)?' +
    '(?:\\s+et\\s+al\\.?)?)' +
    ',?\\s+(?:\\[(\\d{4})[\\d\\u2013\\-]*\\]\\s*)?' +
    '(\\d{4}[a-z]?|forthcoming)',
    'g'
  );

  // Narrative: "Burstein (2020)", "Thomas's (2006, 43–47)", "Heyes (2018)"
  var NARRATIVE_RE = new RegExp(
    '((?:[A-Z]\\.\\s+)?[A-Z\u00C0-\u00D6\u00D8-\u00DE][a-zA-Z\u00C0-\u00FF\\-\u2019\']+' +
    '(?:\\s+[A-Z\u00C0-\u00D6\u00D8-\u00DE][a-zA-Z\u00C0-\u00FF\\-\u2019\']+)*' +
    '(?:,\\s+[A-Z\u00C0-\u00D6\u00D8-\u00DE][a-zA-Z\u00C0-\u00FF\\-\u2019\']+(?:\\s+[A-Z\u00C0-\u00D6\u00D8-\u00DE][a-zA-Z\u00C0-\u00FF\\-\u2019\']+)*)*' +
    '(?:,?\\s*and\\s+[A-Z\u00C0-\u00D6\u00D8-\u00DE][a-zA-Z\u00C0-\u00FF\\-\u2019\']+' +
      '(?:\\s+[A-Z\u00C0-\u00D6\u00D8-\u00DE][a-zA-Z\u00C0-\u00FF\\-\u2019\']+)*)?'+
    '(?:\\s+et\\s+al\\.?)?)' +
    '\\s*\\(\\s*(?:\\[(\\d{4})[\\d\\u2013\\-]*\\]\\s*)?(\\d{4}[a-z]?|forthcoming)(?:\\s*,\\s*[^)]{0,60})?\\)',
    'g'
  );

  // -----------------------------------------------------------------------
  // Process a single text node: find citation patterns, wrap in spans
  // -----------------------------------------------------------------------
  function processNode(node) {
    var text = node.textContent;
    if (!text || !/[A-Z]/.test(text) || (!/\d{4}/.test(text) && !text.includes('forthcoming'))) return;

    var matches = [];

    // Pass 1: inline author-year (parenthetical context)
    AUTHOR_YEAR_RE.lastIndex = 0;
    var m;
    while ((m = AUTHOR_YEAR_RE.exec(text)) !== null) {
      var author = m[1].trim().replace(/[\u2019']s\s*$/, '');
      var html;
      if (m[2] && m[3]) {
        // Bracketed original year + pub year: try compound "Author orig pub" first
        // (handles reprints where both years are needed to disambiguate, e.g. Mitchell_1972_2002),
        // then fall back to orig year alone, then pub year alone.
        html = fuzzyLookup(author + ' ' + m[2] + ' ' + m[3]) ||
               fuzzyLookup(author + ' ' + m[2]) ||
               fuzzyLookup(author + ' ' + m[3]);
      } else {
        html = fuzzyLookup(author + ' ' + (m[2] || m[3]));
      }
      if (html) {
        matches.push({ start: m.index, end: m.index + m[0].length, display: m[0], html: html });
      }
    }

    // Pass 2: narrative form Author (Year)
    NARRATIVE_RE.lastIndex = 0;
    while ((m = NARRATIVE_RE.exec(text)) !== null) {
      var author2 = m[1].trim().replace(/[\u2019']s\s*$/, '');
      var primaryYear = m[3] || m[2];
      var html2;
      if (m[2] && m[3]) {
        html2 = fuzzyLookup(author2 + ' ' + m[2] + ' ' + m[3]) ||
                fuzzyLookup(author2 + ' ' + m[2]) ||
                fuzzyLookup(author2 + ' ' + m[3]);
      } else {
        html2 = fuzzyLookup(author2 + ' ' + primaryYear);
      }
      if (!html2) continue;

      // Check for additional years after the primary year, e.g. "Maw (2002, 2004, 2013)"
      var parenIdx = m[0].indexOf('(');
      var primaryOffset = m[0].indexOf(primaryYear, parenIdx);
      var afterPrimary = m[0].slice(primaryOffset + primaryYear.length);
      var extraYearRE = /,\s*(\d{4}[a-z]?)\b/g;
      var extraM2;
      var extraEntries = [];
      while ((extraM2 = extraYearRE.exec(afterPrimary)) !== null) {
        var extraHtml = fuzzyLookup(author2 + ' ' + extraM2[1]);
        if (extraHtml) {
          var yrOffset = primaryOffset + primaryYear.length + extraM2.index + extraM2[0].indexOf(extraM2[1]);
          extraEntries.push({ year: extraM2[1], html: extraHtml, offset: yrOffset });
        }
      }

      if (extraEntries.length > 0) {
        // Multi-year: wrap each year token individually
        var pStart = m.index + primaryOffset, pEnd = pStart + primaryYear.length;
        if (!matches.some(function(e) { return pStart < e.end && pEnd > e.start; })) {
          matches.push({ start: pStart, end: pEnd, display: primaryYear, html: html2 });
        }
        for (var ei = 0; ei < extraEntries.length; ei++) {
          var ent = extraEntries[ei];
          var eStart = m.index + ent.offset, eEnd = eStart + ent.year.length;
          if (!matches.some(function(e) { return eStart < e.end && eEnd > e.start; })) {
            matches.push({ start: eStart, end: eEnd, display: ent.year, html: ent.html });
          }
        }
      } else {
        // Single year: wrap the full narrative match as before
        var overlaps = matches.some(function(e) {
          return m.index < e.end && m.index + m[0].length > e.start;
        });
        if (!overlaps) {
          matches.push({ start: m.index, end: m.index + m[0].length, display: m[0], html: html2 });
        }
      }
    }

    // Pass 3: implied same-author years — "Sundberg 1970, 1973" → also link ", 1973"
    var IMPLIED_YEAR_RE = /^[,;]\s*(\d{4}[a-z]?)/;
    var baseMatches = matches.slice();
    for (var k = 0; k < baseMatches.length; k++) {
      var base = baseMatches[k];
      // Strip year (and optional bracket year) from end of display to get author
      var authorPart = base.display
        .replace(/,?\s+(?:\[\d{4}[\d\u2013\-]*\]\s*)?(?:\d{4}[a-z]?|forthcoming)\s*$/, '')
        .trim();
      if (!authorPart) continue;
      var pos = base.end;
      while (pos < text.length) {
        var im = text.slice(pos).match(IMPLIED_YEAR_RE);
        if (!im) break;
        var implHtml = fuzzyLookup(authorPart + ' ' + im[1]);
        var iStart = pos, iEnd = pos + im[0].length;
        var covered = matches.some(function (e) { return iStart >= e.start && iEnd <= e.end; });
        if (implHtml && !covered) {
          matches.push({ start: iStart, end: iEnd, display: im[0], html: implHtml });
          pos = iEnd;
        } else {
          break;
        }
      }
    }

    if (!matches.length) return;

    matches.sort(function (a, b) { return a.start - b.start; });

    var frag = document.createDocumentFragment();
    var lastIndex = 0;

    for (var i = 0; i < matches.length; i++) {
      var match = matches[i];
      if (match.start < lastIndex) continue; // skip overlap
      if (match.start > lastIndex) {
        frag.appendChild(document.createTextNode(text.slice(lastIndex, match.start)));
      }
      var span = document.createElement('span');
      span.className = 'cite-ref';
      span.textContent = match.display;
      span.dataset.citHtml = match.html;
      frag.appendChild(span);
      lastIndex = match.end;
    }

    if (lastIndex < text.length) {
      frag.appendChild(document.createTextNode(text.slice(lastIndex)));
    }

    node.parentNode.replaceChild(frag, node);
  }

  // -----------------------------------------------------------------------
  // Handle italicised periodical/title citations: <em>Variety</em> [1966] 2001
  // These span element boundaries so the text-node walker can't see them.
  // -----------------------------------------------------------------------
  function processEmCitations(article) {
    var ems = Array.prototype.slice.call(article.querySelectorAll('em'));
    ems.forEach(function (em) {
      // Skip works-cited, code, already-wrapped
      var el = em;
      while (el) {
        if (el.id === 'works-cited') return;
        var t = el.tagName ? el.tagName.toLowerCase() : '';
        if (t === 'script' || t === 'style' || t === 'code' || t === 'pre') return;
        el = el.parentNode;
      }
      if (em.closest && em.closest('.cite-ref')) return;

      var next = em.nextSibling;
      if (!next || next.nodeType !== 3) return;

      var emText = em.textContent.trim();
      var afterText = next.textContent;

      // Match optional [orig_year] then pub_year at start of following text
      var m = afterText.match(/^(\s*(?:\[(\d{4})[\d\u2013\-]*\]\s*)?)(\d{4}[a-z]?)/);
      if (!m) return;

      var lookupYear = m[2] || m[3];
      var html = fuzzyLookup(emText + ' ' + lookupYear);
      if (!html) return;

      var consumed = m[0]; // e.g. " [1966] 2001"
      var remaining = afterText.slice(consumed.length);

      var span = document.createElement('span');
      span.className = 'cite-ref';
      span.dataset.citHtml = html;

      em.parentNode.insertBefore(span, em);
      span.appendChild(em);
      span.appendChild(document.createTextNode(consumed));

      if (remaining) {
        next.textContent = remaining;
      } else {
        next.parentNode.removeChild(next);
      }
    });
  }

  // -----------------------------------------------------------------------
  // Walk text nodes in the article, skipping works-cited and code blocks
  // -----------------------------------------------------------------------
  function walkArticle() {
    var article = document.querySelector('article.main-article');
    if (!article) return;

    var walker = document.createTreeWalker(
      article,
      NodeFilter.SHOW_TEXT,
      {
        acceptNode: function (node) {
          var p = node.parentNode;
          if (!p) return NodeFilter.FILTER_REJECT;
          var tag = p.tagName ? p.tagName.toLowerCase() : '';
          if (tag === 'script' || tag === 'style' || tag === 'code' || tag === 'pre') {
            return NodeFilter.FILTER_REJECT;
          }
          // Skip the works-cited section
          var el = p;
          while (el) {
            if (el.id === 'works-cited') return NodeFilter.FILTER_REJECT;
            el = el.parentNode;
          }
          // Skip already-processed spans
          if (p.classList && p.classList.contains('cite-ref')) {
            return NodeFilter.FILTER_REJECT;
          }
          return NodeFilter.FILTER_ACCEPT;
        }
      }
    );

    var nodes = [];
    var node;
    while ((node = walker.nextNode())) nodes.push(node);
    nodes.forEach(processNode);

    processEmCitations(article);
  }

  // -----------------------------------------------------------------------
  // Tooltip
  // -----------------------------------------------------------------------
  var tooltip = document.createElement('div');
  tooltip.id = 'citation-tooltip';
  document.body.appendChild(tooltip);

  function positionTooltip(el) {
    var rect = el.getBoundingClientRect();
    var scrollY = window.scrollY || window.pageYOffset || 0;
    var scrollX = window.scrollX || window.pageXOffset || 0;

    // 9px gap: 8px for arrow height + 1px breathing room
    var top = rect.bottom + scrollY + 9;
    var left = rect.left + scrollX;
    var maxW = Math.min(440, window.innerWidth - 40);

    if (left + maxW > scrollX + window.innerWidth - 20) {
      left = scrollX + window.innerWidth - maxW - 20;
    }
    if (left < scrollX + 10) left = scrollX + 10;

    tooltip.style.top = top + 'px';
    tooltip.style.left = left + 'px';
    tooltip.style.maxWidth = maxW + 'px';

    // Point the arrow at the horizontal centre of the cite-ref element.
    // --arrow-left is the left edge of the outer 14px-wide triangle.
    var citeCenter = rect.left + rect.width / 2 + scrollX;
    var arrowLeft = Math.round(citeCenter - left - 7);
    // Clamp so the arrow stays within the tooltip box
    arrowLeft = Math.max(8, Math.min(maxW - 22, arrowLeft));
    tooltip.style.setProperty('--arrow-left', arrowLeft + 'px');
  }

  document.addEventListener('mouseover', function (e) {
    var ref = e.target.closest && e.target.closest('.cite-ref');
    if (!ref || !ref.dataset.citHtml) return;
    tooltip.innerHTML = ref.dataset.citHtml;
    positionTooltip(ref);
    tooltip.classList.add('visible');
  });

  document.addEventListener('mouseout', function (e) {
    if (e.target.closest && e.target.closest('.cite-ref')) {
      tooltip.classList.remove('visible');
    }
  });

  // -----------------------------------------------------------------------
  // Init
  // -----------------------------------------------------------------------
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', walkArticle);
  } else {
    walkArticle();
  }

})();
