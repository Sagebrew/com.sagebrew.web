/**
 * @file
 * Handles generic ajax requests.
 * Pass in whatever overrides you want, but lets stop the same lines of code over and over again.
 * Don't use directly.
 * use sagebrew.resource instead. see sagebrew.js
 */

var helpers = require('./../helpers');

function baseOptions() {
    return {
        xhrFields: {withCredentials: true},
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        beforeSend: function (xhr, settings) {
            if (!helpers.csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", helpers.getCookie('csrftoken'));
            }
        },
        error: function (XMLHttpRequest) {
            if (XMLHttpRequest.status === 500) {
                $("#server_error").show();
            }
        }
    };
}

/**
 * GET
 * @param options
 * @returns {*}
 */
export function get(options) {
    var defaultOptions = baseOptions();
    defaultOptions.type = "GET";
    var settings = $.extend({}, defaultOptions, options);
    console.log("YAY");
    return $.ajax(settings);
}

/**
 * POST
 * @param options
 * @returns {*}
 */
export function post(options) {
    var defaultOptions = baseOptions();
    defaultOptions.type = "POST";
    var settings = $.extend({}, defaultOptions, options);
    console.log("YAY");
    return $.ajax(settings);
}

/**
 * PUT
 * @param options
 * @returns {*}
 */
export function put(options) {
    var defaultOptions = baseOptions();
    defaultOptions.type = "PUT";
    var settings = $.extend({}, defaultOptions, options);
    console.log("YAY");
    return $.ajax(settings);
}

/**
 * DELETE
 * delete is a reserved word in js so we cant use it as the function name
 * =(
 * @param options
 * @returns {*}
 */
export function remove(options) {
    var defaultOptions = baseOptions();
    defaultOptions.type = "DELETE";
    var settings = $.extend({}, defaultOptions, options);
    console.log("YAY");
    return $.ajax(settings);
}