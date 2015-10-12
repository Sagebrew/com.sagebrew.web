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
        //Notification count in sidebar.
        sagebrew.request.get({url: "/v1/me/notifications/render/"})
            .then(function(data){
                $('#notification_wrapper').append(data.results.html);
                if (data.results.unseen > 0) {
                    $('#js-notification_notifier_wrapper').append('<span class="navbar-new sb_notifier" id="js-sb_notifications_notifier">' + data.results.unseen + '</span>');
                }
        });

        // Shows the notifications when the notification icon is clicked
        $(".show_notifications-action").click(function () {
            $("#notification_div").fadeToggle();

            if ($('#js-notification_notifier_wrapper').children().length > 0) {
                sagebrew.request.get({url:  "/v1/me/notifications/?seen=true"})
                    .then(function() {
                        $('#js-sb_notifications_notifier').remove();
                });
            }

        });

        //
        // Rep Was Viewed?
        $(".show-reputation-action").on("click", function () {
            sagebrew.request.put({
                url: "/v1/me/",
                data: JSON.stringify({
                    "reputation_update_seen": true
                })
            });
        });

        //
        // Show Rep
        sagebrew.request.get({url: "/v1/profiles/" + $("#reputation_total").data('username') + "/reputation/"})
            .then(function(data) {
                $("#reputation_total").append("<p>" + data['reputation'] + "</p>");
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
        // Friends
        // Retrieves all the friend requests for a given user and gathers how
        // many have been seen or unseen.
        sagebrew.request.get({url: "/v1/me/friend_requests/render/"})
            .then(function(data) {
                $('#friend_request_wrapper').append(data.results.html);
                if (data.results.unseen > 0) {
                    $('#js-friend_request_notifier_wrapper').append('<span class="navbar-new sb_notifier" id="js-sb_friend_request_notifier">' + data.results.unseen + '</span>');
                }
            });

        // Shows the friend requests when the friend request icon is clicked
        $(".show_friend_request-action").click(function () {
            $("#friend_request_div").fadeToggle();
            if ($('#js-sb_friend_request_notifier').length > 0) {
                sagebrew.request.get({url: "/v1/me/friend_requests/?seen=true"})
                .then(function() {
                     $('#js-sb_friend_request_notifier').remove();
                });
            }

            $(".respond_friend_request-accept-action").click(function (event) {
                event.preventDefault();
                var requestID = $(this).data('request_id');
                sagebrew.request.post({
                    url: "/v1/me/friend_requests/" + requestID + "/accept/",
                    data: JSON.stringify({
                        'request_id': requestID
                    })
                }).then(function() {
                    $('#friend_request_' + requestID).remove();
                });
            });

            $(".respond_friend_request-decline-action").click(function (event) {
                event.preventDefault();
                var requestID = $(this).data('request_id');
                sagebrew.request.post({
                    url: "/v1/me/friend_requests/" + requestID + "/decline/",
                    data: JSON.stringify({
                        'request_id': requestID
                    })
                }).then(function() {
                    $('#friend_request_' + requestID).remove();
                });
            });

            $(".respond_friend_request-block-action").click(function (event) {
                event.preventDefault();
                var requestID = $(this).data('request_id');
                sagebrew.request.post({
                    url: "/v1/me/friend_requests/" + requestID + "/block/",
                    data: JSON.stringify({
                        'request_id': requestID
                    })
                }).then(function() {
                    $('#friend_request_' + requestID).remove();
                });
            });

        });
    });
}

export function initNavbar() {
    return navbar();
}