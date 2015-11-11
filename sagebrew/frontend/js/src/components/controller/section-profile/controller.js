/**
 * @file
 * JS for the entire user area.
 * TODO: Rename controller.
 * Profile is really one specific page in this section.
 */
var representatives = require('./partials/representatives'),
    friends = require('./partials/friends'),
    postcreate = require('./partials/postcreate'),
    profile = require('./partials/profile'),
    newsfeed = require('./partials/newsfeed'),
    follow = require('./partials/follow');

/**
 * Meta.
 */
export const meta = {
    controller: "section-profile",
    match_method: "path",
    check: "^user"
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
    // Sidebar
    representatives.init();
    // Friends Page
    friends.init();
    // Post create functionality.
    postcreate.init();
    // Profile page.
    profile.init();
    // Newsfeed page.
    newsfeed.init();
    // Follow functionality
    follow.init();
}

/**
 * Post Load
 */
export function postload() {
    //
    // Intercom Tracking
}