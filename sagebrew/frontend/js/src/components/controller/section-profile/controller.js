/**
 * @file
 * JS for the entire profile area.
 */

/**
 * @file
 * -- Contains all functionality for the profile section.
 */
var representatives = require('./partials/representatives'),
    friends = require('./partials/friends');

export function init() {
    $(document).ready(function(){
        representatives.init();
        friends.init();
    });
}

