/**
 * @file
 * Authed User Controller. Loaded on every page loaded by a logged in user.
 */
var navbar = require('./partials/navbar').initNavbar;


/**
 * Meta.
 */
export const meta = {
    controller: "user-auth",
    match_method: "user",
    check: "auth"
};


/**
 * Load
 */
export function load() {
    navbar();
}

