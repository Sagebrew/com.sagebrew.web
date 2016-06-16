var wallpaper = require('./partials/wallpaper'),
    helpers = require('common/helpers'),
    maps = require('common/static_map').init;

export const meta = {
    controller: "mission/mission-view",
    match_method: "path",
    check: [
       "^missions\/[A-Za-z0-9.@_%+-]{36}\/[A-Za-z0-9.@_%+-]{1,70}$"
    ],
    does_not_include: ['advocate', 'public_office', 'select', 'account']
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
    var missionID = helpers.args(1);
    $('[data-toggle="tooltip"]').tooltip();
    $('[data-toggle="popover"]').popover();
    wallpaper.load();
    helpers.disableFigcapEditing($(".block"));
    maps("/v1/missions/" + missionID + "/", "#map");
}

/**
 * Post Load
 */
export function postload() {
    //
    // Intercom Tracking
}