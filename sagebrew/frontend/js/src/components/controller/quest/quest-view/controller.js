/**
 * @file
 */
var quest = require('./partials/quest');


/**
 * Meta.
 */
export const meta = {
    controller: "quest/quest-view",
    match_method: "path",
    check: [
        "^quests\/[A-Za-z0-9.@_%+-]{2,36}\/updates$",
        "^quests\/[A-Za-z0-9.@_%+-]{2,36}$",
        "^quests\/[A-Za-z0-9.@_%+-]{2,36}\/insights$"
    ]
};


/**
 * Load.
 */
export function load() {
    quest.load();
}