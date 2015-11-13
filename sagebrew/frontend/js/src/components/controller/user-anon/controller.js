/**
 * @file
 * Loaded on every page that is requested by an anon user.
 */

var loginform = require('./partials/loginform').initLoginForm;



export function init() {
    loginform();
}