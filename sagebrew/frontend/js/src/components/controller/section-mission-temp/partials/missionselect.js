export function load() {
    var $app = $(".app-sb");
    $app
        //
        // TODO repeat code as what we use in section-profile friends.js
        .on('mouseenter', ".js-hover-overlay-activate", function(event) {
            event.preventDefault();
            var $this = $(this),
            overlay = $this.parent().parent().find(".sb-overlay");
            overlay.height($this.height());
            overlay.fadeIn('fast');
        })
        //
        // Remove overlay when mouse leaves card region
        .on('mouseleave', '.sb-overlay', function(event) {
            event.preventDefault();
            $(this).fadeOut('fast');
            $(".sb-profile-not-friend-element-image").removeClass("active");
        })
        .on('click', '#js-public-office', function(event) {
            "use strict";
            event.preventDefault();
            window.location.href = "/quest/mission/public_office/";
        });
}
