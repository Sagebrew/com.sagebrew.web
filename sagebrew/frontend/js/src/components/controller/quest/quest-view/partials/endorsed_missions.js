var helpers = require('common/helpers'),
    request = require('api').request,
    settings = require('settings').settings,
    templates = require('template_build/templates');

export function load() {
    var app = $(".app-sb"),
        questId = helpers.args(1),
        $container = $("#js-endorsed-mission-container");
    request.get({url:"/v1/quests/" + questId + "/endorsed/"})
        .done(function(data) {
            $(".loader").remove();
            if (data.length > 0) {
                for (var i = 0; i < data.length; i++) {
                    $container.append(templates.quest_endorsed(data[i]));
                }
            } else {
                $container.append(templates.position_holder({static_url: settings.static_url}));
            }
        });
}