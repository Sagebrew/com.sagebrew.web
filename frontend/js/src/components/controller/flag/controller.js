/**
 * @file
 */
var flag = require('./partials/flag');


/**
 * Meta.
 */
export const meta = {
    controller: "flag",
    match_method: "path",
    check: [
        "^conversations/[A-Za-z0-9.@_%+-]{36}\/",
        "^user/newsfeed$",
        "^user/[A-Za-z0-9.@_%+-]{2,36}",
        "^questions|solutions|posts\/[A-Za-z0-9.@_%+-]{2,36}$"
    ]
};


/**
 * Load.
 */
export function load() {
    flag.load();
}