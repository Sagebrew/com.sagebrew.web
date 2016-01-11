var missions = require('common/missions'),
    helpers = require('common/helpers'),
    request = require('api').request;

export function load() {
    var followButton = $(".js-follow-btn"),
        followText,
        questId;
    followButton.on('click', function() {
        followText = followButton.text().toLowerCase();
        questId = helpers.args(1);
        request.post({url:"/v1/quests/" + questId + "/" + followText + "/"})
            .done(function(data) {
                if (followText === "follow") {
                    followButton.text("Unfollow");
                } else {
                    followButton.text("Follow");
                }
            });
    });
}