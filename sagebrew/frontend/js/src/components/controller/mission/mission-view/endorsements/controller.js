var request = require('api').request,
    templates = require('template_build/templates'),
    handlebarsHelpers = require('common/handlebars_helpers').installHandleBarsHelpers;

export const meta = {
    controller: "mission/mission-view/endorsements",
    match_method: "path",
    check: [
       "^missions\/[A-Za-z0-9.@_%+-]{36}\/[A-Za-z0-9.@_%+-]{1,140}\/endorsements"
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
    var missionId = window.location.pathname.match("([A-Za-z0-9.@_%+-]{36})")[0],
        $endorsementWrapper = $("#js-endorsement-wrapper");
    if ($endorsementWrapper !== undefined && $endorsementWrapper !== null){
        handlebarsHelpers();
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
                for (var i = 0; i < data.length; i++) {
                    $container.append(templates.endorsement_button(data[i]));
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