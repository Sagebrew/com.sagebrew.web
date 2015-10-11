/**
 * @file
 * Used on every page with an anon user.
 */

var userAnonInit = require('./components/init').userAnonInit;
var loginform = require('./components/authed/navbar').initLoginForm;

//Init various things for anon user.
userAnonInit();
loginform();


