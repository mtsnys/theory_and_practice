// ADDS ACTIVE CLASS TO LINKS WHEN SECTION WITH THE SAME SELECTOR AS THE HREF IS REACHED (CLASS .LINK IS NEEDED ON ALL <a> TAGS)

$(document).ready(function () {
    $(window).scroll(function () {

        var y = $(this).scrollTop();

        $('.link').each(function (event) {
            if (y >= $($(this).attr('href')).offset().top - 40) {
                $('.link').not(this).removeClass('active');
                $(this).addClass('active');
            }
        });

    });
});

// SMOOTH SCROLLING (with negative scroll of 40 for header)

$(function () {
    $('a[href*=#]:not([href=#])').click(function () {
        if (location.pathname.replace(/^\//, '') == this.pathname.replace(/^\//, '') && location.hostname == this.hostname) {
            var target = $(this.hash);
            target = target.length ? target : $('[name=' + this.hash.slice(1) + ']');
            if (target.length) {
                $('html,body').animate({
                    scrollTop: (target.offset().top - 40)
                }, 850);
                return false;
            }
        }
    });
});