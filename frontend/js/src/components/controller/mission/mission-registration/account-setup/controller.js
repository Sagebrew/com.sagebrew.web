var advocate = require('./partials/advocatemission');

export const meta = {
    controller: "mission/mission-registration/account-setup",
    match_method: "path",
    check: [
       "^missions/account"
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