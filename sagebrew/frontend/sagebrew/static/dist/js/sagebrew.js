require=(function e(t,n,r){function s(o,u){if(!n[o]){if(!t[o]){var a=typeof require=="function"&&require;if(!u&&a)return a(o,!0);if(i)return i(o,!0);var f=new Error("Cannot find module '"+o+"'");throw f.code="MODULE_NOT_FOUND",f}var l=n[o]={exports:{}};t[o][0].call(l.exports,function(e){var n=t[o][1][e];return s(n?n:e)},l,l.exports,e,t,n,r)}return n[o].exports}var i=typeof require=="function"&&require;for(var o=0;o<r.length;o++)s(r[o]);return s})({1:[function(require,module,exports){
/**
 * @file
 * Handles generic ajax requests.
 * Pass in whatever overrides you want, but lets stop the same lines of code over and over again.
 * Don't use directly.
 * use sagebrew.resource instead. see sagebrew.js
 */

'use strict';

Object.defineProperty(exports, '__esModule', {
    value: true
});
exports.get = get;
exports.post = post;
exports.put = put;
exports.remove = remove;
var helpers = require('./../helpers');

/**
 * Handle api errors
 * @param XMLHttpRequest
 * @param notifyFrom
 * @param notifyAlign
 */
function errorDisplay(XMLHttpRequest, notifyFrom, notifyAlign) {
    notifyFrom = typeof notifyFrom !== 'undefined' ? notifyFrom : "top";
    notifyAlign = typeof notifyAlign !== 'undefined' ? notifyAlign : 'right';
    switch (XMLHttpRequest.status) {
        case 500:
            $.notify({ message: "Sorry looks like we're having some server issues right now. " }, { type: "danger" });
            break;
        case 401:
            $.notify({ message: "Sorry doesn't look like you're allowed to do that. " }, { type: "danger" });
            break;
        case 404:
            $.notify({ message: "Sorry, we can't seem to find what you're looking for" }, { type: 'danger' });
            break;
        case 400:
            var notification, badItemCap, errorMessage, reportMsg;
            var notificationDetail = XMLHttpRequest.responseJSON;
            var notificationText = XMLHttpRequest.responseText;
            if (!(typeof notificationDetail === "undefined" || notificationDetail === null)) {
                notification = notificationDetail;
            } else if (notificationText !== undefined) {
                notification = notificationText;
            } else {
                $.notify({ message: "Sorry looks like you didn't include all the necessary information." }, { type: 'danger' });
            }
            if (typeof notification !== 'object') {
                notification = JSON.parse(notification);
            } else {
                try {
                    notification = JSON.parse(notification.detail);
                } catch (e) {
                    if (notification.detail !== undefined) {
                        $.notify({ message: notification.detail }, { type: 'danger', placement: { from: notifyFrom, align: notifyAlign } });
                    } else {
                        for (var key in notification) {
                            $.notify({ message: notification[key][0] }, { type: 'danger' });
                        }
                    }
                    notification = [];
                }
            }
            for (var badItem in notification) {
                for (var message in notification[badItem]) {
                    if (typeof notification[badItem] === 'object') {
                        reportMsg = notification[badItem][message].message;
                    } else {
                        reportMsg = notification[badItem][message];
                    }
                    badItemCap = badItem.charAt(0).toUpperCase() + badItem.slice(1);
                    errorMessage = badItemCap + ": " + reportMsg;
                    $.notify({ message: errorMessage.replace('_', " ") }, { type: 'danger', placement: { from: notifyFrom, align: notifyAlign } });
                }
            }
            break;
    }
}

function baseOptions() {
    return {
        xhrFields: { withCredentials: true },
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        beforeSend: function beforeSend(xhr, settings) {
            if (!helpers.csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", helpers.getCookie('csrftoken'));
            }
        },
        error: function error(XMLHttpRequest) {
            errorDisplay(XMLHttpRequest);
        }
    };
}

/**
 * GET
 * @param options
 * @returns {*}
 */

function get(options) {
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

function post(options) {
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

function put(options) {
    var defaultOptions = baseOptions();
    defaultOptions.type = "PUT";
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

function remove(options) {
    var defaultOptions = baseOptions();
    defaultOptions.type = "DELETE";
    var settings = $.extend({}, defaultOptions, options);
    return $.ajax(settings);
}

},{"./../helpers":3}],2:[function(require,module,exports){
/**
 * @file
 * blah blah?
 */

"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.test = test;

function test() {
  console.log("asdfasdf");
  return 'asdfadf';
}

},{}],3:[function(require,module,exports){
/**
 * @file
 * Helper functions that aren't global.
 */

/**
 * Get cookie based by name.
 * @param name
 * @returns {*}
 */
'use strict';

Object.defineProperty(exports, '__esModule', {
    value: true
});
exports.getCookie = getCookie;
exports.csrfSafeMethod = csrfSafeMethod;

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i += 1) {
            var cookie = $.trim(cookies[i]);
            // Does this cookie string begin with the name we want?

            if (cookie.substring(0, name.length + 1) === name + '=') {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * Check if HTTP method requires CSRF.
 * @param method
 * @returns {boolean}
 */

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method)
    );
}

},{}],4:[function(require,module,exports){
/**
 * @file
 * Init the SB website.
 * globalInit - Runs on all pages.
 * UserAuthedInit - Runs on authed pages.
 * userAnonInit - Runs on anon pages.
 * TODO: The individual init functions could be turned into arrays or objects and then
 * looped over.
 */
'use strict';

Object.defineProperty(exports, '__esModule', {
    value: true
});
exports.globalInit = globalInit;
exports.userAuthedInit = userAuthedInit;
exports.userAnonInit = userAnonInit;
var helpers = require('./helpers');

/**
 * Scope - Global
 * Ajax Setup
 * -- Automatically add CSRF cookie value to all ajax requests.
 */
function ajaxSetup() {
    $.ajaxSetup({
        beforeSend: function beforeSend(xhr, settings) {
            if (!helpers.csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", helpers.getCookie('csrftoken'));
            }
        }
    });
}

/**
 *  Scope - User Authed
 *  Adds an event handler to page unload that ajax posts all the user's actions that occured during the page.
 *  TODO: Stop doing this.
 *  Not only are non-async ajax calls deprecated it holds the page load up for the user.
 *  They can't even start loading the next page until this is completed.
 */
function collectAuthedActions() {
    $(document).ready(function () {
        "use strict";
        window.onbeforeunload = function () {
            var objectList = [];
            $(".js-page-object").each(function () {
                objectList.push($(this).data('object_uuid'));
            });
            if (objectList.length) {
                $.ajax({
                    xhrFields: { withCredentials: true },
                    type: "POST",
                    async: false,
                    url: "/docstore/update_neo_api/",
                    data: JSON.stringify({
                        'object_uuids': objectList
                    }),
                    contentType: "application/json; charset=utf-8",
                    dataType: "json",
                    error: function error(XMLHttpRequest) {
                        if (XMLHttpRequest.status === 500) {
                            $("#server_error").show();
                        }
                    }
                });
            }
        };
    });
}

/**
 * This function is called in sagebrew.js main file.
 * Each init task should be defined in it's own function for whatever reason.
 * -- Better code readability?
 */

function globalInit() {
    ajaxSetup();
}

/**
 * Auth Init.
 */

function userAuthedInit() {
    collectAuthedActions();
}

/**
 * Anon Init.
 */

function userAnonInit() {}

},{"./helpers":3}],"sagebrew":[function(require,module,exports){
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

'use strict';

Object.defineProperty(exports, '__esModule', {
  value: true
});
var globalInit = require('./components/init').globalInit,
    test = require('./components/core').test,
    resourceMethods = require('./components/common/resourcemethods');

//
// init page.
globalInit();

/**
 * Real generic wrapper around ajax requests.
 * @param options
 * @returns {*}
 */
var request = resourceMethods;
exports.request = request;

},{"./components/common/resourcemethods":1,"./components/core":2,"./components/init":4}]},{},["sagebrew"])
//# sourceMappingURL=data:application/json;charset:utf-8;base64,eyJ2ZXJzaW9uIjozLCJzb3VyY2VzIjpbIm5vZGVfbW9kdWxlcy9icm93c2VyaWZ5L25vZGVfbW9kdWxlcy9icm93c2VyLXBhY2svX3ByZWx1ZGUuanMiLCIvVXNlcnMvbXdpc25lci9Qcm9qZWN0cy9zYWdlYnJldy9jb20uc2FnZWJyZXcud2ViL3NhZ2VicmV3L2Zyb250ZW5kL2pzL3NyYy9jb21wb25lbnRzL2NvbW1vbi9yZXNvdXJjZW1ldGhvZHMuanMiLCIvVXNlcnMvbXdpc25lci9Qcm9qZWN0cy9zYWdlYnJldy9jb20uc2FnZWJyZXcud2ViL3NhZ2VicmV3L2Zyb250ZW5kL2pzL3NyYy9jb21wb25lbnRzL2NvcmUuanMiLCIvVXNlcnMvbXdpc25lci9Qcm9qZWN0cy9zYWdlYnJldy9jb20uc2FnZWJyZXcud2ViL3NhZ2VicmV3L2Zyb250ZW5kL2pzL3NyYy9jb21wb25lbnRzL2hlbHBlcnMuanMiLCIvVXNlcnMvbXdpc25lci9Qcm9qZWN0cy9zYWdlYnJldy9jb20uc2FnZWJyZXcud2ViL3NhZ2VicmV3L2Zyb250ZW5kL2pzL3NyYy9jb21wb25lbnRzL2luaXQuanMiLCIvVXNlcnMvbXdpc25lci9Qcm9qZWN0cy9zYWdlYnJldy9jb20uc2FnZWJyZXcud2ViL3NhZ2VicmV3L2Zyb250ZW5kL2pzL3NyYy9zYWdlYnJldy5qcyJdLCJuYW1lcyI6W10sIm1hcHBpbmdzIjoiQUFBQTs7Ozs7Ozs7Ozs7Ozs7Ozs7O0FDUUEsSUFBSSxPQUFPLEdBQUcsT0FBTyxDQUFDLGNBQWMsQ0FBQyxDQUFDOzs7Ozs7OztBQVF0QyxTQUFTLFlBQVksQ0FBQyxjQUFjLEVBQUUsVUFBVSxFQUFFLFdBQVcsRUFBRTtBQUMzRCxjQUFVLEdBQUcsT0FBTyxVQUFVLEtBQUssV0FBVyxHQUFHLFVBQVUsR0FBRyxLQUFLLENBQUM7QUFDcEUsZUFBVyxHQUFHLE9BQU8sV0FBVyxLQUFLLFdBQVcsR0FBRyxXQUFXLEdBQUcsT0FBTyxDQUFDO0FBQ3pFLFlBQVEsY0FBYyxDQUFDLE1BQU07QUFDekIsYUFBSyxHQUFHO0FBQ0os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QUFVLEdBQUc7QUFDekIsYUFBUyxFQUFFLENBQUM7Q0FDZjs7Ozs7O0FBS00sU0FBUyxjQUFjLEdBQUc7QUFDN0Isd0JBQW9CLEVBQUUsQ0FBQztDQUMxQjs7Ozs7O0FBS00sU0FBUyxZQUFZLEdBQUcsRUFFOUI7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7QUN4RUQsSUFBSSxVQUFVLEdBQUcsT0FBTyxDQUFDLG1CQUFtQixDQUFDLENBQUMsVUFBVTtJQUNwRCxJQUFJLEdBQUcsT0FBTyxDQUFDLG1CQUFtQixDQUFDLENBQUMsSUFBSTtJQUN4QyxlQUFlLEdBQUcsT0FBTyxDQUFDLHFDQUFxQyxDQUFDLENBQUM7Ozs7QUFJckUsVUFBVSxFQUFFLENBQUM7Ozs7Ozs7QUFPTixJQUFNLE9BQU8sR0FBRyxlQUFlLENBQUMiLCJmaWxlIjoiZ2VuZXJhdGVkLmpzIiwic291cmNlUm9vdCI6IiIsInNvdXJjZXNDb250ZW50IjpbIihmdW5jdGlvbiBlKHQsbixyKXtmdW5jdGlvbiBzKG8sdSl7aWYoIW5bb10pe2lmKCF0W29dKXt2YXIgYT10eXBlb2YgcmVxdWlyZT09XCJmdW5jdGlvblwiJiZyZXF1aXJlO2lmKCF1JiZhKXJldHVybiBhKG8sITApO2lmKGkpcmV0dXJuIGkobywhMCk7dmFyIGY9bmV3IEVycm9yKFwiQ2Fubm90IGZpbmQgbW9kdWxlICdcIitvK1wiJ1wiKTt0aHJvdyBmLmNvZGU9XCJNT0RVTEVfTk9UX0ZPVU5EXCIsZn12YXIgbD1uW29dPXtleHBvcnRzOnt9fTt0W29dWzBdLmNhbGwobC5leHBvcnRzLGZ1bmN0aW9uKGUpe3ZhciBuPXRbb11bMV1bZV07cmV0dXJuIHMobj9uOmUpfSxsLGwuZXhwb3J0cyxlLHQsbixyKX1yZXR1cm4gbltvXS5leHBvcnRzfXZhciBpPXR5cGVvZiByZXF1aXJlPT1cImZ1bmN0aW9uXCImJnJlcXVpcmU7Zm9yKHZhciBvPTA7bzxyLmxlbmd0aDtvKyspcyhyW29dKTtyZXR1cm4gc30pIiwiLyoqXG4gKiBAZmlsZVxuICogSGFuZGxlcyBnZW5lcmljIGFqYXggcmVxdWVzdHMuXG4gKiBQYXNzIGluIHdoYXRldmVyIG92ZXJyaWRlcyB5b3Ugd2FudCwgYnV0IGxldHMgc3RvcCB0aGUgc2FtZSBsaW5lcyBvZiBjb2RlIG92ZXIgYW5kIG92ZXIgYWdhaW4uXG4gKiBEb24ndCB1c2UgZGlyZWN0bHkuXG4gKiB1c2Ugc2FnZWJyZXcucmVzb3VyY2UgaW5zdGVhZC4gc2VlIHNhZ2VicmV3LmpzXG4gKi9cblxudmFyIGhlbHBlcnMgPSByZXF1aXJlKCcuLy4uL2hlbHBlcnMnKTtcblxuLyoqXG4gKiBIYW5kbGUgYXBpIGVycm9yc1xuICogQHBhcmFtIFhNTEh0dHBSZXF1ZXN0XG4gKiBAcGFyYW0gbm90aWZ5RnJvbVxuICogQHBhcmFtIG5vdGlmeUFsaWduXG4gKi9cbmZ1bmN0aW9uIGVycm9yRGlzcGxheShYTUxIdHRwUmVxdWVzdCwgbm90aWZ5RnJvbSwgbm90aWZ5QWxpZ24pIHtcbiAgICBub3RpZnlGcm9tID0gdHlwZW9mIG5vdGlmeUZyb20gIT09ICd1bmRlZmluZWQnID8gbm90aWZ5RnJvbSA6IFwidG9wXCI7XG4gICAgbm90aWZ5QWxpZ24gPSB0eXBlb2Ygbm90aWZ5QWxpZ24gIT09ICd1bmRlZmluZWQnID8gbm90aWZ5QWxpZ24gOiAncmlnaHQnO1xuICAgIHN3aXRjaCAoWE1MSHR0cFJlcXVlc3Quc3RhdHVzKSB7XG4gICAgICAgIGNhc2UgNTAwOlxuICAgICAgICAgICAgJC5ub3RpZnkoe21lc3NhZ2U6IFwiU29ycnkgbG9va3MgbGlrZSB3ZSdyZSBoYXZpbmcgc29tZSBzZXJ2ZXIgaXNzdWVzIHJpZ2h0IG5vdy4gXCJ9LCB7dHlwZTogXCJkYW5nZXJcIn0pO1xuICAgICAgICBicmVhaztcbiAgICAgICAgY2FzZSA0MDE6XG4gICAgICAgICAgICAkLm5vdGlmeSh7bWVzc2FnZTogXCJTb3JyeSBkb2Vzbid0IGxvb2sgbGlrZSB5b3UncmUgYWxsb3dlZCB0byBkbyB0aGF0LiBcIn0sIHt0eXBlOiBcImRhbmdlclwifSk7XG4gICAgICAgIGJyZWFrO1xuICAgICAgICBjYXNlIDQwNDpcbiAgICAgICAgICAgICQubm90aWZ5KHttZXNzYWdlOiBcIlNvcnJ5LCB3ZSBjYW4ndCBzZWVtIHRvIGZpbmQgd2hhdCB5b3UncmUgbG9va2luZyBmb3JcIn0sIHt0eXBlOiAnZGFuZ2VyJ30pO1xuICAgICAgICBicmVhaztcbiAgICAgICAgY2FzZSA0MDA6XG4gICAgICAgICAgICB2YXIgbm90aWZpY2F0aW9uLCBiYWRJdGVtQ2FwLCBlcnJvck1lc3NhZ2UsIHJlcG9ydE1zZztcbiAgICAgICAgICAgIHZhciBub3RpZmljYXRpb25EZXRhaWwgPSBYTUxIdHRwUmVxdWVzdC5yZXNwb25zZUpTT047XG4gICAgICAgICAgICB2YXIgbm90aWZpY2F0aW9uVGV4dCA9IFhNTEh0dHBSZXF1ZXN0LnJlc3BvbnNlVGV4dDtcbiAgICAgICAgICAgIGlmICghKHR5cGVvZiBub3RpZmljYXRpb25EZXRhaWwgPT09IFwidW5kZWZpbmVkXCIgfHwgbm90aWZpY2F0aW9uRGV0YWlsID09PSBudWxsKSkge1xuICAgICAgICAgICAgICAgIG5vdGlmaWNhdGlvbiA9IG5vdGlmaWNhdGlvbkRldGFpbDtcbiAgICAgICAgICAgIH0gZWxzZSBpZiggbm90aWZpY2F0aW9uVGV4dCAhPT0gdW5kZWZpbmVkKSB7XG4gICAgICAgICAgICAgICAgbm90aWZpY2F0aW9uID0gbm90aWZpY2F0aW9uVGV4dDtcbiAgICAgICAgICAgIH0gZWxzZSB7XG4gICAgICAgICAgICAgICAgJC5ub3RpZnkoe21lc3NhZ2U6IFwiU29ycnkgbG9va3MgbGlrZSB5b3UgZGlkbid0IGluY2x1ZGUgYWxsIHRoZSBuZWNlc3NhcnkgaW5mb3JtYXRpb24uXCJ9LCB7dHlwZTogJ2Rhbmdlcid9KTtcbiAgICAgICAgICAgIH1cbiAgICAgICAgICAgIGlmICh0eXBlb2Yobm90aWZpY2F0aW9uKSAhPT0gJ29iamVjdCcpe1xuICAgICAgICAgICAgICAgIG5vdGlmaWNhdGlvbiA9IEpTT04ucGFyc2Uobm90aWZpY2F0aW9uKTtcbiAgICAgICAgICAgIH0gZWxzZSB7XG4gICAgICAgICAgICAgICAgdHJ5IHtcbiAgICAgICAgICAgICAgICAgICAgbm90aWZpY2F0aW9uID0gSlNPTi5wYXJzZShub3RpZmljYXRpb24uZGV0YWlsKTtcbiAgICAgICAgICAgICAgICB9XG4gICAgICAgICAgICAgICAgY2F0Y2goZSkge1xuICAgICAgICAgICAgICAgICAgICBpZihub3RpZmljYXRpb24uZGV0YWlsICE9PSB1bmRlZmluZWQpIHtcbiAgICAgICAgICAgICAgICAgICAgICAgICQubm90aWZ5KHttZXNzYWdlOiBub3RpZmljYXRpb24uZGV0YWlsfSwge3R5cGU6ICdkYW5nZXInLCBwbGFjZW1lbnQ6IHsgZnJvbTogbm90aWZ5RnJvbSwgYWxpZ246IG5vdGlmeUFsaWdufX0pO1xuICAgICAgICAgICAgICAgICAgICB9IGVsc2V7XG4gICAgICAgICAgICAgICAgICAgICAgICBmb3IgKHZhciBrZXkgaW4gbm90aWZpY2F0aW9uKSB7XG4gICAgICAgICAgICAgICAgICAgICAgICAgICQubm90aWZ5KHttZXNzYWdlOiBub3RpZmljYXRpb25ba2V5XVswXX0sIHt0eXBlOiAnZGFuZ2VyJ30pO1xuICAgICAgICAgICAgICAgICAgICAgICAgfVxuICAgICAgICAgICAgICAgICAgICB9XG4gICAgICAgICAgICAgICAgICAgIG5vdGlmaWNhdGlvbiA9IFtdO1xuICAgICAgICAgICAgICAgIH1cbiAgICAgICAgICAgIH1cbiAgICAgICAgICAgIGZvciAodmFyIGJhZEl0ZW0gaW4gbm90aWZpY2F0aW9uKSB7XG4gICAgICAgICAgICAgICAgZm9yICh2YXIgbWVzc2FnZSBpbiBub3RpZmljYXRpb25bYmFkSXRlbV0pIHtcbiAgICAgICAgICAgICAgICAgICAgaWYgKHR5cGVvZihub3RpZmljYXRpb25bYmFkSXRlbV0pID09PSAnb2JqZWN0Jyl7XG4gICAgICAgICAgICAgICAgICAgICAgICByZXBvcnRNc2cgPSBub3RpZmljYXRpb25bYmFkSXRlbV1bbWVzc2FnZV0ubWVzc2FnZTtcbiAgICAgICAgICAgICAgICAgICAgfSBlbHNlIHtcbiAgICAgICAgICAgICAgICAgICAgICAgIHJlcG9ydE1zZyA9IG5vdGlmaWNhdGlvbltiYWRJdGVtXVttZXNzYWdlXTtcbiAgICAgICAgICAgICAgICAgICAgfVxuICAgICAgICAgICAgICAgICAgICBiYWRJdGVtQ2FwID0gYmFkSXRlbS5jaGFyQXQoMCkudG9VcHBlckNhc2UoKSArIGJhZEl0ZW0uc2xpY2UoMSk7XG4gICAgICAgICAgICAgICAgICAgIGVycm9yTWVzc2FnZSA9IGJhZEl0ZW1DYXAgKyBcIjogXCIgKyByZXBvcnRNc2c7XG4gICAgICAgICAgICAgICAgICAgICQubm90aWZ5KHttZXNzYWdlOiBlcnJvck1lc3NhZ2UucmVwbGFjZSgnXycsIFwiIFwiKX0sIHt0eXBlOiAnZGFuZ2VyJywgcGxhY2VtZW50OiB7IGZyb206IG5vdGlmeUZyb20sIGFsaWduOiBub3RpZnlBbGlnbn19KTtcbiAgICAgICAgICAgICAgICB9XG4gICAgICAgICAgICB9XG4gICAgICAgIGJyZWFrO1xuICAgIH1cbn1cblxuZnVuY3Rpb24gYmFzZU9wdGlvbnMoKSB7XG4gICAgcmV0dXJuIHtcbiAgICAgICAgeGhyRmllbGRzOiB7d2l0aENyZWRlbnRpYWxzOiB0cnVlfSxcbiAgICAgICAgY29udGVudFR5cGU6IFwiYXBwbGljYXRpb24vanNvbjsgY2hhcnNldD11dGYtOFwiLFxuICAgICAgICBkYXRhVHlwZTogXCJqc29uXCIsXG4gICAgICAgIGJlZm9yZVNlbmQ6IGZ1bmN0aW9uICh4aHIsIHNldHRpbmdzKSB7XG4gICAgICAgICAgICBpZiAoIWhlbHBlcnMuY3NyZlNhZmVNZXRob2Qoc2V0dGluZ3MudHlwZSkgJiYgIXRoaXMuY3Jvc3NEb21haW4pIHtcbiAgICAgICAgICAgICAgICB4aHIuc2V0UmVxdWVzdEhlYWRlcihcIlgtQ1NSRlRva2VuXCIsIGhlbHBlcnMuZ2V0Q29va2llKCdjc3JmdG9rZW4nKSk7XG4gICAgICAgICAgICB9XG4gICAgICAgIH0sXG4gICAgICAgIGVycm9yOiBmdW5jdGlvbiAoWE1MSHR0cFJlcXVlc3QpIHtcbiAgICAgICAgICBlcnJvckRpc3BsYXkoWE1MSHR0cFJlcXVlc3QpO1xuICAgICAgICB9XG4gICAgfTtcbn1cblxuLyoqXG4gKiBHRVRcbiAqIEBwYXJhbSBvcHRpb25zXG4gKiBAcmV0dXJucyB7Kn1cbiAqL1xuZXhwb3J0IGZ1bmN0aW9uIGdldChvcHRpb25zKSB7XG4gICAgdmFyIGRlZmF1bHRPcHRpb25zID0gYmFzZU9wdGlvbnMoKTtcbiAgICBkZWZhdWx0T3B0aW9ucy50eXBlID0gXCJHRVRcIjtcbiAgICB2YXIgc2V0dGluZ3MgPSAkLmV4dGVuZCh7fSwgZGVmYXVsdE9wdGlvbnMsIG9wdGlvbnMpO1xuICAgIHJldHVybiAkLmFqYXgoc2V0dGluZ3MpO1xufVxuXG4vKipcbiAqIFBPU1RcbiAqIEBwYXJhbSBvcHRpb25zXG4gKiBAcmV0dXJucyB7Kn1cbiAqL1xuZXhwb3J0IGZ1bmN0aW9uIHBvc3Qob3B0aW9ucykge1xuICAgIHZhciBkZWZhdWx0T3B0aW9ucyA9IGJhc2VPcHRpb25zKCk7XG4gICAgZGVmYXVsdE9wdGlvbnMudHlwZSA9IFwiUE9TVFwiO1xuICAgIHZhciBzZXR0aW5ncyA9ICQuZXh0ZW5kKHt9LCBkZWZhdWx0T3B0aW9ucywgb3B0aW9ucyk7XG4gICAgcmV0dXJuICQuYWpheChzZXR0aW5ncyk7XG59XG5cbi8qKlxuICogUFVUXG4gKiBAcGFyYW0gb3B0aW9uc1xuICogQHJldHVybnMgeyp9XG4gKi9cbmV4cG9ydCBmdW5jdGlvbiBwdXQob3B0aW9ucykge1xuICAgIHZhciBkZWZhdWx0T3B0aW9ucyA9IGJhc2VPcHRpb25zKCk7XG4gICAgZGVmYXVsdE9wdGlvbnMudHlwZSA9IFwiUFVUXCI7XG4gICAgdmFyIHNldHRpbmdzID0gJC5leHRlbmQoe30sIGRlZmF1bHRPcHRpb25zLCBvcHRpb25zKTtcbiAgICByZXR1cm4gJC5hamF4KHNldHRpbmdzKTtcbn1cblxuLyoqXG4gKiBERUxFVEVcbiAqIGRlbGV0ZSBpcyBhIHJlc2VydmVkIHdvcmQgaW4ganMgc28gd2UgY2FudCB1c2UgaXQgYXMgdGhlIGZ1bmN0aW9uIG5hbWVcbiAqID0oXG4gKiBAcGFyYW0gb3B0aW9uc1xuICogQHJldHVybnMgeyp9XG4gKi9cbmV4cG9ydCBmdW5jdGlvbiByZW1vdmUob3B0aW9ucykge1xuICAgIHZhciBkZWZhdWx0T3B0aW9ucyA9IGJhc2VPcHRpb25zKCk7XG4gICAgZGVmYXVsdE9wdGlvbnMudHlwZSA9IFwiREVMRVRFXCI7XG4gICAgdmFyIHNldHRpbmdzID0gJC5leHRlbmQoe30sIGRlZmF1bHRPcHRpb25zLCBvcHRpb25zKTtcbiAgICByZXR1cm4gJC5hamF4KHNldHRpbmdzKTtcbn0iLCIvKipcbiAqIEBmaWxlXG4gKiBibGFoIGJsYWg/XG4gKi9cblxuZXhwb3J0IGZ1bmN0aW9uIHRlc3QoKSB7XG4gICAgY29uc29sZS5sb2coXCJhc2RmYXNkZlwiKTtcbiAgICByZXR1cm4gJ2FzZGZhZGYnO1xufSIsIi8qKlxuICogQGZpbGVcbiAqIEhlbHBlciBmdW5jdGlvbnMgdGhhdCBhcmVuJ3QgZ2xvYmFsLlxuICovXG5cbi8qKlxuICogR2V0IGNvb2tpZSBiYXNlZCBieSBuYW1lLlxuICogQHBhcmFtIG5hbWVcbiAqIEByZXR1cm5zIHsqfVxuICovXG5leHBvcnQgZnVuY3Rpb24gZ2V0Q29va2llKG5hbWUpIHtcbiAgICB2YXIgY29va2llVmFsdWUgPSBudWxsO1xuICAgIGlmIChkb2N1bWVudC5jb29raWUgJiYgZG9jdW1lbnQuY29va2llICE9PSBcIlwiKSB7XG4gICAgICAgIHZhciBjb29raWVzID0gZG9jdW1lbnQuY29va2llLnNwbGl0KCc7Jyk7XG4gICAgICAgIGZvciAodmFyIGkgPSAwOyBpIDwgY29va2llcy5sZW5ndGg7IGkgKz0gMSkge1xuICAgICAgICAgICAgdmFyIGNvb2tpZSA9ICQudHJpbShjb29raWVzW2ldKTtcbiAgICAgICAgICAgIC8vIERvZXMgdGhpcyBjb29raWUgc3RyaW5nIGJlZ2luIHdpdGggdGhlIG5hbWUgd2Ugd2FudD9cblxuICAgICAgICAgICAgaWYgKGNvb2tpZS5zdWJzdHJpbmcoMCwgbmFtZS5sZW5ndGggKyAxKSA9PT0gKG5hbWUgKyAnPScpKSB7XG4gICAgICAgICAgICAgICAgY29va2llVmFsdWUgPSBkZWNvZGVVUklDb21wb25lbnQoY29va2llLnN1YnN0cmluZyhuYW1lLmxlbmd0aCArIDEpKTtcbiAgICAgICAgICAgICAgICBicmVhaztcbiAgICAgICAgICAgIH1cbiAgICAgICAgfVxuICAgIH1cbiAgICByZXR1cm4gY29va2llVmFsdWU7XG59XG5cbi8qKlxuICogQ2hlY2sgaWYgSFRUUCBtZXRob2QgcmVxdWlyZXMgQ1NSRi5cbiAqIEBwYXJhbSBtZXRob2RcbiAqIEByZXR1cm5zIHtib29sZWFufVxuICovXG5leHBvcnQgZnVuY3Rpb24gY3NyZlNhZmVNZXRob2QobWV0aG9kKSB7XG4gICAgLy8gdGhlc2UgSFRUUCBtZXRob2RzIGRvIG5vdCByZXF1aXJlIENTUkYgcHJvdGVjdGlvblxuICAgIHJldHVybiAoL14oR0VUfEhFQUR8T1BUSU9OU3xUUkFDRSkkLy50ZXN0KG1ldGhvZCkpO1xufSIsIi8qKlxuICogQGZpbGVcbiAqIEluaXQgdGhlIFNCIHdlYnNpdGUuXG4gKiBnbG9iYWxJbml0IC0gUnVucyBvbiBhbGwgcGFnZXMuXG4gKiBVc2VyQXV0aGVkSW5pdCAtIFJ1bnMgb24gYXV0aGVkIHBhZ2VzLlxuICogdXNlckFub25Jbml0IC0gUnVucyBvbiBhbm9uIHBhZ2VzLlxuICogVE9ETzogVGhlIGluZGl2aWR1YWwgaW5pdCBmdW5jdGlvbnMgY291bGQgYmUgdHVybmVkIGludG8gYXJyYXlzIG9yIG9iamVjdHMgYW5kIHRoZW5cbiAqIGxvb3BlZCBvdmVyLlxuICovXG52YXIgaGVscGVycyA9IHJlcXVpcmUoJy4vaGVscGVycycpO1xuXG4vKipcbiAqIFNjb3BlIC0gR2xvYmFsXG4gKiBBamF4IFNldHVwXG4gKiAtLSBBdXRvbWF0aWNhbGx5IGFkZCBDU1JGIGNvb2tpZSB2YWx1ZSB0byBhbGwgYWpheCByZXF1ZXN0cy5cbiAqL1xuZnVuY3Rpb24gYWpheFNldHVwKCkge1xuICAgICQuYWpheFNldHVwKHtcbiAgICAgICAgYmVmb3JlU2VuZDogZnVuY3Rpb24gKHhociwgc2V0dGluZ3MpIHtcbiAgICAgICAgICAgIGlmICghaGVscGVycy5jc3JmU2FmZU1ldGhvZChzZXR0aW5ncy50eXBlKSAmJiAhdGhpcy5jcm9zc0RvbWFpbikge1xuICAgICAgICAgICAgICAgIHhoci5zZXRSZXF1ZXN0SGVhZGVyKFwiWC1DU1JGVG9rZW5cIiwgaGVscGVycy5nZXRDb29raWUoJ2NzcmZ0b2tlbicpKTtcbiAgICAgICAgICAgIH1cbiAgICAgICAgfVxuICAgIH0pO1xufVxuXG4vKipcbiAqICBTY29wZSAtIFVzZXIgQXV0aGVkXG4gKiAgQWRkcyBhbiBldmVudCBoYW5kbGVyIHRvIHBhZ2UgdW5sb2FkIHRoYXQgYWpheCBwb3N0cyBhbGwgdGhlIHVzZXIncyBhY3Rpb25zIHRoYXQgb2NjdXJlZCBkdXJpbmcgdGhlIHBhZ2UuXG4gKiAgVE9ETzogU3RvcCBkb2luZyB0aGlzLlxuICogIE5vdCBvbmx5IGFyZSBub24tYXN5bmMgYWpheCBjYWxscyBkZXByZWNhdGVkIGl0IGhvbGRzIHRoZSBwYWdlIGxvYWQgdXAgZm9yIHRoZSB1c2VyLlxuICogIFRoZXkgY2FuJ3QgZXZlbiBzdGFydCBsb2FkaW5nIHRoZSBuZXh0IHBhZ2UgdW50aWwgdGhpcyBpcyBjb21wbGV0ZWQuXG4gKi9cbmZ1bmN0aW9uIGNvbGxlY3RBdXRoZWRBY3Rpb25zKCkge1xuICAgICQoZG9jdW1lbnQpLnJlYWR5KGZ1bmN0aW9uICgpIHtcbiAgICAgICAgXCJ1c2Ugc3RyaWN0XCI7XG4gICAgICAgIHdpbmRvdy5vbmJlZm9yZXVubG9hZCA9IGZ1bmN0aW9uICgpIHtcbiAgICAgICAgICAgIHZhciBvYmplY3RMaXN0ID0gW107XG4gICAgICAgICAgICAkKFwiLmpzLXBhZ2Utb2JqZWN0XCIpLmVhY2goZnVuY3Rpb24gKCkge1xuICAgICAgICAgICAgICAgIG9iamVjdExpc3QucHVzaCgkKHRoaXMpLmRhdGEoJ29iamVjdF91dWlkJykpO1xuICAgICAgICAgICAgfSk7XG4gICAgICAgICAgICBpZiAob2JqZWN0TGlzdC5sZW5ndGgpIHtcbiAgICAgICAgICAgICAgICAkLmFqYXgoe1xuICAgICAgICAgICAgICAgICAgICB4aHJGaWVsZHM6IHt3aXRoQ3JlZGVudGlhbHM6IHRydWV9LFxuICAgICAgICAgICAgICAgICAgICB0eXBlOiBcIlBPU1RcIixcbiAgICAgICAgICAgICAgICAgICAgYXN5bmM6IGZhbHNlLFxuICAgICAgICAgICAgICAgICAgICB1cmw6IFwiL2RvY3N0b3JlL3VwZGF0ZV9uZW9fYXBpL1wiLFxuICAgICAgICAgICAgICAgICAgICBkYXRhOiBKU09OLnN0cmluZ2lmeSh7XG4gICAgICAgICAgICAgICAgICAgICAgICAnb2JqZWN0X3V1aWRzJzogb2JqZWN0TGlzdFxuICAgICAgICAgICAgICAgICAgICB9KSxcbiAgICAgICAgICAgICAgICAgICAgY29udGVudFR5cGU6IFwiYXBwbGljYXRpb24vanNvbjsgY2hhcnNldD11dGYtOFwiLFxuICAgICAgICAgICAgICAgICAgICBkYXRhVHlwZTogXCJqc29uXCIsXG4gICAgICAgICAgICAgICAgICAgIGVycm9yOiBmdW5jdGlvbiAoWE1MSHR0cFJlcXVlc3QpIHtcbiAgICAgICAgICAgICAgICAgICAgICAgIGlmIChYTUxIdHRwUmVxdWVzdC5zdGF0dXMgPT09IDUwMCkge1xuICAgICAgICAgICAgICAgICAgICAgICAgICAgICQoXCIjc2VydmVyX2Vycm9yXCIpLnNob3coKTtcbiAgICAgICAgICAgICAgICAgICAgICAgIH1cbiAgICAgICAgICAgICAgICAgICAgfVxuICAgICAgICAgICAgICAgIH0pO1xuICAgICAgICAgICAgfVxuICAgICAgICB9O1xuICAgIH0pO1xufVxuXG5cblxuLyoqXG4gKiBUaGlzIGZ1bmN0aW9uIGlzIGNhbGxlZCBpbiBzYWdlYnJldy5qcyBtYWluIGZpbGUuXG4gKiBFYWNoIGluaXQgdGFzayBzaG91bGQgYmUgZGVmaW5lZCBpbiBpdCdzIG93biBmdW5jdGlvbiBmb3Igd2hhdGV2ZXIgcmVhc29uLlxuICogLS0gQmV0dGVyIGNvZGUgcmVhZGFiaWxpdHk/XG4gKi9cbmV4cG9ydCBmdW5jdGlvbiBnbG9iYWxJbml0KCkge1xuICAgIGFqYXhTZXR1cCgpO1xufVxuXG4vKipcbiAqIEF1dGggSW5pdC5cbiAqL1xuZXhwb3J0IGZ1bmN0aW9uIHVzZXJBdXRoZWRJbml0KCkge1xuICAgIGNvbGxlY3RBdXRoZWRBY3Rpb25zKCk7XG59XG5cbi8qKlxuICogQW5vbiBJbml0LlxuICovXG5leHBvcnQgZnVuY3Rpb24gdXNlckFub25Jbml0KCkge1xuXG59XG5cblxuXG5cbiIsIi8qKlxuICogQGZpbGVcbiAqIFByaW1hcnkgSlMgZmlsZSB0aGF0IGlzIGxvYWRlZCBvbiBldmVyeSBwYWdlLlxuICogV0lQIEpTIFN0cmF0ZWd5LiBUaGlzIGlzIGEgV0lQIGFuZCBtYXkgb3IgbWF5IG5vdCBldmVuIHdvcmsuXG4gKlxuICogSlMgU2NvcGVzOlxuICogR2xvYmFsOiBKUyB0aGF0IGlzIGluY2x1ZGVkIG9uIGV2ZXJ5IHBhZ2UuXG4gKiBVc2VyOiBKUyB0aGF0IGlzIGluY2x1ZGVkIG9uIGV2ZXJ5IHBhZ2UsIGJ1dCBkZXBlbmRzIG9uIGlmIHRoZSB1c2VyIGlzIGF1dGggb3IgYW5vbi5cbiAqIFNlY3Rpb246IEpTIHRoYXQgaXMgb25seSBpbmNsdWRlZCBvbiBhIHNwZWNpZmljIHNlY3Rpb24gb2YgdGhlIHNpdGUuXG4gKlxuICogVGhpcyBmaWxlIGhhbmRsZXMgdGhlIGdsb2JhbCBzY29wZS5cbiAqXG4gKi9cblxudmFyIGdsb2JhbEluaXQgPSByZXF1aXJlKCcuL2NvbXBvbmVudHMvaW5pdCcpLmdsb2JhbEluaXQsXG4gICAgdGVzdCA9IHJlcXVpcmUoJy4vY29tcG9uZW50cy9jb3JlJykudGVzdCxcbiAgICByZXNvdXJjZU1ldGhvZHMgPSByZXF1aXJlKCcuL2NvbXBvbmVudHMvY29tbW9uL3Jlc291cmNlbWV0aG9kcycpO1xuXG4vL1xuLy8gaW5pdCBwYWdlLlxuZ2xvYmFsSW5pdCgpO1xuXG4vKipcbiAqIFJlYWwgZ2VuZXJpYyB3cmFwcGVyIGFyb3VuZCBhamF4IHJlcXVlc3RzLlxuICogQHBhcmFtIG9wdGlvbnNcbiAqIEByZXR1cm5zIHsqfVxuICovXG5leHBvcnQgY29uc3QgcmVxdWVzdCA9IHJlc291cmNlTWV0aG9kcztcbiJdfQ==
