var request = require('api').request,
    updateNewsTemplate = require('controller/section-profile/templates/update_news.hbs'),
    moment = require('moment'),
    helpers = require('common/helpers');

export const meta = {
    controller: "mission/mission-manage/updates",
    match_method: "path",
    check: [
        "^missions\/[A-Za-z0-9.@_%+-]{36}\/[A-Za-z0-9.@_%+-]{1,70}\/manage\/updates$"
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
    var missionId = window.location.pathname.match("([A-Za-z0-9.@_%+-]{36})")[0],
        $updateWrapper = $("#js-update-wrapper");

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
                    data.results[i].created = moment(data.results[i].created).format("dddd, MMMM Do YYYY, h:mm a");
                    $container.append(updateNewsTemplate(data.results[i]));
                }
                helpers.disableFigcapEditing();
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