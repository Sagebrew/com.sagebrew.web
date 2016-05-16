var request = require('api').request,
    reviewMissionTemplate = require('controller/council/templates/review_mission.hbs'),
    moment = require('moment'),
    args = require('common/helpers').args;


export const meta = {
    controller: "council/review_mission",
    match_method: "path",
    check: [
        "^council\/missions\/[A-Za-z0-9.@_%+-]{36}\/review$"
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
    var $missionWrapper = $("#js-mission-verification-wrapper"),
        missionId = args(2);
    request.get({url: "/v1/missions/" + missionId + "/"})
        .done(function(data) {
            $missionWrapper.prepend(reviewMissionTemplate({mission: data}));
        });
}

/**
 * Post Load
 */
export function postload() {
    //
    // Intercom Tracking
}
