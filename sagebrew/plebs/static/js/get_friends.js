/*global $, jQuery, ajaxSecurity*/
$(document).ready(function () {
    "use strict";
    function removeFriend() {
        $(".remove_friend").click(function (event) {
            event.preventDefault();
            var friendToRemove = $(this).data('remove_friend');
            $.ajaxSetup({
                beforeSend: function (xhr, settings) {
                    ajaxSecurity(xhr, settings);
                }
            });
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
    var username = $("#user_info").data("page_user_username"),
        scrolled = false;
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            ajaxSecurity(xhr, settings);
        }
    });
    $.ajax({
        xhrFields: {withCredentials: true},
        type: "GET",
        url: "/v1/profiles/" + username + "/friends/?html=true",
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (data) {
            if (data.count === 0){
                $("#friend_wrapper").append("<div><h3>Please use search to find your friends :)</h3></div>");
            }
            $.each(data.results, function (i, l) {
                $("#friend_wrapper").append(l);
            });
            $("#next_url").data('url', data.next);
            removeFriend();
        },
        error: function (XMLHttpRequest) {
            if (XMLHttpRequest.status === 500) {
                $("#server_error").show();
            }
        }
    });
    $(window).scroll(function () {
        if (scrolled === false) {
            if ($(window).scrollTop() + $(window).height() > ($(document).height() - $(document).height() * 0.5)) {
                scrolled = true;
                var next = $("#next_url").data('url');
                if (next !== null) {
                    $.ajaxSetup({
                        beforeSend: function (xhr, settings) {
                            ajaxSecurity(xhr, settings);
                        }
                    });
                    $.ajax({
                        xhrFields: {withCredentials: true},
                        type: "GET",
                        url: next,
                        contentType: "application/json; charset=utf-8",
                        dataType: "json",
                        success: function (data) {
                            scrolled = false;
                            $.each(data.results, function (i, l) {
                                $("#friend_wrapper").append(l);
                            });
                            $("#next_url").data('url', data.next);
                            removeFriend();
                        },
                        error: function (XMLHttpRequest) {
                            if (XMLHttpRequest.status === 500) {
                                $("#server_error").show();
                            }
                        }
                    });
                }
            }
        }
    });
});