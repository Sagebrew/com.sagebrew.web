// TODO this could be split into seperate dirs within the quest section
// based on the new layout @mwisner is working on in #720
var politician = require('./partials/politicianmission'),
    mission = require('./partials/missionselect');

export const meta = {
    controller: "registration",
    match_method: "path",
    check: [
       "^quest/mission/public_office",
       "^quest/mission" // TODO this could be moved to a seperate controller/dir
                        // based on the new layout @mwisner is working on in #720
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
    "use strict";
    mission.load();
    politician.load();
}

/**
 * Post Load
 */
export function postload() {
    //
    // Intercom Tracking
}