/**
 * @file
 * Primary JS file that is loaded on every page.
 * WIP JS Strategy. This is a WIP and may or may not even work.
 *
 *
 */

var helpers = require('./components/common/helpers'),
    app_settings = require('./components/settings').settings,
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


export const settings = app_settings;