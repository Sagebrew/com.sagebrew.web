/**
 * @file
 * Loaded on every page that is requested by an anon user.
 */

var loginform = require('./partials/loginform').initLoginForm,
    testPrivate = require('common/helpers').testPrivateBrowsing;


/**
 * Meta.
 */
export const meta = {
    controller: "user-anon",
    match_method: "user",
    check: "anon"
};

/**
 * Init
 */
export function init() {
    testPrivate();
    loginform();
}