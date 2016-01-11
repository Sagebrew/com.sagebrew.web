var helpers = require('common/helpers'),
    request = require('api').request;

export function load() {
    var followButton = $(".js-follow-btn"),
        app = $(".app-sb"),
        followText,
        questId;

    app.on('click', ".js-follow-btn", function() {
        followText = followButton.text().toLowerCase();
        questId = helpers.args(1);
        request.post({url:"/v1/quests/" + questId + "/" + followText + "/"})
            .done(function() {
                if (followText === "follow") {
                    followButton.text("Unfollow");
                } else {
                    followButton.text("Follow");
                }
            });
    });
}