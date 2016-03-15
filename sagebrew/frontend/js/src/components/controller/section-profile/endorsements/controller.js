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
    var username = getArgs(1),
        endorsementWrapper = $("#endorsements_wrapper");
    if (endorsementWrapper !== undefined && endorsementWrapper !== null){
        endorsementWrapper.sb_contentLoader({
            emptyDataMessage: templates.position_holder({static_url: settings.static_url}),
            url: '/v1/profiles/' + username + '/endorsed/',
            dataCallback: function(base_url, params) {
                var urlParams = $.param(params);
                var url;
                if (urlParams) {
                    url = base_url + "?" + urlParams;
                }
                else {
                    url = base_url;
                }
                return request.get({url:url});

            },
            renderCallback: function($container, data) {
                for (var i = 0; i < data.length; i++) {
                    $container.append(templates.quest_endorsed(data[i]));
                }
            }
        });
    }
}

/**
 * Post Load
 */
export function postload() {
    //
    // Intercom Tracking
}