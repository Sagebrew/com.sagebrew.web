/**
 * @file
 * JS for the entire user area.
 * TODO: Rename controller.
 * Profile is really one specific page in this section.
 */
var loader = require('./partials/single-object-loader');


export const meta = {
    controller: "section-single-object-page",
    match_method: "path",
    check: [
        "^questions|solutions|posts\/[A-Za-z0-9.@_%+-]{2,36}$"
    ],
    does_not_include: [
        'edit',
        'help\/'
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
    // Single content loader
    loader.init();
}

