var interests = require('./partials/interests');

export const meta = {
    controller: "registration",
    match_method: "path",
    check: [
       "^registration/interests",
        "^registration/profile_information",
        "^registration/profile_picture"
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
    interests.load();
}

/**
 * Post Load
 */
export function postload() {
    //
    // Intercom Tracking
}