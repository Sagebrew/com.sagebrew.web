/**
 * @file
 * Handles generic ajax requests.
 * Pass in whatever overrides you want, but lets stop the same lines of code over and over again.
 * Don't use directly.
 * use sagebrew.resource instead. see sagebrew.js
 */

var helpers = require('./helpers');



/**
 * Handle api errors
 * @param XMLHttpRequest
 * @param notifyFrom
 * @param notifyAlign
 */
export function errorDisplay(XMLHttpRequest, notifyFrom, notifyAlign) {
    notifyFrom = typeof notifyFrom !== 'undefined' ? notifyFrom : "top";
    notifyAlign = typeof notifyAlign !== 'undefined' ? notifyAlign : 'right';
    var notificationMsg;
    switch (XMLHttpRequest.status) {
        case 500:
            $.notify({message: "Sorry looks like we're having some server issues right now. "}, {type: "danger"});
        break;
        case 401:
            $.notify({message: "Sorry doesn't look like you're allowed to do that. "}, {type: "danger"});
        break;
        case 404:
            $.notify({message: "Sorry, we can't seem to find what you're looking for"}, {type: 'danger'});
        break;
        case 400:
            var notification, badItemCap, errorMessage, reportMsg;
            var notificationDetail = XMLHttpRequest.responseJSON;
            var notificationText = XMLHttpRequest.responseText;
            if (!(typeof notificationDetail === "undefined" || notificationDetail === null)) {
                notification = notificationDetail;
            } else if( notificationText !== undefined) {
                notification = notificationText;
            } else {
                $.notify({message: "Sorry looks like you didn't include all the necessary information."}, {type: 'danger'});
            }
            if (typeof(notification) !== 'object'){
                notification = JSON.parse(notification);
            } else {
                try {
                    notification = JSON.parse(notification.detail);
                }
                catch(e) {
                    if(notification.detail !== undefined) {
                        $.notify({message: notification.detail}, {type: 'danger', placement: { from: notifyFrom, align: notifyAlign}});
                    } else{
                        for (var key in notification) {
                            notificationMsg = "" + helpers.toTitleCase(key) + ": " + notification[key][0];
                            $.notify({message: notificationMsg.replace("Non_field_errors: ", "").replace("_", " ")}, {type: 'danger'});
                        }
                    }
                    notification = [];
                }
            }
            for (var badItem in notification) {
                if (notification.hasOwnProperty(badItem)) {
                    for (var message in notification[badItem]) {
                        if (notification[badItem].hasOwnProperty(message)) {
                            if (typeof(notification[badItem]) === 'object'){
                                reportMsg = "" + helpers.toTitleCase(badItem)+ ": " + notification[badItem][message].message;
                            } else {
                                reportMsg = "" + helpers.toTitleCase(badItem) + ": " + notification[badItem][message];
                            }
                            badItemCap = badItem.charAt(0).toUpperCase() + badItem.slice(1);
                            errorMessage = badItemCap + ": " + reportMsg;
                            $.notify({message: errorMessage.replace("Non_field_errors: ", "").replace('_', " ")}, {type: 'danger', placement: { from: notifyFrom, align: notifyAlign}});
                        }
                    }
                }
            }
        break;
    }
}

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
            document.getElementById('sb-greyout-page').classList.add('sb_hidden');
            errorDisplay(XMLHttpRequest);
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
    return $.ajax(settings);
}

/**
 * PATCH
 * @param options
 * @returns {*}
 */
export function patch(options) {
    var defaultOptions = baseOptions();
    defaultOptions.type = "PATCH";
    var settings = $.extend({}, defaultOptions, options);
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
    return $.ajax(settings);
}

/**
 * OPTIONS
 * delete is a reserved word in js so we cant use it as the function name
 * =(
 * @param options
 * @returns {*}
 */
export function optionsMethod(options) {
    var defaultOptions = baseOptions();
    defaultOptions.type = "OPTIONS";
    var settings = $.extend({}, defaultOptions, options);
    return $.ajax(settings);
}