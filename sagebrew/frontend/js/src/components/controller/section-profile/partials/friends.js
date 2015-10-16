/**
 * @file
 * Do things with friends.
 */
var request = require('./../../../api').request,
    helpers = require('./../../../common/helpers'),
    settings = require('./../../../settings').settings;

/**
 * Helper function to load friends.
 * This function is recursive. It will load friends until there are no more friends to load.
 *
 * @param url
 */
function loadFriends($app, url) {
    request.get({url:url})
        .done(function(data){
            if (data.count === 0){
                $app.append("<div><h3>Please use search to find your friends :)</h3></div>");
            } else {
                $.each(data.results, function (i, l) {
                    $app.append(l);
                });
            }
            loadFriends($app, data.next);
        });
}

export function init() {
    var $app = $(".app-sb");
    var $appFriends = $(".app-friends");

    // Load Friends.
    if ($appFriends.length) {
        //Load username from url.
        var username = helpers.args(1);
        loadFriends($appFriends, "/v1/profiles/" + username + "/friends/?html=true&limit=5");
    }

    //Friend Action binding.
    //TODO: this is a lot of repeated code from the nav app. We should
    //      consolidate.
    $app
        //
        // Remove Friend. (How Rude)
        .on('click', '.js-remove_friend', function(event) {
            event.preventDefault();
            var friendToRemove = $(this).data('remove_friend');

            request.remove({url: "/v1/me/friends/" + friendToRemove + "/"})
                .done(function() {
                    var container = $("#js-sb_friend_" + friendToRemove);
                    container.remove();
                });
        })

        //
        // Delete friend request
        .on('click', '.js-delete-friend-request', function(event) {
            event.preventDefault();
            var $deleteAction = $(".js-delete-friend-request"),
                objectUUID = $(this).data('uuid');
            $deleteAction.attr("disabled", "disabled");

            request.remove({url: "/v1/me/sent_friend_requests/" + objectUUID + "/"})
                .done(function(){
                    $(".js-delete-friend-request").hide();
                    var $friendAction = $(".js-send-friend-request");
                    $friendAction.show();
                    $friendAction.removeAttr("disabled");
                });
        })
        //
        // Send Friend Request.
        .on('click', 'button.js-send-friend-request', function(event) {
            event.preventDefault();
            var sendRequest = $("button.js-send-friend-request");
            sendRequest.attr("disabled", "disabled");

            request.post({
                url: "/relationships/create_friend_request/",
                data: JSON.stringify({
                    'from_username': $(this).data('from_username'),
                    'to_username': $(this).data('to_username')
                })
            }).done(function(data){
                if (data.action === true) {
                    sendRequest.hide();
                    var deleteFriend = $(".js-delete-friend-request");
                    deleteFriend.data('uuid', data.friend_request_id);
                    deleteFriend.removeAttr("disabled");
                    deleteFriend.show();
                }
            }).fail(function(jqXHR, textStatus, errorThrown){
                if (jqXHR.status === 500) {
                    sendRequest.removeAttr("disabled");
                }
            });
        });
}