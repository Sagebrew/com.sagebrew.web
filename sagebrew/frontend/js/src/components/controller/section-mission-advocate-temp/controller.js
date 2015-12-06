// TODO this could be split into seperate dirs within the quest section
// based on the new layout @mwisner is working on in #720
var advocate = require('./partials/advocatemission');

export const meta = {
    controller: "section-mission-advocate-temp",
    match_method: "path",
    check: [
       "^quest/mission/advocate"
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
    advocate.load();

}

/**
 * Post Load
 */
export function postload() {
    //
    // Intercom Tracking
}