// TODO this could be split into seperate dirs within the quest section
// based on the new layout @mwisner is working on in #720
var missionSelect = require('./partials/missionselect');

export const meta = {
    controller: "mission/select-mission",
    match_method: "path",
    check: [
       "^quest/mission/select$"
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
    missionSelect.load();

}

/**
 * Post Load
 */
export function postload() {
    //
    // Intercom Tracking
}