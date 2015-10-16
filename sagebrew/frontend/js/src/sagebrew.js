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
    //
    // I don't know how useful this is. but lets give it a shot.
    // It's javascript. Everyone gets to do it differently.

    //
    // Init...
    for (var item in ctrls) {
        if (ctrls.hasOwnProperty(item)) {
            var controller = ctrls[item];
            if (controller.hasOwnProperty('init')) {
                controller.init();
            }
        }
    }

    //
    // Load
    $(document).ready(function() {
        for (var item in ctrls) {
            if (ctrls.hasOwnProperty(item)) {
                var controller = ctrls[item];
                if (controller.hasOwnProperty('load')) {
                    controller.load();
                }
            }
        }
    });

    // postLoad
    for (var item in ctrls) {
        if (ctrls.hasOwnProperty(item)) {
            var controller = ctrls[item];
            if (controller.hasOwnProperty('postload')) {
                controller.postload();
            }
        }
    }

}


export const settings = app_settings;