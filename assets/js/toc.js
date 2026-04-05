// Detect when toc-wrapper becomes sticky and add .is-stuck so the gradient mask activates
(function () {
    var tocWrapper = document.querySelector('.toc-wrapper');
    if (!tocWrapper) return;
    var sentinel = document.createElement('div');
    sentinel.style.cssText = 'position:absolute;height:1px;width:1px;pointer-events:none;';
    tocWrapper.parentNode.insertBefore(sentinel, tocWrapper);
    new IntersectionObserver(function (entries) {
        tocWrapper.classList.toggle('is-stuck', !entries[0].isIntersecting);
    }).observe(sentinel);
})();

// ADDS ACTIVE CLASS TO LINKS WHEN SECTION WITH THE SAME SELECTOR AS THE HREF IS REACHED (CLASS .LINK IS NEEDED ON ALL <a> TAGS)

var tocScrolling = false;

$(document).ready(function () {
    $(window).scroll(function () {
        $('.back-to-top').toggleClass('visible', $(this).scrollTop() > 100);

        if (tocScrolling) return;

        var y = $(this).scrollTop();

        $('.link').each(function () {
            var id = ($(this).attr('href') || '').replace(/^#/, '');
            var el = id ? document.getElementById(id) : null;
            if (el && y >= $(el).offset().top - 40) {
                $('.link').not(this).removeClass('active');
                $(this).addClass('active');
            }
        });

    });
});

// SMOOTH SCROLLING (with negative scroll of 40 for header)

$(function () {
    $('a.link[href*="#"]:not([href="#"])').click(function () {
        if (location.pathname.replace(/^\//, '') == this.pathname.replace(/^\//, '') && location.hostname == this.hostname) {
            var id = this.hash.slice(1);
            var el = id ? document.getElementById(id) : null;
            if (!el) el = document.getElementsByName(id)[0] || null;
            if (el) {
                $('.link').removeClass('active');
                $(this).addClass('active');
                tocScrolling = true;
                setTimeout(function () { tocScrolling = false; }, 950);
                $('html,body').animate({
                    scrollTop: ($(el).offset().top - 40)
                }, 850);
                return false;
            }
        }
    });
});
