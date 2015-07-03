/*global $, jQuery, loadPosts, errorDisplay, enableContentFunctionality, populateComments*/
$(document).ready(function () {
    "use strict";
    function newsfeed(url) {
        $("#wall_app").spin({lines: 8, length: 4, width: 3, radius: 5});
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "GET",
            url: url,
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (data) {
                var wallContainer = $('#wall_app');
                if (data.count === 0) {
                    wallContainer.append('<div id="js-wall_temp_message"><h3>Get out there and make some news :)</h3></div>');
                } else {

                    for (var i = 0; i < data.results.length; i++) {
                        wallContainer.append(data.results[i].html);
                        enableContentFunctionality(data.results[i].id, data.results[i].type);
                        if(data.results[i].type !== "politicalcampaign"){
                            populateComments([data.results[i].id], data.results[i].type + "s");
                        }

                    }
                    // TODO Went with this approach as the scrolling approach resulted
                    // in the posts getting out of order. It also had some interesting
                    // functionality that wasn't intuitive. Hopefully transitioning to
                    // a JS Framework allows us to better handle this feature.
                    if (data.next !== null) {
                        if(data.next.indexOf("&page=4&") > -1 && data.next.indexOf("&page_size=2&") > -1){
                            newsfeed("/v1/me/newsfeed/?html=true&expedite=true&page=2&page_size=6");
                        } else {
                            newsfeed(data.next);
                        }
                    }
                }
                wallContainer.spin(false);
            },
            error: function (XMLHttpRequest) {
                errorDisplay(XMLHttpRequest);
            }
        });
    }
    newsfeed("/v1/me/newsfeed/?html=true&expedite=true&page_size=2");
});
