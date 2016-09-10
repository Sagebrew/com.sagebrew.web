var request = require('api').request,
    questionSummaryTemplate = require('../../../conversation/conversation-list/templates/question_summary.hbs'),
    helpers = require('common/helpers');

export const meta = {
    controller: "mission/mission-view/conversations",
    match_method: "path",
    check: [
        "^missions\/[A-Za-z0-9.@_%+-]{36}\/[A-Za-z0-9.@_%+-]{1,70}\/conversations$"
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
    var missionId = helpers.args(1),
        $conversationWrapper = $("#js-conversation-wrapper");
    if ($conversationWrapper !== undefined && $conversationWrapper !== null){
        $conversationWrapper.sb_contentLoader({
            emptyDataMessage: 'There is nothing here',
            loadingMoreItemsMessage: 'Loading some more',
            url: '/v1/questions/',
            params: {
                mission: missionId,
                expand: true
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
                $container.append(questionSummaryTemplate({conversations: data.results}));
                helpers.disableFigcapEditing($container);
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