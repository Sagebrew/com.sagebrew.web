/**
 * @file
 * Manage following and unfollowing users.
 */
var request = require('./../../../api').request,
    helpers = require('./../../../common/helpers');

require('./../../../plugin/contentloader');

export function init() {
    var $app = $(".app-sb"),
        profilePageUser = helpers.args(1);


    //Friend Action binding.
    //TODO: this is a lot of repeated code from the nav app. We should
    //      consolidate.
    $app

        //
        // Delete friend request
        .on('click', '#js-follow', function (event) {
            event.preventDefault();
            var $deleteAction = $(".js-delete-friend-request");
            $deleteAction.attr("disabled", "disabled");

            request.post({
                url: "/v1/profiles/" + profilePageUser + "/follow/"
            }).done(function () {
                    $("#js-follow").hide();
                    var $unfollow = $("#js-unfollow");
                    $unfollow.show();
                    $unfollow.removeAttr("disabled");
            });
        })
        //
        // Send Friend Request.
        .on('click', '#js-unfollow', function (event) {
            event.preventDefault();
            var $follow = $("#js-follow");
            $follow.attr("disabled", "disabled");

            request.post({
                url: "/v1/profiles/" + profilePageUser + "/unfollow/"
            }).done(function (data) {
                var $unfollow = $("#js-unfollow");
                $unfollow.hide();
                $follow.removeAttr("disabled");
                $follow.show();
            }).fail(function (jqXHR) {
                if (jqXHR.status === 500) {
                    $follow.removeAttr("disabled");
                }
            });
        });
}