/*global $*/
$(document).ready(function () {
    "use strict";
    // Retrieves all the friend requests for a given user and gathers how
    // many have been seen or unseen.
    $.ajax({
        xhrFields: {withCredentials: true},
        type: "GET",
        url: "/v1/me/friend_requests/render/",
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (data) {
            $('#friend_request_wrapper').append(data.results.html);
            if (data.results.unseen > 0) {
                $('#js-friend_request_notifier_wrapper').append('<span class="navbar-new sb_notifier" id="js-sb_friend_request_notifier">' + data.results.unseen + '</span>');
            }
        },
        error: function (XMLHttpRequest) {
            if (XMLHttpRequest.status === 500) {
                $("#server_error").show();
            }
        }
    });
    // Shows the friend requests when the friend request icon is clicked
    $(".show_friend_request-action").click(function () {
        $("#friend_request_div").fadeToggle();
        if ($('#js-sb_friend_request_notifier').length > 0) {
            $.ajax({
                xhrFields: {withCredentials: true},
                type: "GET",
                url: "/v1/me/friend_requests/?seen=true",
                contentType: "application/json; charset=utf-8",
                dataType: "json",
                success: function () {
                    $('#js-sb_friend_request_notifier').remove();
                },
                error: function () {
                    $("#server_error").show();
                }
            });
        }
        $(".respond_friend_request-accept-action").click(function (event) {
            event.preventDefault();
            var requestID = $(this).data('request_id');
            $.ajax({
                xhrFields: {withCredentials: true},
                type: "POST",
                url: "/v1/me/friend_requests/" + requestID + "/accept/",
                data: JSON.stringify({
                    'request_id': requestID
                }),
                contentType: "application/json; charset=utf-8",
                dataType: "json",
                success: function () {
                    $('#friend_request_' + requestID).remove();
                },
                error: function (XMLHttpRequest) {
                    if (XMLHttpRequest.status === 500) {
                        $("#server_error").show();
                    }
                }
            });
        });
        $(".respond_friend_request-decline-action").click(function (event) {
            event.preventDefault();
            var requestID = $(this).data('request_id');
            $.ajax({
                xhrFields: {withCredentials: true},
                type: "POST",
                url: "/v1/me/friend_requests/" + requestID + "/decline/",
                data: JSON.stringify({
                    'request_id': requestID
                }),
                contentType: "application/json; charset=utf-8",
                dataType: "json",
                success: function () {
                    $('#friend_request_' + requestID).remove();
                },
                error: function (XMLHttpRequest) {
                    if (XMLHttpRequest.status === 500) {
                        $("#server_error").show();
                    }
                }
            });
        });
        $(".respond_friend_request-block-action").click(function (event) {
            event.preventDefault();
            var requestID = $(this).data('request_id');
            $.ajax({
                xhrFields: {withCredentials: true},
                type: "POST",
                url: "/v1/me/friend_requests/" + requestID + "/block/",
                data: JSON.stringify({
                    'request_id': requestID
                }),
                contentType: "application/json; charset=utf-8",
                dataType: "json",
                success: function () {
                    $('#friend_request_' + requestID).remove();
                },
                error: function (XMLHttpRequest) {
                    if (XMLHttpRequest.status === 500) {
                        $("#server_error").show();
                    }
                }
            });
        });

    });
});
