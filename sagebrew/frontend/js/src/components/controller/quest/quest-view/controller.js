/**
 * @file
 */
var request = require('api').request;


/**
 * Meta.
 */
export const meta = {
    controller: "quest/quest-view",
    match_method: "path",
    check: [
        "^quests\/[A-Za-z0-9.@_%+-]{1,36}\/updates$",
        "^quests\/[A-Za-z0-9.@_%+-]{1,36}$",
        "^quests\/[A-Za-z0-9.@_%+-]{1,36}\/insights$"
    ]
};


/**
 * Load.
 */
export function load() {
    console.log("quest-view");
}