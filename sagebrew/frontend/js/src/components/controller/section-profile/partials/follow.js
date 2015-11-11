/**
 * @file
 * Manage following and unfollowing users.
 */
var request = require('api').request,
    helpers = require('common/helpers');


export function init() {
    var $app = $(".sb-profile-not-friend-container"),
        profilePageUser = helpers.args(1);


    // (Un)follow user bindings
    $app
        //
        // Follow user
        .on('click', '#js-follow', function (event) {
            event.preventDefault();
            var $deleteAction = $(".js-delete-friend-request"),
                $follow = $("#js-follow");
            $deleteAction.attr("disabled", "disabled");

            request.post({
                url: "/v1/profiles/" + profilePageUser + "/follow/"
            }).done(function () {
                    $("#js-follow").hide();
                    var $unfollow = $("#js-unfollow");
                    $unfollow.show();
                    $unfollow.removeAttr("disabled");
            }).fail(function(jqXHR) {
                if (jqXHR.status === 500) {
                    $follow.removeAttr("disabled");
                }
            });
        })
        //
        // Unfollow user
        .on('click', '#js-unfollow', function (event) {
            event.preventDefault();
            var $follow = $("#js-follow"),
                $unfollow = $("#js-unfollow");
            $follow.attr("disabled", "disabled");

            request.post({
                url: "/v1/profiles/" + profilePageUser + "/unfollow/"
            }).done(function (data) {
                $unfollow.hide();
                $follow.removeAttr("disabled");
                $follow.show();
            }).fail(function (jqXHR) {
                if (jqXHR.status === 500) {
                    $unfollow.removeAttr("disabled");
                }
            });
        });
}