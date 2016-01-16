var helpers = require('common/helpers'),
    request = require('api').request;

export function load() {
    var followButtons = document.getElementsByClassName('js-follow-btn'),
        app = $(".app-sb"),
        followText,
        questId;
    console.log(followButtons)
    app.on('click', ".js-follow-btn", function() {
        for (var i = 0; i < followButtons.length; i++) {
            followText = followButtons[i].innerText.toLowerCase();
            followButtons[i].disabled = true;
        }
        questId = helpers.args(1);
        request.post({url:"/v1/quests/" + questId + "/" + followText + "/"})
            .done(function() {
                for (i = 0; i < followButtons.length; i++) {
                    followButtons[i].disabled = false;
                }
                if (followText === "follow") {
                    for (i = 0; i < followButtons.length; i++) {
                        followButtons[i].innerText = "Unfollow";
                    }
                } else {
                    for (i = 0; i < followButtons.length; i++) {
                        followButtons[i].innerText = "Follow";
                    }
                }
            });
    });
}