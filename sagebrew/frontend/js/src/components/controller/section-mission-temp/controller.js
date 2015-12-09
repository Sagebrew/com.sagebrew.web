// TODO this could be split into seperate dirs within the quest section
// based on the new layout @mwisner is working on in #720
var politician = require('./partials/politicianmission');

export const meta = {
    controller: "section-mission-temp",
    match_method: "path",
    check: [
       "^quest/mission/public_office"
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
    politician.load();
}

/**
 * Post Load
 */
export function postload() {
    //
    // Intercom Tracking
}