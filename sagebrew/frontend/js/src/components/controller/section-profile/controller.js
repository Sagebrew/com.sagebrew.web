/**
 * @file
 * JS for the entire profile area.
 */
var representatives = require('./partials/representatives'),
    friends = require('./partials/friends'),
    posts = require('./partials/posts');


/**
 * Init
 */
export function init() {

}

/**
 * Load
 */
export function load() {
    representatives.init();
    friends.init();
    posts.init();
}

/**
 * Post Load
 */
export function postload() {
    //
    // Intercom Tracking
    Intercom('trackEvent', 'visited-profile-page');
}