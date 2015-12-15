/**
 * @file
 * Authed User Controller. Loaded on every page loaded by a logged in user.
 */
var navbar = require('./partials/navbar').initNavbar,
    request = require('./../../api').request;

export function init() {

    $(document).ready(function() {
        navbar();
    });

}


