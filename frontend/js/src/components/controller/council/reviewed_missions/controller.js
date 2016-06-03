var request = require('api').request,
    unverifiedMissionTemplate = require('controller/council/templates/reviewed_missions.hbs'),
    moment = require('moment');


export const meta = {
    controller: "council/reviewed_missions",
    match_method: "path",
    check: [
        "^council\/missions\/reviewed$"
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
    request.get({url: '/v1/missions/?submitted_for_review=true&active=true'})
        .done(function(data) {
            $missionWrapper.append(unverifiedMissionTemplate(
                {missions: data.results, review_string:"With Completed Reviews"}));
            $('[data-toggle="tooltip"]').tooltip();
            $(".mission-created").each(function(){
                var $this = $(this),
                    momentTime = moment($this.html()).format("dddd, MMMM Do YYYY, h:mm a");
                // format each of the element's created times into human readable time
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