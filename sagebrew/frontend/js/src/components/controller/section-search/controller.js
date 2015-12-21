var interests = require('../common/helpers.js');

export const meta = {
    controller: "section-search",
    match_method: "path",
    check: [
       "^search"
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
