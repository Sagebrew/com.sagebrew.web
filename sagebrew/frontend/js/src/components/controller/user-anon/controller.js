/**
 * @file
 * Global SB controller. Loaded on every page.
 */

var loginform = require('./partials/loginform').initLoginForm;



export function init() {
    loginform();
    console.log("Anon Controller Loaded");
}