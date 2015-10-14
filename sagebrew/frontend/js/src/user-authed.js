/**
 * @file
 * Used on every page with an authed user.
 */

var userAuthedInit = require('./components/init').userAuthedInit;
var navbar = require('./components/authed/navbar').initNavbar;

// Init various things for authed user.
userAuthedInit();

$(document).ready(function() {
    navbar();
});