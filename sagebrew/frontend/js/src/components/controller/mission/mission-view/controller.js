var wallpaper = require('./partials/wallpaper'),
    endorse = require('./partials/endorse');

export const meta = {
    controller: "mission/mission-view",
    match_method: "path",
    check: [
       "^missions\/[A-Za-z0-9.@_%+-]{36}\/"
    ]
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
    $('[data-toggle="tooltip"]').tooltip();
    $('[data-toggle="popover"]').popover();
    wallpaper.load();
    endorse.load();
}

/**
 * Post Load
 */
export function postload() {
    //
    // Intercom Tracking
}