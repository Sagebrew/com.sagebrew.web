/**
 * @file
 * JS for the entire user area.
 * TODO: Rename controller.
 * Profile is really one specific page in this section.
 */
var request = require('api').request,
    settings = require('settings').settings,
    getArgs = require('common/helpers').args,
    templates = require('template_build/templates'),
    handlebarsHelpers = require('common/handlebars_helpers').installHandleBarsHelpers;

/**
 * Meta.
 */
export const meta = {
    controller: "section-profile/endorsements",
    match_method: "path",
    check: "^user/[A-Za-z0-9.@_%+-]{1,30}/endorsements$"
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
        greyPage = document.getElementById('sb-greyout-page'),
        username = getArgs(1),
        endorsementWrapper = $("#endorsements_wrapper");
    request.get({url:"/v1/profiles/" + username + "/endorsed/"})
        .done(function(data) {
            handlebarsHelpers();
            for (var i = 0; i < data.length; i++) {
                endorsementWrapper.append(templates.quest_endorsed(data[i]));
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