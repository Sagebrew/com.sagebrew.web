var request = require('api').request,
    unverifiedMissionTemplate = require('controller/council/templates/unverified_missions.hbs'),
    moment = require('moment');


export const meta = {
    controller: "council/unverified_missions",
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
    request.get({url: '/v1/council/missions/'})
        .done(function(data) {
            $missionWrapper.append(unverifiedMissionTemplate({missions: data}));
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