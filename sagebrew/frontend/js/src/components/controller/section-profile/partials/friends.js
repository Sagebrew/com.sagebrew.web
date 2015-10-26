/**
 * @file
 * Do things with friends.
 */
var request = require('./../../../api').request,
    helpers = require('./../../../common/helpers');

require('./../../../plugin/contentloader');

export function init() {
    var $app = $(".app-sb");
    var $appFriends = $(".app-friends");

    // Load Friends.
    var profile_page_user = helpers.args(1);
    $appFriends.sb_contentLoader({
        emptyDataMessage: 'Please use search to find your friends :)',
        url: '/v1/profiles/' + profile_page_user + '/friends/',
        params: {
            expand: 'true',
            expedite: 'true',
            html: 'true'
        },
        dataCallback: function(base_url, params) {
            var urlParams = $.param(params);
            var url;
            if (urlParams) {
                url = base_url + "?" + urlParams;
            }
            else {
                url = base_url;
            }

            return request.get({url:url});

        },
        renderCallback: function($container, data) {
            $.each(data.results, function (i, l) {
                $container.append(l);
            });
        }
    });



    //Friend Action binding.
    //TODO: this is a lot of repeated code from the nav app. We should
    //      consolidate.
    $app
        //
        // Add overlays to non-friend page for descriptions of what the different
        // pieces do
        .on('mouseenter', ".js-hover-overlay-activate", function(event) {
            event.preventDefault();
            var $this = $(this),
            overlay = $this.parent().parent().find(".sb-overlay");
            overlay.height($this.height());
            overlay.fadeIn('fast');
        })

        //
        // Remove overlay when mouse leaves card region
        .on('mouseleave', '.sb-overlay', function(event) {
            event.preventDefault();
            $(this).fadeOut('fast');
            $(".sb-profile-not-friend-element-image").removeClass("active");
        })

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
            }).fail(function(jqXHR){
                if (jqXHR.status === 500) {
                    sendRequest.removeAttr("disabled");
                }
            });
        });
}