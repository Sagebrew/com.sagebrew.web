/*global $, errorDisplay*/
$(document).ready(function () {
    "use strict";
    function removeFriend() {
        $(".js-remove_friend").click(function (event) {
            event.preventDefault();
            var friendToRemove = $(this).data('remove_friend');

            $.ajax({
                xhrFields: {withCredentials: true},
                type: "DELETE",
                url: "/v1/me/friends/" + friendToRemove + "/",
                contentType: "application/json; charset=utf-8",
                dataType: "json",
                success: function () {
                    var container = $("#js-sb_friend_" + friendToRemove);
                    container.remove();
                },
                error: function (XMLHttpRequest) {
                    if (XMLHttpRequest.status === 500) {
                        $("#server_error").show();
                    }
                }
            });
        });
    }
    function getFriends(url) {
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "GET",
            url: url,
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (data) {
                if (data.count === 0){
                    $("#friend_wrapper").append("<div><h3>Please use search to find your friends :)</h3></div>");
                }
                $.each(data.results, function (i, l) {
                    $("#friend_wrapper").append(l);
                });
                removeFriend();
                getFriends(data.next);
            },
            error: function (XMLHttpRequest) {
                errorDisplay(XMLHttpRequest);
            }
        });
    }
    var username = $("#user_info").data("page_user_username");
    getFriends("/v1/profiles/" + username + "/friends/?html=true&limit=1");
});