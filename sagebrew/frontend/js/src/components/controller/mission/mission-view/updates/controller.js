var updates = require('./partials/updates');

export const meta = {
    controller: "mission/mission-view/updates",
    match_method: "path",
    check: [
       "^missions\/[A-Za-z0-9.@_%+-]{36}\/[A-Za-z0-9.@_%+-]{1,140}\/updates"
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
    updates.load();
}

/**
 * Post Load
 */
export function postload() {
    //
    // Intercom Tracking
}