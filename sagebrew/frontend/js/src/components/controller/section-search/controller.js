var interests = require('common/helpers.js'),
    submitSearch = require('./partials/search').submitSearch;

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
    submitSearch()
}

/**
 * Post Load
 */
export function postload() {
    //
    // Intercom Tracking
}
