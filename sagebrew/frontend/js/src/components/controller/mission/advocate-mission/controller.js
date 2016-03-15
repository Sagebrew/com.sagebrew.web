var advocate = require('./partials/advocatemission');

export const meta = {
    controller: "mission/advocate-mission",
    match_method: "path",
    check: [
       "^missions/advocate$"
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