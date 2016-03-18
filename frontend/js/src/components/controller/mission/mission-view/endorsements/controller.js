var request = require('api').request,
    endorsementBtnTemplate = require('common/templates/endorsement_button.hbs');

export const meta = {
    controller: "mission/mission-view/endorsements",
    match_method: "path",
    check: [
       "^missions\/[A-Za-z0-9.@_%+-]{36}\/[A-Za-z0-9.@_%+-]{1,140}\/endorsements$"
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
    require('common/handlebars_helpers');
    var missionId = window.location.pathname.match("([A-Za-z0-9.@_%+-]{36})")[0],
        $endorsementWrapper = $("#js-endorsement-wrapper");
    if ($endorsementWrapper !== undefined && $endorsementWrapper !== null){
        $endorsementWrapper.sb_contentLoader({
            emptyDataMessage: '',
            url: '/v1/missions/' + missionId + '/endorsements/',
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
                    $container.append(endorsementBtnTemplate(data.results[i]));
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