// Converts plain-text URLs in Works Cited entries into clickable links.
// Skips text already inside <a> tags (already linked).

document.addEventListener('DOMContentLoaded', function () {
    var urlRegex = /\bhttps?:\/\/[^\s<>()\[\]{}"]+/g;

    document.querySelectorAll('.citations-list li').forEach(function (li) {
        var walker = document.createTreeWalker(
            li,
            NodeFilter.SHOW_TEXT,
            {
                acceptNode: function (node) {
                    return node.parentNode.tagName === 'A'
                        ? NodeFilter.FILTER_REJECT
                        : NodeFilter.FILTER_ACCEPT;
                }
            }
        );

        var textNodes = [];
        while (walker.nextNode()) {
            textNodes.push(walker.currentNode);
        }

        textNodes.forEach(function (node) {
            if (!urlRegex.test(node.textContent)) { urlRegex.lastIndex = 0; return; }
            urlRegex.lastIndex = 0;

            var span = document.createElement('span');
            span.innerHTML = node.textContent.replace(urlRegex, function (url) {
                // Strip trailing punctuation that is unlikely part of the URL
                var clean = url.replace(/[.,;:!?)>]+$/, '');
                var trail = url.slice(clean.length);
                return '<a href="' + clean + '">' + clean + '</a>' + trail;
            });
            node.parentNode.replaceChild(span, node);
            urlRegex.lastIndex = 0;
        });
    });
});
