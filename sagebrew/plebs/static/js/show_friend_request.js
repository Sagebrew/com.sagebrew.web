/*global $, jQuery*/
$(document).ready(function () {
    "use strict";
    $(".show_friend_request-action").click(function () {
        $("#friend_request_div").fadeToggle();
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