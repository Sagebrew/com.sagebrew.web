/**
 * @file
 * Authed User Controller. Loaded on every page loaded by a logged in user.
 */
var navbar = require('./partials/navbar').initNavbar,
    settings = require('settings').settings,
    request = require('api').request;


/**
 * Meta.
 */
export const meta = {
    controller: "user-auth",
    match_method: "user",
    check: "auth"
};


/**
 * Load
 */
export function load() {
    navbar();
    var $app = $(".app-sb"),
        greyPage = document.getElementById('sb-greyout-page');
    $app
        .on('click', '.js-quest-signup', function(event) {
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
