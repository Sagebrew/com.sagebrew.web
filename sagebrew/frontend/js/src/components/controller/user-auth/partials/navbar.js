/**
 * @file
 * All the functionality for the navbar.
 * TODO: Reorganize.
 * App: .app-navbar
 */
var request = require('./../../../api').request;
var settings = require('./../../../settings').settings;


/**
 *  Scope - User Authed
 *  All things relating to the navbar.
 */
function navbar() {
    var $navbar = $(".app-navbar");

    //
    // Load navbar count(s)
    var notifications = request.get({url: "/v1/me/notifications/render/"}),
        rep = request.get({url: "/v1/profiles/" + settings.user.username + "/reputation/"}),
        friends = request.get({url: "/v1/me/friend_requests/render/"});

    $.when(notifications, rep, friends).done(function(notificationData, repData, friendsData) {
        //Notifications
        $('#notification_wrapper').append(notificationData[0].results.html);
        if (notificationData[0].results.unseen > 0) {
            $('#js-notification_notifier_wrapper').append('<span class="navbar-new sb_notifier" id="js-sb_notifications_notifier">' + notificationData[0].results.unseen + '</span>');
        }

        //Rep
        $("#reputation_total").append("<p>" + repData[0]['reputation'] + "</p>");

        //Friends
        $('#friend_request_wrapper').append(friendsData[0].results.html);
        if (friendsData[0].results.unseen > 0) {
            $('#js-friend_request_notifier_wrapper').append('<span class="navbar-new sb_notifier" id="js-sb_friend_request_notifier">' + friendsData[0].results.unseen + '</span>');
        }

    });

    //
    // Bind Navbar Events.
    $navbar
        // Shows the notifications when the notification icon is clicked
        // Notify backend user has viewed the notifications.
        .on('click', '.show_notifications-action', function(event) {
            $("#notification_div").fadeToggle();
            if ($('#js-notification_notifier_wrapper').children().length > 0) {
                request.get({url:  "/v1/me/notifications/?seen=true"})
                    .then(function() {
                        $('#js-sb_notifications_notifier').remove();
                });
            }

        })
        //
        // Show Rep
        .on('click', '.show-reputation-action', function(event) {
            if ($(".sb_reputation_block:visible").length) {
                request.put({
                    url: "/v1/me/",
                    data: JSON.stringify({
                        "reputation_update_seen": true
                    })
                });
            }
        })
        //
        // Shows the friend requests when the friend request icon is clicked
        .on('click', '.show_friend_request-action', function(event) {
            $("#friend_request_div").fadeToggle();
            if ($('#js-sb_friend_request_notifier').length > 0) {
                request.get({url: "/v1/me/friend_requests/?seen=true"})
                .then(function() {
                     $('#js-sb_friend_request_notifier').remove();
                });
            }
        })
        //
        // Friend Request / Accept
        .on('click', '.respond_friend_request-accept-action', function(event) {
            event.preventDefault();
            var requestID = $(this).data('request_id');
            request.post({
                url: "/v1/me/friend_requests/" + requestID + "/accept/",
                data: JSON.stringify({
                    'request_id': requestID
                })
            }).then(function() {
                $('#friend_request_' + requestID).remove();
            });
        })
        //
        // Friend Request / Decline
        .on('click', '.respond_friend_request-decline-action', function(event){
            event.preventDefault();
            var requestID = $(this).data('request_id');
            request.post({
                url: "/v1/me/friend_requests/" + requestID + "/decline/",
                data: JSON.stringify({
                    'request_id': requestID
                })
            }).then(function() {
                $('#friend_request_' + requestID).remove();
            });
        })
        //
        // Friend Request / Block
        .on('click', '.respond_friend_request-block-action', function(event) {
            event.preventDefault();
            var requestID = $(this).data('request_id');
            request.post({
                url: "/v1/me/friend_requests/" + requestID + "/block/",
                data: JSON.stringify({
                    'request_id': requestID
                })
            }).then(function() {
                $('#friend_request_' + requestID).remove();
            });
        });

    //
    // Search
    $(".full_search-action").click(function(event) {
        var search_param = ($('#sb_search_input').val());
        window.location.href = "/search/?q=" + search_param + "&page=1&filter=general";
    });
    $("#sb_search_input").keyup(function(event) {
        if(event.which === 10 || event.which === 13) {
            var search_param = ($('#sb_search_input').val());
            window.location.href = "/search/?q=" + search_param + "&page=1&filter=general";
        }
    });
}

export function initNavbar() {
    return navbar();
}