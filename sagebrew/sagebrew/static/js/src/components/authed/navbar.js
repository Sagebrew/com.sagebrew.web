/**
 * @file
 * All the functionality for the navbar.
 * TODO: Reorganize.
 */
var sagebrew = require('sagebrew');

/**
 *  Scope - User Authed
 *  All things relating to the navbar.
 */
function navbar() {
    $(document).ready(function() {
        //
        // Notifications
        // Retrieves all the notifications for a given user and gathers how
        // many have been seen or unseen.
        console.log("Navbar Start");

        sagebrew.resource.get({url: "/v1/me/notifications/render/"}).then(function(data){
            $('#notification_wrapper').append(data.results.html);
            if (data.results.unseen > 0) {
                $('#js-notification_notifier_wrapper').append('<span class="navbar-new sb_notifier" id="js-sb_notifications_notifier">' + data.results.unseen + '</span>');
            }
        });

        // Shows the notifications when the notification icon is clicked
        $(".show_notifications-action").click(function () {
            $("#notification_div").fadeToggle();
            if ($('#js-notification_notifier_wrapper').children().length > 0) {
                $.ajax({
                    xhrFields: {withCredentials: true},
                    type: "GET",
                    url: "/v1/me/notifications/?seen=true",
                    contentType: "application/json; charset=utf-8",
                    dataType: "json",
                    success: function () {
                        $('#js-sb_notifications_notifier').remove();
                    },
                    error: function (XMLHttpRequest) {
                        errorDisplay(XMLHttpRequest);
                    }
                });
            }
        });

        //
        // Rep Was Viewed?
        $(".show-reputation-action").on("click", function () {
            $.ajax({
                xhrFields: {withCredentials: true},
                type: "PUT",
                url: "/v1/me/",
                contentType: "application/json; charset=utf-8",
                dataType: "json",
                data: JSON.stringify({
                    "reputation_update_seen": true
                })
            });
        });

        //
        // Show Rep
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "GET",
            url: "/v1/profiles/" + $("#reputation_total").data('username') + "/reputation/",
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (data) {
                $("#reputation_total").append("<p>" + data["reputation"] + "</p>");
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                if(XMLHttpRequest.status === 500){
                    $("#server_error").show();
                }
            }
        });

        //
        // Search
        $(".full_search-action").click(function(e) {
            var search_param = ($('#sb_search_input').val());
            window.location.href = "/search/?q=" + search_param + "&page=1&filter=general";
        });
        $("#sb_search_input").keyup(function(e) {
            if(e.which === 10 || e.which === 13) {
                var search_param = ($('#sb_search_input').val());
                window.location.href = "/search/?q=" + search_param + "&page=1&filter=general";
            }
        });

        //
        //

        //
        // Friends
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
}

export function initNavbar() {
    return navbar();
}