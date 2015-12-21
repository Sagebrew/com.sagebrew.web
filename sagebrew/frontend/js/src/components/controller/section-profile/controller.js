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
    follow = require('./partials/follow'),
    request = require('api').request,
    settings = require('settings').settings;

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
    var $app = $(".app-sb");
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
    $app
        .on('click', '#js-quest-signup', function(event) {
            event.preventDefault();
            request.post({url: "/v1/quests/", data: {}})
                .done(function () {
                    window.location.href("/quests/" + settings.user.username)
                });
        });
}

/**
 * Post Load
 */
export function postload() {
    //
    // Intercom Tracking
}