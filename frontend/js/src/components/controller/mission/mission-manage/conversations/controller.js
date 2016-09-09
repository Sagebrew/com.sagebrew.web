var request = require('api').request,
    questionSummaryTemplate = require('../../../conversation/conversation-list/templates/question_summary.hbs'),
    moment = require('moment'),
    helpers = require('common/helpers');

export const meta = {
    controller: "mission/mission-manage/conversations",
    match_method: "path",
    check: [
        "^missions\/[A-Za-z0-9.@_%+-]{36}\/[A-Za-z0-9.@_%+-]{1,70}\/manage\/conversations$"
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
    console.log('here');
    if ($conversationWrapper !== undefined && $conversationWrapper !== null){
        console.log('there');
        $conversationWrapper.sb_contentLoader({
            emptyDataMessage: 'There is nothing here',
            loadingMoreItemsMessage: 'Loading some more',
            url: '/v1/questions/',
            params: {
                mission: missionId
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
                console.log(data);
                console.log($container);
                for (var i = 0; i < data.count; i++) {
                    data.results[i].created = moment(data.results[i].created).format("dddd, MMMM Do YYYY, h:mm a");
                    $container.append(questionSummaryTemplate(data.results[i]));
                }
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