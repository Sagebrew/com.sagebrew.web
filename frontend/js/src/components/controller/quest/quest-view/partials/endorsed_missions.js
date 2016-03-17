var helpers = require('common/helpers'),
    request = require('api').request,
    settings = require('settings').settings,
    templates = require('template_build/templates');

export function load() {
    var app = $(".app-sb"),
        questId = helpers.args(1),
        $container = $("#js-endorsed-mission-container");
    if ($container !== undefined && $container !== null){
        $container.sb_contentLoader({
            emptyDataMessage: templates.position_holder({static_url: settings.static_url}),
            url: '/v1/quests/' + questId + '/endorsed/',
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
                for (var i = 0; i < data.count; i++) {
                    $container.append(templates.quest_endorsed(data.results[i]));
                }
            }
        });
    }
}