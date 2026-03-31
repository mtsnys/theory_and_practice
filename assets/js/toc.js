// ADDS ACTIVE CLASS TO LINKS WHEN SECTION WITH THE SAME SELECTOR AS THE HREF IS REACHED (CLASS .LINK IS NEEDED ON ALL <a> TAGS)

$(document).ready(function () {
    $(window).scroll(function () {

        var y = $(this).scrollTop();

        $('.link').each(function (event) {
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
    $('a[href*="#"]:not([href="#"])').click(function () {
        if (location.pathname.replace(/^\//, '') == this.pathname.replace(/^\//, '') && location.hostname == this.hostname) {
            var id = this.hash.slice(1);
            var el = id ? document.getElementById(id) : null;
            if (!el) el = document.getElementsByName(id)[0] || null;
            if (el) {
                $('html,body').animate({
                    scrollTop: ($(el).offset().top - 40)
                }, 850);
                return false;
            }
        }
    });
});
