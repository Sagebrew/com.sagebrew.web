/**
 * @file
 * Global SB controller. Loaded on every page.
 */

var helpers = require('./../../common/helpers');


/**
 * Scope - Global
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
 * Init.
 */
export function init() {
    ajaxSetup();

}
/**
 * Load
 */
export function load() {

}