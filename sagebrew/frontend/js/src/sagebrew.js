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

var helpers = require('./components/common/helpers'),
    router = require('./components/router');

var ctrls = router.controllers();
if (ctrls.length) {
    for (var item in ctrls) {
        var controller = ctrls[item];
        if (controller.hasOwnProperty('init')) {
            controller.init();
        }
    }
}

/**
 * Real generic wrapper around ajax requests.
 * @param options
 * @returns {*}
 */
export const request = require('./components/common/resourcemethods');

/**
 * Resource Loader
 */
export const resource = require('./components/api');

