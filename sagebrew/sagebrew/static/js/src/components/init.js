/**
 * @file
 * Init the SB website. This runs on all pages.
 */
var helpers = require('./helpers');

/**
 * Ajax Setup
 * -- Automatically add CSRF cookie value to all ajax requests.
 */
function ajaxSetup() {
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!helpers.csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", helpers.getCookie('csrftoken'));
            }
        }
    });
}

/**
 * This function is called in sagebrew.js main file.
 * Each init task should be defined in it's own function for whatever reason.
 * -- Better code readability?
 */
export function init() {
    ajaxSetup();
}





