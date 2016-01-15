var helpers = require('common/helpers'),
    request = require('api').request;

export function load() {
    var followButton = document.getElementById('js-follow-btn'),
        app = $(".app-sb"),
        followText,
        questId;

    app.on('click', "#js-follow-btn", function() {
        followText = followButton.innerText.toLowerCase();
        questId = helpers.args(1);
        followButton.disabled = true;
        request.post({url:"/v1/quests/" + questId + "/" + followText + "/"})
            .done(function() {
                followButton.disabled = false;
                if (followText === "follow") {
                    followButton.innerText = "Unfollow";
                } else {
                    followButton.innerText = "Follow";
                }
            });
    });
}