var locations = require('./partials/locations'),
    questionCreate = require('./partials/questioncreate');

/**
 * Init
 */
export function init() {

}

/**
 * Load
 */
export function load() {
    // Sidebar
    questionCreate.init();
    locations.init();
}

/**
 * Post Load
 */
export function postload() {
    //
    // Intercom Tracking
}