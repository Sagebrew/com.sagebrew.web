require=(function e(t,n,r){function s(o,u){if(!n[o]){if(!t[o]){var a=typeof require=="function"&&require;if(!u&&a)return a(o,!0);if(i)return i(o,!0);var f=new Error("Cannot find module '"+o+"'");throw f.code="MODULE_NOT_FOUND",f}var l=n[o]={exports:{}};t[o][0].call(l.exports,function(e){var n=t[o][1][e];return s(n?n:e)},l,l.exports,e,t,n,r)}return n[o].exports}var i=typeof require=="function"&&require;for(var o=0;o<r.length;o++)s(r[o]);return s})({1:[function(require,module,exports){
/**
 * @file
 * Handles generic ajax requests.
 * Pass in whatever overrides you want, but lets stop the same lines of code over and over again.
 * Don't use directly.
 * use sagebrew.resource instead. see sagebrew.js
 */

"use strict";

Object.defineProperty(exports, "__esModule", {
    value: true
});
exports.get = get;
exports.post = post;
exports.put = put;
exports.remove = remove;
var helpers = require('./../helpers');

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

function get(options) {
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

function post(options) {
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

function put(options) {
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

function remove(options) {
    var defaultOptions = baseOptions();
    defaultOptions.type = "DELETE";
    var settings = $.extend({}, defaultOptions, options);
    console.log("YAY");
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
    console.log("Global Init Start");
    ajaxSetup();
    console.log("Global Init Stop");
}

/**
 * Auth Init.
 */

function userAuthedInit() {
    console.log("userAuthedInit Start");
    collectAuthedActions();
    console.log("userAuthedInit Stop");
}

/**
 * Anon Init.
 */

function userAnonInit() {
    console.log("userAnonInit Start");
    console.log("userAnonInit Stop");
}

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
exports.abcd = abcd;
var globalInit = require('./components/init').globalInit,
    test = require('./components/core').test,
    resourceMethods = require('./components/common/resourcemethods');

//
// init page.
globalInit();

console.log(test());

function abcd() {
  return test();
}

/**
 * Real generic wrapper around ajax requests.
 * @param options
 * @returns {*}
 */
var resource = resourceMethods;
exports.resource = resource;

},{"./components/common/resourcemethods":1,"./components/core":2,"./components/init":4}]},{},["sagebrew"])
//# sourceMappingURL=data:application/json;charset:utf-8;base64,eyJ2ZXJzaW9uIjozLCJzb3VyY2VzIjpbIm5vZGVfbW9kdWxlcy9icm93c2VyaWZ5L25vZGVfbW9kdWxlcy9icm93c2VyLXBhY2svX3ByZWx1ZGUuanMiLCIvVXNlcnMvbXdpc25lci9Qcm9qZWN0cy9zYWdlYnJldy9jb20uc2FnZWJyZXcud2ViL3NhZ2VicmV3L3NhZ2VicmV3L3N0YXRpYy9qcy9zcmMvY29tcG9uZW50cy9jb21tb24vcmVzb3VyY2VtZXRob2RzLmpzIiwiL1VzZXJzL213aXNuZXIvUHJvamVjdHMvc2FnZWJyZXcvY29tLnNhZ2VicmV3LndlYi9zYWdlYnJldy9zYWdlYnJldy9zdGF0aWMvanMvc3JjL2NvbXBvbmVudHMvY29yZS5qcyIsIi9Vc2Vycy9td2lzbmVyL1Byb2plY3RzL3NhZ2VicmV3L2NvbS5zYWdlYnJldy53ZWIvc2FnZWJyZXcvc2FnZWJyZXcvc3RhdGljL2pzL3NyYy9jb21wb25lbnRzL2hlbHBlcnMuanMiLCIvVXNlcnMvbXdpc25lci9Qcm9qZWN0cy9zYWdlYnJldy9jb20uc2FnZWJyZXcud2ViL3NhZ2VicmV3L3NhZ2VicmV3L3N0YXRpYy9qcy9zcmMvY29tcG9uZW50cy9pbml0LmpzIiwiL1VzZXJzL213aXNuZXIvUHJvamVjdHMvc2FnZWJyZXcvY29tLnNhZ2VicmV3LndlYi9zYWdlYnJldy9zYWdlYnJldy9zdGF0aWMvanMvc3JjL3NhZ2VicmV3LmpzIl0sIm5hbWVzIjpbXSwibWFwcGluZ3MiOiJBQUFBOzs7Ozs7Ozs7Ozs7Ozs7Ozs7QUNRQSxJQUFJLE9BQU8sR0FBRyxPQUFPLENBQUMsY0FBYyxDQUFDLENBQUM7O0FBRXRDLFNBQVMsV0FBVyxHQUFHO0FBQ25CLFdBQU87QUFDSCxpQkFBUyxFQUFFLEVBQUMsZUFBZSxFQUFFLElBQUksRUFBQztBQUNsQyxtQkFBVyxFQUFFLGlDQUFpQztBQUM5QyxnQkFBUSxFQUFFLE1BQU07QUFDaEIsa0JBQVUsRUFBRSxvQkFBVSxHQUFHLEVBQUUsUUFBUSxFQUFFO0FBQ2pDLGdCQUFJLENBQUMsT0FBTyxDQUFDLGNB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QUFxQixDQUFDLENBQUM7Q0FDdEM7Ozs7OztBQUtNLFNBQVMsWUFBWSxHQUFHO0FBQzNCLFdBQU8sQ0FBQyxHQUFHLENBQUMsb0JBQW9CLENBQUMsQ0FBQztBQUNsQyxXQUFPLENBQUMsR0FBRyxDQUFDLG1CQUFtQixDQUFDLENBQUM7Q0FDcEM7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7O0FDN0VELElBQUksVUFBVSxHQUFHLE9BQU8sQ0FBQyxtQkFBbUIsQ0FBQyxDQUFDLFVBQVU7SUFDcEQsSUFBSSxHQUFHLE9BQU8sQ0FBQyxtQkFBbUIsQ0FBQyxDQUFDLElBQUk7SUFDeEMsZUFBZSxHQUFHLE9BQU8sQ0FBQyxxQ0FBcUMsQ0FBQyxDQUFDOzs7O0FBSXJFLFVBQVUsRUFBRSxDQUFDOztBQUViLE9BQU8sQ0FBQyxHQUFHLENBQUMsSUFBSSxFQUFFLENBQUMsQ0FBQzs7QUFFYixTQUFTLElBQUksR0FBRztBQUNuQixTQUFPLElBQUksRUFBRSxDQUFDO0NBQ2pCOzs7Ozs7O0FBT00sSUFBTSxRQUFRLEdBQUcsZUFBZSxDQUFDIiwiZmlsZSI6ImdlbmVyYXRlZC5qcyIsInNvdXJjZVJvb3QiOiIiLCJzb3VyY2VzQ29udGVudCI6WyIoZnVuY3Rpb24gZSh0LG4scil7ZnVuY3Rpb24gcyhvLHUpe2lmKCFuW29dKXtpZighdFtvXSl7dmFyIGE9dHlwZW9mIHJlcXVpcmU9PVwiZnVuY3Rpb25cIiYmcmVxdWlyZTtpZighdSYmYSlyZXR1cm4gYShvLCEwKTtpZihpKXJldHVybiBpKG8sITApO3ZhciBmPW5ldyBFcnJvcihcIkNhbm5vdCBmaW5kIG1vZHVsZSAnXCIrbytcIidcIik7dGhyb3cgZi5jb2RlPVwiTU9EVUxFX05PVF9GT1VORFwiLGZ9dmFyIGw9bltvXT17ZXhwb3J0czp7fX07dFtvXVswXS5jYWxsKGwuZXhwb3J0cyxmdW5jdGlvbihlKXt2YXIgbj10W29dWzFdW2VdO3JldHVybiBzKG4/bjplKX0sbCxsLmV4cG9ydHMsZSx0LG4scil9cmV0dXJuIG5bb10uZXhwb3J0c312YXIgaT10eXBlb2YgcmVxdWlyZT09XCJmdW5jdGlvblwiJiZyZXF1aXJlO2Zvcih2YXIgbz0wO288ci5sZW5ndGg7bysrKXMocltvXSk7cmV0dXJuIHN9KSIsIi8qKlxuICogQGZpbGVcbiAqIEhhbmRsZXMgZ2VuZXJpYyBhamF4IHJlcXVlc3RzLlxuICogUGFzcyBpbiB3aGF0ZXZlciBvdmVycmlkZXMgeW91IHdhbnQsIGJ1dCBsZXRzIHN0b3AgdGhlIHNhbWUgbGluZXMgb2YgY29kZSBvdmVyIGFuZCBvdmVyIGFnYWluLlxuICogRG9uJ3QgdXNlIGRpcmVjdGx5LlxuICogdXNlIHNhZ2VicmV3LnJlc291cmNlIGluc3RlYWQuIHNlZSBzYWdlYnJldy5qc1xuICovXG5cbnZhciBoZWxwZXJzID0gcmVxdWlyZSgnLi8uLi9oZWxwZXJzJyk7XG5cbmZ1bmN0aW9uIGJhc2VPcHRpb25zKCkge1xuICAgIHJldHVybiB7XG4gICAgICAgIHhockZpZWxkczoge3dpdGhDcmVkZW50aWFsczogdHJ1ZX0sXG4gICAgICAgIGNvbnRlbnRUeXBlOiBcImFwcGxpY2F0aW9uL2pzb247IGNoYXJzZXQ9dXRmLThcIixcbiAgICAgICAgZGF0YVR5cGU6IFwianNvblwiLFxuICAgICAgICBiZWZvcmVTZW5kOiBmdW5jdGlvbiAoeGhyLCBzZXR0aW5ncykge1xuICAgICAgICAgICAgaWYgKCFoZWxwZXJzLmNzcmZTYWZlTWV0aG9kKHNldHRpbmdzLnR5cGUpICYmICF0aGlzLmNyb3NzRG9tYWluKSB7XG4gICAgICAgICAgICAgICAgeGhyLnNldFJlcXVlc3RIZWFkZXIoXCJYLUNTUkZUb2tlblwiLCBoZWxwZXJzLmdldENvb2tpZSgnY3NyZnRva2VuJykpO1xuICAgICAgICAgICAgfVxuICAgICAgICB9LFxuICAgICAgICBlcnJvcjogZnVuY3Rpb24gKFhNTEh0dHBSZXF1ZXN0KSB7XG4gICAgICAgICAgICBpZiAoWE1MSHR0cFJlcXVlc3Quc3RhdHVzID09PSA1MDApIHtcbiAgICAgICAgICAgICAgICAkKFwiI3NlcnZlcl9lcnJvclwiKS5zaG93KCk7XG4gICAgICAgICAgICB9XG4gICAgICAgIH1cbiAgICB9O1xufVxuXG4vKipcbiAqIEdFVFxuICogQHBhcmFtIG9wdGlvbnNcbiAqIEByZXR1cm5zIHsqfVxuICovXG5leHBvcnQgZnVuY3Rpb24gZ2V0KG9wdGlvbnMpIHtcbiAgICB2YXIgZGVmYXVsdE9wdGlvbnMgPSBiYXNlT3B0aW9ucygpO1xuICAgIGRlZmF1bHRPcHRpb25zLnR5cGUgPSBcIkdFVFwiO1xuICAgIHZhciBzZXR0aW5ncyA9ICQuZXh0ZW5kKHt9LCBkZWZhdWx0T3B0aW9ucywgb3B0aW9ucyk7XG4gICAgY29uc29sZS5sb2coXCJZQVlcIik7XG4gICAgcmV0dXJuICQuYWpheChzZXR0aW5ncyk7XG59XG5cbi8qKlxuICogUE9TVFxuICogQHBhcmFtIG9wdGlvbnNcbiAqIEByZXR1cm5zIHsqfVxuICovXG5leHBvcnQgZnVuY3Rpb24gcG9zdChvcHRpb25zKSB7XG4gICAgdmFyIGRlZmF1bHRPcHRpb25zID0gYmFzZU9wdGlvbnMoKTtcbiAgICBkZWZhdWx0T3B0aW9ucy50eXBlID0gXCJQT1NUXCI7XG4gICAgdmFyIHNldHRpbmdzID0gJC5leHRlbmQoe30sIGRlZmF1bHRPcHRpb25zLCBvcHRpb25zKTtcbiAgICBjb25zb2xlLmxvZyhcIllBWVwiKTtcbiAgICByZXR1cm4gJC5hamF4KHNldHRpbmdzKTtcbn1cblxuLyoqXG4gKiBQVVRcbiAqIEBwYXJhbSBvcHRpb25zXG4gKiBAcmV0dXJucyB7Kn1cbiAqL1xuZXhwb3J0IGZ1bmN0aW9uIHB1dChvcHRpb25zKSB7XG4gICAgdmFyIGRlZmF1bHRPcHRpb25zID0gYmFzZU9wdGlvbnMoKTtcbiAgICBkZWZhdWx0T3B0aW9ucy50eXBlID0gXCJQVVRcIjtcbiAgICB2YXIgc2V0dGluZ3MgPSAkLmV4dGVuZCh7fSwgZGVmYXVsdE9wdGlvbnMsIG9wdGlvbnMpO1xuICAgIGNvbnNvbGUubG9nKFwiWUFZXCIpO1xuICAgIHJldHVybiAkLmFqYXgoc2V0dGluZ3MpO1xufVxuXG4vKipcbiAqIERFTEVURVxuICogZGVsZXRlIGlzIGEgcmVzZXJ2ZWQgd29yZCBpbiBqcyBzbyB3ZSBjYW50IHVzZSBpdCBhcyB0aGUgZnVuY3Rpb24gbmFtZVxuICogPShcbiAqIEBwYXJhbSBvcHRpb25zXG4gKiBAcmV0dXJucyB7Kn1cbiAqL1xuZXhwb3J0IGZ1bmN0aW9uIHJlbW92ZShvcHRpb25zKSB7XG4gICAgdmFyIGRlZmF1bHRPcHRpb25zID0gYmFzZU9wdGlvbnMoKTtcbiAgICBkZWZhdWx0T3B0aW9ucy50eXBlID0gXCJERUxFVEVcIjtcbiAgICB2YXIgc2V0dGluZ3MgPSAkLmV4dGVuZCh7fSwgZGVmYXVsdE9wdGlvbnMsIG9wdGlvbnMpO1xuICAgIGNvbnNvbGUubG9nKFwiWUFZXCIpO1xuICAgIHJldHVybiAkLmFqYXgoc2V0dGluZ3MpO1xufSIsIi8qKlxuICogQGZpbGVcbiAqIGJsYWggYmxhaD9cbiAqL1xuXG5leHBvcnQgZnVuY3Rpb24gdGVzdCgpIHtcbiAgICBjb25zb2xlLmxvZyhcImFzZGZhc2RmXCIpO1xuICAgIHJldHVybiAnYXNkZmFkZic7XG59IiwiLyoqXG4gKiBAZmlsZVxuICogSGVscGVyIGZ1bmN0aW9ucyB0aGF0IGFyZW4ndCBnbG9iYWwuXG4gKi9cblxuLyoqXG4gKiBHZXQgY29va2llIGJhc2VkIGJ5IG5hbWUuXG4gKiBAcGFyYW0gbmFtZVxuICogQHJldHVybnMgeyp9XG4gKi9cbmV4cG9ydCBmdW5jdGlvbiBnZXRDb29raWUobmFtZSkge1xuICAgIHZhciBjb29raWVWYWx1ZSA9IG51bGw7XG4gICAgaWYgKGRvY3VtZW50LmNvb2tpZSAmJiBkb2N1bWVudC5jb29raWUgIT09IFwiXCIpIHtcbiAgICAgICAgdmFyIGNvb2tpZXMgPSBkb2N1bWVudC5jb29raWUuc3BsaXQoJzsnKTtcbiAgICAgICAgZm9yICh2YXIgaSA9IDA7IGkgPCBjb29raWVzLmxlbmd0aDsgaSArPSAxKSB7XG4gICAgICAgICAgICB2YXIgY29va2llID0gJC50cmltKGNvb2tpZXNbaV0pO1xuICAgICAgICAgICAgLy8gRG9lcyB0aGlzIGNvb2tpZSBzdHJpbmcgYmVnaW4gd2l0aCB0aGUgbmFtZSB3ZSB3YW50P1xuXG4gICAgICAgICAgICBpZiAoY29va2llLnN1YnN0cmluZygwLCBuYW1lLmxlbmd0aCArIDEpID09PSAobmFtZSArICc9JykpIHtcbiAgICAgICAgICAgICAgICBjb29raWVWYWx1ZSA9IGRlY29kZVVSSUNvbXBvbmVudChjb29raWUuc3Vic3RyaW5nKG5hbWUubGVuZ3RoICsgMSkpO1xuICAgICAgICAgICAgICAgIGJyZWFrO1xuICAgICAgICAgICAgfVxuICAgICAgICB9XG4gICAgfVxuICAgIHJldHVybiBjb29raWVWYWx1ZTtcbn1cblxuLyoqXG4gKiBDaGVjayBpZiBIVFRQIG1ldGhvZCByZXF1aXJlcyBDU1JGLlxuICogQHBhcmFtIG1ldGhvZFxuICogQHJldHVybnMge2Jvb2xlYW59XG4gKi9cbmV4cG9ydCBmdW5jdGlvbiBjc3JmU2FmZU1ldGhvZChtZXRob2QpIHtcbiAgICAvLyB0aGVzZSBIVFRQIG1ldGhvZHMgZG8gbm90IHJlcXVpcmUgQ1NSRiBwcm90ZWN0aW9uXG4gICAgcmV0dXJuICgvXihHRVR8SEVBRHxPUFRJT05TfFRSQUNFKSQvLnRlc3QobWV0aG9kKSk7XG59IiwiLyoqXG4gKiBAZmlsZVxuICogSW5pdCB0aGUgU0Igd2Vic2l0ZS5cbiAqIGdsb2JhbEluaXQgLSBSdW5zIG9uIGFsbCBwYWdlcy5cbiAqIFVzZXJBdXRoZWRJbml0IC0gUnVucyBvbiBhdXRoZWQgcGFnZXMuXG4gKiB1c2VyQW5vbkluaXQgLSBSdW5zIG9uIGFub24gcGFnZXMuXG4gKiBUT0RPOiBUaGUgaW5kaXZpZHVhbCBpbml0IGZ1bmN0aW9ucyBjb3VsZCBiZSB0dXJuZWQgaW50byBhcnJheXMgb3Igb2JqZWN0cyBhbmQgdGhlblxuICogbG9vcGVkIG92ZXIuXG4gKi9cbnZhciBoZWxwZXJzID0gcmVxdWlyZSgnLi9oZWxwZXJzJyk7XG5cbi8qKlxuICogU2NvcGUgLSBHbG9iYWxcbiAqIEFqYXggU2V0dXBcbiAqIC0tIEF1dG9tYXRpY2FsbHkgYWRkIENTUkYgY29va2llIHZhbHVlIHRvIGFsbCBhamF4IHJlcXVlc3RzLlxuICovXG5mdW5jdGlvbiBhamF4U2V0dXAoKSB7XG4gICAgJC5hamF4U2V0dXAoe1xuICAgICAgICBiZWZvcmVTZW5kOiBmdW5jdGlvbiAoeGhyLCBzZXR0aW5ncykge1xuICAgICAgICAgICAgaWYgKCFoZWxwZXJzLmNzcmZTYWZlTWV0aG9kKHNldHRpbmdzLnR5cGUpICYmICF0aGlzLmNyb3NzRG9tYWluKSB7XG4gICAgICAgICAgICAgICAgeGhyLnNldFJlcXVlc3RIZWFkZXIoXCJYLUNTUkZUb2tlblwiLCBoZWxwZXJzLmdldENvb2tpZSgnY3NyZnRva2VuJykpO1xuICAgICAgICAgICAgfVxuICAgICAgICB9XG4gICAgfSk7XG59XG5cbi8qKlxuICogIFNjb3BlIC0gVXNlciBBdXRoZWRcbiAqICBBZGRzIGFuIGV2ZW50IGhhbmRsZXIgdG8gcGFnZSB1bmxvYWQgdGhhdCBhamF4IHBvc3RzIGFsbCB0aGUgdXNlcidzIGFjdGlvbnMgdGhhdCBvY2N1cmVkIGR1cmluZyB0aGUgcGFnZS5cbiAqICBUT0RPOiBTdG9wIGRvaW5nIHRoaXMuXG4gKiAgTm90IG9ubHkgYXJlIG5vbi1hc3luYyBhamF4IGNhbGxzIGRlcHJlY2F0ZWQgaXQgaG9sZHMgdGhlIHBhZ2UgbG9hZCB1cCBmb3IgdGhlIHVzZXIuXG4gKiAgVGhleSBjYW4ndCBldmVuIHN0YXJ0IGxvYWRpbmcgdGhlIG5leHQgcGFnZSB1bnRpbCB0aGlzIGlzIGNvbXBsZXRlZC5cbiAqL1xuZnVuY3Rpb24gY29sbGVjdEF1dGhlZEFjdGlvbnMoKSB7XG4gICAgJChkb2N1bWVudCkucmVhZHkoZnVuY3Rpb24gKCkge1xuICAgICAgICBcInVzZSBzdHJpY3RcIjtcbiAgICAgICAgd2luZG93Lm9uYmVmb3JldW5sb2FkID0gZnVuY3Rpb24gKCkge1xuICAgICAgICAgICAgdmFyIG9iamVjdExpc3QgPSBbXTtcbiAgICAgICAgICAgICQoXCIuanMtcGFnZS1vYmplY3RcIikuZWFjaChmdW5jdGlvbiAoKSB7XG4gICAgICAgICAgICAgICAgb2JqZWN0TGlzdC5wdXNoKCQodGhpcykuZGF0YSgnb2JqZWN0X3V1aWQnKSk7XG4gICAgICAgICAgICB9KTtcbiAgICAgICAgICAgIGlmIChvYmplY3RMaXN0Lmxlbmd0aCkge1xuICAgICAgICAgICAgICAgICQuYWpheCh7XG4gICAgICAgICAgICAgICAgICAgIHhockZpZWxkczoge3dpdGhDcmVkZW50aWFsczogdHJ1ZX0sXG4gICAgICAgICAgICAgICAgICAgIHR5cGU6IFwiUE9TVFwiLFxuICAgICAgICAgICAgICAgICAgICBhc3luYzogZmFsc2UsXG4gICAgICAgICAgICAgICAgICAgIHVybDogXCIvZG9jc3RvcmUvdXBkYXRlX25lb19hcGkvXCIsXG4gICAgICAgICAgICAgICAgICAgIGRhdGE6IEpTT04uc3RyaW5naWZ5KHtcbiAgICAgICAgICAgICAgICAgICAgICAgICdvYmplY3RfdXVpZHMnOiBvYmplY3RMaXN0XG4gICAgICAgICAgICAgICAgICAgIH0pLFxuICAgICAgICAgICAgICAgICAgICBjb250ZW50VHlwZTogXCJhcHBsaWNhdGlvbi9qc29uOyBjaGFyc2V0PXV0Zi04XCIsXG4gICAgICAgICAgICAgICAgICAgIGRhdGFUeXBlOiBcImpzb25cIixcbiAgICAgICAgICAgICAgICAgICAgZXJyb3I6IGZ1bmN0aW9uIChYTUxIdHRwUmVxdWVzdCkge1xuICAgICAgICAgICAgICAgICAgICAgICAgaWYgKFhNTEh0dHBSZXF1ZXN0LnN0YXR1cyA9PT0gNTAwKSB7XG4gICAgICAgICAgICAgICAgICAgICAgICAgICAgJChcIiNzZXJ2ZXJfZXJyb3JcIikuc2hvdygpO1xuICAgICAgICAgICAgICAgICAgICAgICAgfVxuICAgICAgICAgICAgICAgICAgICB9XG4gICAgICAgICAgICAgICAgfSk7XG4gICAgICAgICAgICB9XG4gICAgICAgIH07XG4gICAgfSk7XG59XG5cblxuXG4vKipcbiAqIFRoaXMgZnVuY3Rpb24gaXMgY2FsbGVkIGluIHNhZ2VicmV3LmpzIG1haW4gZmlsZS5cbiAqIEVhY2ggaW5pdCB0YXNrIHNob3VsZCBiZSBkZWZpbmVkIGluIGl0J3Mgb3duIGZ1bmN0aW9uIGZvciB3aGF0ZXZlciByZWFzb24uXG4gKiAtLSBCZXR0ZXIgY29kZSByZWFkYWJpbGl0eT9cbiAqL1xuZXhwb3J0IGZ1bmN0aW9uIGdsb2JhbEluaXQoKSB7XG4gICAgY29uc29sZS5sb2coXCJHbG9iYWwgSW5pdCBTdGFydFwiKTtcbiAgICBhamF4U2V0dXAoKTtcbiAgICBjb25zb2xlLmxvZyhcIkdsb2JhbCBJbml0IFN0b3BcIik7XG59XG5cbi8qKlxuICogQXV0aCBJbml0LlxuICovXG5leHBvcnQgZnVuY3Rpb24gdXNlckF1dGhlZEluaXQoKSB7XG4gICAgY29uc29sZS5sb2coXCJ1c2VyQXV0aGVkSW5pdCBTdGFydFwiKTtcbiAgICBjb2xsZWN0QXV0aGVkQWN0aW9ucygpO1xuICAgIGNvbnNvbGUubG9nKFwidXNlckF1dGhlZEluaXQgU3RvcFwiKTtcbn1cblxuLyoqXG4gKiBBbm9uIEluaXQuXG4gKi9cbmV4cG9ydCBmdW5jdGlvbiB1c2VyQW5vbkluaXQoKSB7XG4gICAgY29uc29sZS5sb2coXCJ1c2VyQW5vbkluaXQgU3RhcnRcIik7XG4gICAgY29uc29sZS5sb2coXCJ1c2VyQW5vbkluaXQgU3RvcFwiKTtcbn1cblxuXG5cblxuIiwiLyoqXG4gKiBAZmlsZVxuICogUHJpbWFyeSBKUyBmaWxlIHRoYXQgaXMgbG9hZGVkIG9uIGV2ZXJ5IHBhZ2UuXG4gKiBXSVAgSlMgU3RyYXRlZ3kuIFRoaXMgaXMgYSBXSVAgYW5kIG1heSBvciBtYXkgbm90IGV2ZW4gd29yay5cbiAqXG4gKiBKUyBTY29wZXM6XG4gKiBHbG9iYWw6IEpTIHRoYXQgaXMgaW5jbHVkZWQgb24gZXZlcnkgcGFnZS5cbiAqIFVzZXI6IEpTIHRoYXQgaXMgaW5jbHVkZWQgb24gZXZlcnkgcGFnZSwgYnV0IGRlcGVuZHMgb24gaWYgdGhlIHVzZXIgaXMgYXV0aCBvciBhbm9uLlxuICogU2VjdGlvbjogSlMgdGhhdCBpcyBvbmx5IGluY2x1ZGVkIG9uIGEgc3BlY2lmaWMgc2VjdGlvbiBvZiB0aGUgc2l0ZS5cbiAqXG4gKiBUaGlzIGZpbGUgaGFuZGxlcyB0aGUgZ2xvYmFsIHNjb3BlLlxuICpcbiAqL1xuXG52YXIgZ2xvYmFsSW5pdCA9IHJlcXVpcmUoJy4vY29tcG9uZW50cy9pbml0JykuZ2xvYmFsSW5pdCxcbiAgICB0ZXN0ID0gcmVxdWlyZSgnLi9jb21wb25lbnRzL2NvcmUnKS50ZXN0LFxuICAgIHJlc291cmNlTWV0aG9kcyA9IHJlcXVpcmUoJy4vY29tcG9uZW50cy9jb21tb24vcmVzb3VyY2VtZXRob2RzJyk7XG5cbi8vXG4vLyBpbml0IHBhZ2UuXG5nbG9iYWxJbml0KCk7XG5cbmNvbnNvbGUubG9nKHRlc3QoKSk7XG5cbmV4cG9ydCBmdW5jdGlvbiBhYmNkKCkge1xuICAgIHJldHVybiB0ZXN0KCk7XG59XG5cbi8qKlxuICogUmVhbCBnZW5lcmljIHdyYXBwZXIgYXJvdW5kIGFqYXggcmVxdWVzdHMuXG4gKiBAcGFyYW0gb3B0aW9uc1xuICogQHJldHVybnMgeyp9XG4gKi9cbmV4cG9ydCBjb25zdCByZXNvdXJjZSA9IHJlc291cmNlTWV0aG9kcztcbiJdfQ==
