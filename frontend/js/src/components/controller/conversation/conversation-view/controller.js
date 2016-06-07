var mapLocation = require('./partials/map-location'),
    question = require('./partials/question'),
    solution = require('./partials/solution');



/**
 * Meta.
 */
export const meta = {
    controller: "conversation/conversation-view",
    match_method: "path",
    check: "^conversations\/[A-Za-z0-9.@_%+-]{36}\/"
};


/**
 * Load
 */
export function load() {
    // Sidebar
    mapLocation.init();
    solution.load();
    question.load();
}

