var mapLocation = require('./partials/map-location'),
    question = require('./partials/question');

/**
 * Meta.
 */
export const meta = {
    controller: "section-conversation",
    match_method: "path",
    check: "^conversations\/([A-Za-z0-9.@_%+-]{36})\/"
};


/**
 * Load
 */
export function load() {
    // Sidebar
    question.load();
    mapLocation.init();
}

