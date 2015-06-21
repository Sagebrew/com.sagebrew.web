/*global $, jQuery, loadPosts, errorDisplay*/
$(document).ready(function () {
    "use strict";

    function newsfeed(url) {
        $("#news").spin({lines: 8, length: 4, width: 3, radius: 5});
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "GET",
            url: url,
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (data) {
                var wallContainer = $('#news');
                if (data.count === 0) {
                    wallContainer.append('<div id="js-wall_temp_message"><h3>Get out there and make some news :)</h3></div>');
                } else {
                    wallContainer.append(data.results);
                    // TODO Went with this approach as the scrolling approach resulted
                    // in the posts getting out of order. It also had some interesting
                    // functionality that wasn't intuitive. Hopefully transitioning to
                    // a JS Framework allows us to better handle this feature.
                    if (data.next !== null) {
                        newsfeed(data.next);
                    }
                }
                wallContainer.spin(false);
            },
            error: function (XMLHttpRequest) {
                errorDisplay(XMLHttpRequest);
            }
        });
    }
    newsfeed("/v1/me/newsfeed/?html=true&expedite=true&page_size=6");
});
