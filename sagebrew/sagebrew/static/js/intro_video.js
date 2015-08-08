/*global $, jQuery, ajaxSecurity, wistiaJQuery*/
$(document).ready(function () {
    "use strict";
    var vid = document.getElementById("bgvid"),
        pauseButton = document.getElementById("intro-video");
    console.log(pauseButton);
    function vidFade() {
        vid.classList.add("stopfade");
    }

    vid.addEventListener('ended', function () {
    // only functional if "loop" is removed
        vid.pause();
    // to capture IE10
        vidFade();
    });
    wistiaJQuery(document).bind("wistia-popover", function(event, iframe) {
        vid.pause();
        iframe.wistiaApi.time(0).play();
    });
    wistiaJQuery(document).bind("wistia-popover-close", function() {
        vid.play();
    });
});