var request = require('api').request,
    reviewMissionTemplate = require('controller/council/templates/review_mission.hbs'),
    args = require('common/helpers').args,
    getCheckboxes = require('common/helpers').getCheckedBoxes;


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
        missionId = args(2),
        $app = $(".app-sb");
    request.get({url: "/v1/missions/" + missionId + "/"})
        .done(function(data) {
            $missionWrapper.prepend(reviewMissionTemplate(
                {mission: data, review_string:"Submitted for Review"}));
        });
    $app
        .on('click', '#js-submit-initial', function(e) {
            e.preventDefault();
            $("#js-review-modal").modal();
        })
        .on('click', '#js-submit-review', function(e) {
            e.preventDefault();
            var data = {
                'review_feedback': getCheckboxes('feedbackItem')
            };
            request.patch(
                {
                    url: '/v1/missions/' + missionId + '/review/',
                    data: JSON.stringify(data)
                }
            ).done(function() {
                window.history.back();
            });
        });
}

/**
 * Post Load
 */
export function postload() {
    //
    // Intercom Tracking
}
