var request = require('api').request,
    reviewedMissionTemplate = require('controller/council/templates/reviewed_missions.hbs'),
    moment = require('moment');


export const meta = {
    controller: "council/unreviewed_missions",
    match_method: "path",
    check: [
        "^council\/missions$"
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
    var $missionWrapper = $("#js-mission-verification-wrapper");
    request.get({url: '/v1/missions/?submitted_for_review=true&active=false'})
        .done(function(data) {
            $missionWrapper.append(reviewedMissionTemplate({missions: data.results, review_string: "to be Reviewed"}));
            $('[data-toggle="tooltip"]').tooltip();
            $(".mission-created").each(function(){
                var $this = $(this),
                    momentTime = moment($this.html()).format("dddd, MMMM Do YYYY, h:mm a");
                $this.html(momentTime);
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