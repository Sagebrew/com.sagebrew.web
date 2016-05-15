var missionSelect = require('./partials/missionselect');

export const meta = {
    controller: "mission/registration/select-mission",
    match_method: "path",
    check: [
       "^missions/select$"
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