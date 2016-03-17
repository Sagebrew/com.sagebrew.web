var helpers = require('common/helpers'),
    request = require('api').request,
    settings = require('settings').settings,
    positionHolderTemplate = require('controller/mission/political-mission/templates/position_holder.hbs'),
    endorsementTemplate = require('common/templates/quest_endorsed.hbs');

export function load() {
    var questId = helpers.args(1),
        $container = $("#js-endorsed-mission-container");
    if ($container !== undefined && $container !== null){
        $container.sb_contentLoader({
            emptyDataMessage: positionHolderTemplate({static_url: settings.static_url}),
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
                    $container.append(endorsementTemplate(data.results[i]));
                }
            }
        });
    }
}