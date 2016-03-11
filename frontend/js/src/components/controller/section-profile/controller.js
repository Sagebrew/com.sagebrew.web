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
    solutions = require('controller/conversation/conversation-view/partials/solution'),
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
    var $app = $(".app-sb"),
        greyPage = document.getElementById('sb-greyout-page');
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
    postcreate.load();
    solutions.load();
    $app
        .on('click', '#js-quest-signup', function(event) {
            event.preventDefault();
            greyPage.classList.remove('sb_hidden');
            if(settings.profile.quest !== null){
                greyPage.classList.add('sb_hidden');
                window.location.href = "/missions/select/";
            } else {
                request.post({url: "/v1/quests/", data: {}})
                    .done(function () {
                        greyPage.classList.add('sb_hidden');
                        window.location.href = "/missions/select/";
                    });
            }
        });
}

/**
 * Post Load
 */
export function postload() {
    //
    // Intercom Tracking
}