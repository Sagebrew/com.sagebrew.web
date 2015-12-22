var interests = require('common/helpers.js'),
    searchFunc = require('./partials/search');

export const meta = {
    controller: "section-search",
    match_method: "path",
    check: [
       "^search"
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
    searchFunc.submitSearch();
    searchFunc.switchSearchFilter();
}

/**
 * Post Load
 */
export function postload() {
    //
    // Intercom Tracking
}
