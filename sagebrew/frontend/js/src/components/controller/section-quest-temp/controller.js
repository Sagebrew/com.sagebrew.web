// TODO this could be split into seperate dirs within the quest section
// based on the new layout @mwisner is working on in #720
var quest = require('./partials/quest');

export const meta = {
    controller: "section-quest-temp",
    match_method: "path",
    check: [
       "^quests/\/([A-Za-z0-9.@_%+-]{2,36})"
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
    "use strict";
    quest.load();
}

/**
 * Post Load
 */
export function postload() {
    //
    // Intercom Tracking
}