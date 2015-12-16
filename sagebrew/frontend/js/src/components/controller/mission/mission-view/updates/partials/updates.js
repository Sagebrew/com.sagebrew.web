var request = require('api').request,
    templates = require('template_build/templates'),
    settings = require('settings').settings,
    helpers = require('common/helpers');


export function load() {
    var $app = $(".app-sb"),
        missionId = window.location.pathname.match("([A-Za-z0-9.@_%+-]{36})")[0],
        $updateWrapper = $("#js-update-wrapper");

    if ($updateWrapper !== undefined && $updateWrapper !== null){
        $updateWrapper.sb_contentLoader({
            emptyDataMessage: '',
            url: '/v1/missions/' + missionId + '/updates/render/',
            params: {
                expand: 'true',
                about_type: 'mission'
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
                for (var i = 0; i < data.count; i++) {
                    $container.append(data.results.html[i]);
                }
            }
        });
    }

    $app.on('click', '.edit-update', function () {
        event.preventDefault();
        window.location.href = "/quests/" + missionId + "/updates/" + $(this).data('object_uuid') + "/edit/";
    });

}