var request = require('api').request,
    markdown = require('common/markdown').addMarkdown,
    updateNewsTemplate = require('controller/section-profile/templates/update_news.hbs');

export const meta = {
    controller: "mission/mission-manage/updates",
    match_method: "path",
    check: [
        "^missions\/[A-Za-z0-9.@_%+-]{36}\/[A-Za-z0-9.@_%+-]{1,140}\/manage\/updates$"
    ]
};


/**
 * Init
 */
export function init() {

}

/**
 * Load
 */
export function load() {
    require('plugin/contentloader');
    var $app = $(".app-sb"),
        missionId = window.location.pathname.match("([A-Za-z0-9.@_%+-]{36})")[0],
        $updateWrapper = $("#js-update-wrapper");
    markdown($("textarea.markdown-input"));
    $app
        .on('click', '#submit', function(event) {
            event.preventDefault();
            var form = document.getElementById('updateForm');
            var data = {};
            for (var i = 0, ii = form.length; i < ii; ++i) {
                var input = form[i];
                // Don't check the value because if the use has entered a value
                // we prepopulate it. So if they remove it we want to set it to
                // an empty string in the backend.
                if (input.name) {
                  data[input.name] = input.value;
                }
            }
            data.about_type = "mission";
            data.about_id = missionId;
            if('content' in data && 'title' in data){
                request.post({url: "/v1/missions/" + missionId + "/updates/",
                    data: JSON.stringify(data)
                }).done(function (){
                    window.location.reload();
                });
            }

        });

    if ($updateWrapper !== undefined && $updateWrapper !== null){
        $updateWrapper.sb_contentLoader({
            emptyDataMessage: '',
            url: '/v1/missions/' + missionId + '/updates/',
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
                    $container.append(updateNewsTemplate(data.results[i]));
                }
            }
        });
    }
}

/**
 * Post Load
 */
export function postload() {
    //
    // Intercom Tracking
}