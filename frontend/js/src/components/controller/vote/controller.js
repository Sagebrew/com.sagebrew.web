/**
 * @file
 */
var vote = require('./partials/vote');


/**
 * Meta.
 */
export const meta = {
    controller: "vote",
    match_method: "path",
    check: [
        "^conversations/[A-Za-z0-9.@_%+-]{36}\/",
        "^conversations$",
        "^user/newsfeed$",
        "^user/[A-Za-z0-9.@_%+-]{2,36}",
        "^questions|solutions|posts\/[A-Za-z0-9.@_%+-]{2,36}$"
    ]
};


/**
 * Load.
 */
export function load() {
    vote.load();
}