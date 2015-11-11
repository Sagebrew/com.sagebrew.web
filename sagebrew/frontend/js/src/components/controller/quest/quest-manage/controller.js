/**
 * @file
 */
var request = require('api').request;


/**
 * Meta.
 */
export const meta = {
    controller: "quest/quest-manage",
    match_method: "path",
    check: [
       "^quests\/[A-Za-z0-9.@_%+-]{1,36}\/manage"
    ]
};


/**
 * Load.
 */
export function load() {
    console.log("quest-manage");
}