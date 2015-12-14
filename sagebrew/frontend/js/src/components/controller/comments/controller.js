/**
 * @file
 */
var comments = require('./partials/comments');


/**
 * Meta.
 */
export const meta = {
    controller: "comments",
    match_method: "path",
    check: [
        "^conversations/[A-Za-z0-9.@_%+-]{36}\/",
        "^user/newsfeed$",
        "^user/[A-Za-z0-9.@_%+-]{2,36}"
    ]
};


/**
 * Load.
 */
export function load() {
    comments.load();
}