var args = require('common/helpers').args,
    mapLocation = require('common/static_map'),
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
    mapLocation.init("/v1/questions/" + args(1) + "/?expedite=true", "map", false);
    solution.load();
    question.load();
}

