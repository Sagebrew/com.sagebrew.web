var mapLocation = require('./partials/map-location'),
    question = require('./partials/question');

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
    question.load();
    mapLocation.init();
}

/**
 * Post Load
 */
export function postload() {
    //
    // Intercom Tracking
}