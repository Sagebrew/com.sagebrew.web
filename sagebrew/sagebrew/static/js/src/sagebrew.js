/**
 * @file
 * Primary JS file that is loaded on every page.
 * WIP JS Strategy. This is a WIP and may or may not even work.
 *
 * JS Scopes:
 * Global: JS that is included on every page.
 * User: JS that is included on every page, but depends on if the user is auth or anon.
 * Section: JS that is only included on a specific section of the site.
 *
 * This file handles the global scope.
 *
 */

var globalInit = require('./components/init').globalInit;
var test = require('./components/core').test;

//
// init page.
globalInit();

console.log(test());

export function abcd() {
    return test();
}