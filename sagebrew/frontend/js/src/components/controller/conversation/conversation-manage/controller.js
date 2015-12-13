var locations = require('./partials/locations'),
    questionCreate = require('./partials/questioncreate');

/**
 * Meta.
 */
export const meta = {
    controller: "section-conversation-manage",
    match_method: "path",
    check: [
        "^conversations\/questions\/[A-Za-z0-9.@_%+-]{36}\/edit",
        "^conversations/submit_question"
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
    // Sidebar
    questionCreate.init();
    locations.init();
}

/**
 * Post Load
 */
export function postload() {
    //
    // Intercom Tracking
}