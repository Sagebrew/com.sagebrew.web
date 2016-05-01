var politician = require('./partials/politicianmission');

export const meta = {
    controller: "mission/registration/political-mission",
    match_method: "path",
    check: [
       "^missions/public_office$"
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