/**
 * @file
 * Primary JS file that is loaded on every page.
 */

var app_settings = require('./components/settings').settings,
    router = require('./components/router');

var ctrls = router.controllers();
if (ctrls.length) {

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

/**
 * I'm not sure if this is valid.
 */
export const settings = app_settings;