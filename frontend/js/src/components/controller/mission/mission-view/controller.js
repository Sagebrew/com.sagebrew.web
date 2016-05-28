var wallpaper = require('./partials/wallpaper');

export const meta = {
    controller: "mission/mission-view",
    match_method: "path",
    check: [
       "^missions\/[A-Za-z0-9.@_%+-]{36}\/"
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
    $('[data-toggle="tooltip"]').tooltip();
    $('[data-toggle="popover"]').popover();
    wallpaper.load();
}

/**
 * Post Load
 */
export function postload() {
    //
    // Intercom Tracking
}