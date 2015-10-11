require=(function e(t,n,r){function s(o,u){if(!n[o]){if(!t[o]){var a=typeof require=="function"&&require;if(!u&&a)return a(o,!0);if(i)return i(o,!0);var f=new Error("Cannot find module '"+o+"'");throw f.code="MODULE_NOT_FOUND",f}var l=n[o]={exports:{}};t[o][0].call(l.exports,function(e){var n=t[o][1][e];return s(n?n:e)},l,l.exports,e,t,n,r)}return n[o].exports}var i=typeof require=="function"&&require;for(var o=0;o<r.length;o++)s(r[o]);return s})({1:[function(require,module,exports){
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

},{}],2:[function(require,module,exports){
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

},{}],3:[function(require,module,exports){
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

},{"./helpers":2}],"sagebrew":[function(require,module,exports){
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
var globalInit = require('./components/init').globalInit;
var test = require('./components/core').test;

//
// init page.
globalInit();

console.log(test());

function abcd() {
  return test();
}

},{"./components/core":1,"./components/init":3}]},{},["sagebrew"])
//# sourceMappingURL=data:application/json;charset:utf-8;base64,eyJ2ZXJzaW9uIjozLCJzb3VyY2VzIjpbIm5vZGVfbW9kdWxlcy9icm93c2VyaWZ5L25vZGVfbW9kdWxlcy9icm93c2VyLXBhY2svX3ByZWx1ZGUuanMiLCIvVXNlcnMvbXdpc25lci9Qcm9qZWN0cy9zYWdlYnJldy9jb20uc2FnZWJyZXcud2ViL3NhZ2VicmV3L3NhZ2VicmV3L3N0YXRpYy9qcy9zcmMvY29tcG9uZW50cy9jb3JlLmpzIiwiL1VzZXJzL213aXNuZXIvUHJvamVjdHMvc2FnZWJyZXcvY29tLnNhZ2VicmV3LndlYi9zYWdlYnJldy9zYWdlYnJldy9zdGF0aWMvanMvc3JjL2NvbXBvbmVudHMvaGVscGVycy5qcyIsIi9Vc2Vycy9td2lzbmVyL1Byb2plY3RzL3NhZ2VicmV3L2NvbS5zYWdlYnJldy53ZWIvc2FnZWJyZXcvc2FnZWJyZXcvc3RhdGljL2pzL3NyYy9jb21wb25lbnRzL2luaXQuanMiLCIvVXNlcnMvbXdpc25lci9Qcm9qZWN0cy9zYWdlYnJldy9jb20uc2FnZWJyZXcud2ViL3NhZ2VicmV3L3NhZ2VicmV3L3N0YXRpYy9qcy9zcmMvc2FnZWJyZXcuanMiXSwibmFtZXMiOltdLCJtYXBwaW5ncyI6IkFBQUE7Ozs7Ozs7Ozs7Ozs7QUNLTyxTQUFTLElBQUksR0FBRztBQUNuQixTQUFPLENBQUMsR0FBRyxDQUFDLFVBQVUsQ0FBQyxDQUFDO0FBQ3hCLFNBQU8sU0FBUyxDQUFDO0NBQ3BCOzs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7QUNFTSxTQUFTLFNBQVMsQ0FBQyxJQUFJLEVBQUU7QUFDNUIsUUFBSSxXQUFXLEdBQUcsSUFBSSxDQUFDO0FBQ3ZCLFFBQUksUUFBUSxDQUFDLE1BQU0sSUFBSSxRQUFRLENBQUMsTUFBTSxLQUFLLEVBQUUsRUFBRTtBQUMzQyxZQUFJLE9BQU8sR0FBRyxRQUFRLENBQUMsTUFBTSxDQUFDLEtBQUssQ0FBQyxHQUFHLENBQUMsQ0FBQztBQUN6QyxhQUFLLElBQUksQ0FBQyxHQUFHLENBQUMsRUFBRSxDQUFDLEdBQUcsT0FBTyxDQUFDLE1BQU0sRUFBRSxDQUFDLElBQUksQ0FBQyxFQUFFO0FBQ3hDLGdCQUFJLE1BQU0sR0FBRyxDQUFDLENBQUMsSUFBSSxDQUFDLE9BQU8sQ0FBQyxDQUFDLENBQUMsQ0FBQyxDQUFDOzs7QUFHaEMsZ0JBQUksTUFBTSxDQUFDLFNBQVMsQ0FBQyxDQUFDLEVBQUUsSUFBSSxDQUFDLE1BQU0sR0FBRyxDQUFDLENBQUMsS0FBTSxJQUFJLEdBQUcsR0FBRyxBQUFDLEVBQUU7QUFDdkQsMkJBQVcsR0FBRyxrQkFBa0IsQ0FBQyxNQUFNLENBQUMsU0FBUyxDQUFDLElBQUksQ0FBQyxNQUFNLEdBQUcsQ0FBQyxDQUFDLENBQUMsQ0FBQztBQUNwRSxzQkFBTTthQUNUO1NBQ0o7S0FDSjtBQUNELFdBQU8sV0FBVyxDQUFDO0NBQ3RCOzs7Ozs7OztBQU9NLFNBQVMsY0FBYyxDQUFDLE1BQU0sRUFBRTs7QUFFbkMsV0FBUSw2QkFBNEIsQ0FBQyxJQUFJLENBQUMsTUFBTSxDQUFDO01BQUU7Q0FDdEQ7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7O0FDMUJELElBQUksT0FBTyxHQUFHLE9BQU8sQ0FBQyxXQUFXLENBQUMsQ0FBQzs7Ozs7OztBQU9uQyxTQUFTLFNBQVMsR0FBRztBQUNqQixLQUFDLENBQUMsU0FBUyxDQUFDO0FBQ1Isa0JBQVUsRUFBRSxvQkFBVSxHQUFHLEVBQUUsUUFBUSxFQUFFO0FBQ2pDLGdCQUFJLENBQUMsT0FBTyxDQUFDLGNBQWMsQ0FBQyxRQUFRLENBQUMsSUFBSSxDQUFDLElBQUksQ0FBQyxJQUFJLENBQUMsV0FBVyxFQUFFO0FBQzdELG1CQUFHLENBQUMsZ0JBQWdCLENBQUMsYUFBYSxFQUFFLE9BQU8sQ0FBQyxTQUFTLENBQUMsV0FBVyxDQUFDLENBQUMsQ0FBQzthQUN2RTtTQUNKO0tBQ0osQ0FBQyxDQUFDO0NBQ047Ozs7Ozs7OztBQVNELFNBQVMsb0JBQW9CLEdBQUc7QUFDNUIsS0FBQyxDQUFDLFFBQVEsQ0FBQyxDQUFDLEtBQUssQ0FBQyxZQUFZO0FBQzFCLG9CQUFZLENBQUM7QUFDYixjQUFNLENBQUMsY0FBYyxHQUFHLFlBQVk7QUFDaEMsZ0JBQUksVUFBVSxHQUFHLEVBQUUsQ0FBQztBQUNwQixhQUFDLENBQUMsaUJBQWlCLENBQUMsQ0FBQyxJQUFJLENBQUMsWUFBWTtBQUNsQywwQkFBVSxDQUFDLElBQUksQ0FBQyxDQUFDLENBQUMsSUFBSSxDQUFDLENBQUMsSUFBSSxDQUFDLGFBQWEsQ0FBQyxDQUFDLENBQUM7YUFDaEQsQ0FBQyxDQUFDO0FBQ0gsZ0JBQUksVUFBVSxDQUFDLE1BQU0sRUFBRTtBQUNuQixpQkFBQyxDQUFDLElBQUksQ0FBQztBQUNILDZCQUFTLEVBQUUsRUFBQyxlQUFlLEVBQUUsSUFBSSxFQUFDO0FBQ2xDLHdCQUFJLEVBQUUsTUFBTTtBQUNaLHlCQUFLLEVBQUUsS0FBSztBQUNaLHVCQUFHLEVBQUUsMkJBQTJCO0FBQ2hDLHdCQUFJLEVBQUUsSUFBSSxDQUFDLFNBQVMsQ0FBQztBQUNqQixzQ0FBYyxFQUFFLFVBQVU7cUJBQzdCLENBQUM7QUFDRiwrQkFBVyxFQUFFLGlDQUFpQztBQUM5Qyw0QkFBUSxFQUFFLE1BQU07QUFDaEIseUJBQUssRUFBRSxlQUFVLGNBQWMsRUFBRTtBQUM3Qiw0QkFBSSxjQUFjLENBQUMsTUFBTSxLQUFLLEdBQUcsRUFBRTtBQUMvQiw2QkFBQyxDQUFDLGVBQWUsQ0FBQyxDQUFDLElBQUksRUFBRSxDQUFDO3lCQUM3QjtxQkFDSjtpQkFDSixDQUFDLENBQUM7YUFDTjtTQUNKLENBQUM7S0FDTCxDQUFDLENBQUM7Q0FDTjs7Ozs7Ozs7QUFTTSxTQUFTLFVBQVUsR0FBRztBQUN6QixXQUFPLENBQUMsR0FBRyxDQUFDLG1CQUFtQixDQUFDLENBQUM7QUFDakMsYUFBUyxFQUFFLENBQUM7QUFDWixXQUFPLENBQUMsR0FBRyxDQUFDLGtCQUFrQixDQUFDLENBQUM7Q0FDbkM7Ozs7OztBQUtNLFNBQVMsY0FBYyxHQUFHO0FBQzdCLFdBQU8sQ0FBQyxHQUFHLENBQUMsc0JBQXNCLENBQUMsQ0FBQztBQUNwQyx3QkFBb0IsRUFBRSxDQUFDO0FBQ3ZCLFdBQU8sQ0FBQyxHQUFHLENBQUMscUJBQXFCLENBQUMsQ0FBQztDQUN0Qzs7Ozs7O0FBS00sU0FBUyxZQUFZLEdBQUc7QUFDM0IsV0FBTyxDQUFDLEdBQUcsQ0FBQyxvQkFBb0IsQ0FBQyxDQUFDO0FBQ2xDLFdBQU8sQ0FBQyxHQUFHLENBQUMsbUJBQW1CLENBQUMsQ0FBQztDQUNwQzs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7QUM3RUQsSUFBSSxVQUFVLEdBQUcsT0FBTyxDQUFDLG1CQUFtQixDQUFDLENBQUMsVUFBVSxDQUFDO0FBQ3pELElBQUksSUFBSSxHQUFHLE9BQU8sQ0FBQyxtQkFBbUIsQ0FBQyxDQUFDLElBQUksQ0FBQzs7OztBQUk3QyxVQUFVLEVBQUUsQ0FBQzs7QUFFYixPQUFPLENBQUMsR0FBRyxDQUFDLElBQUksRUFBRSxDQUFDLENBQUM7O0FBRWIsU0FBUyxJQUFJLEdBQUc7QUFDbkIsU0FBTyxJQUFJLEVBQUUsQ0FBQztDQUNqQiIsImZpbGUiOiJnZW5lcmF0ZWQuanMiLCJzb3VyY2VSb290IjoiIiwic291cmNlc0NvbnRlbnQiOlsiKGZ1bmN0aW9uIGUodCxuLHIpe2Z1bmN0aW9uIHMobyx1KXtpZighbltvXSl7aWYoIXRbb10pe3ZhciBhPXR5cGVvZiByZXF1aXJlPT1cImZ1bmN0aW9uXCImJnJlcXVpcmU7aWYoIXUmJmEpcmV0dXJuIGEobywhMCk7aWYoaSlyZXR1cm4gaShvLCEwKTt2YXIgZj1uZXcgRXJyb3IoXCJDYW5ub3QgZmluZCBtb2R1bGUgJ1wiK28rXCInXCIpO3Rocm93IGYuY29kZT1cIk1PRFVMRV9OT1RfRk9VTkRcIixmfXZhciBsPW5bb109e2V4cG9ydHM6e319O3Rbb11bMF0uY2FsbChsLmV4cG9ydHMsZnVuY3Rpb24oZSl7dmFyIG49dFtvXVsxXVtlXTtyZXR1cm4gcyhuP246ZSl9LGwsbC5leHBvcnRzLGUsdCxuLHIpfXJldHVybiBuW29dLmV4cG9ydHN9dmFyIGk9dHlwZW9mIHJlcXVpcmU9PVwiZnVuY3Rpb25cIiYmcmVxdWlyZTtmb3IodmFyIG89MDtvPHIubGVuZ3RoO28rKylzKHJbb10pO3JldHVybiBzfSkiLCIvKipcbiAqIEBmaWxlXG4gKiBibGFoIGJsYWg/XG4gKi9cblxuZXhwb3J0IGZ1bmN0aW9uIHRlc3QoKSB7XG4gICAgY29uc29sZS5sb2coXCJhc2RmYXNkZlwiKTtcbiAgICByZXR1cm4gJ2FzZGZhZGYnO1xufSIsIi8qKlxuICogQGZpbGVcbiAqIEhlbHBlciBmdW5jdGlvbnMgdGhhdCBhcmVuJ3QgZ2xvYmFsLlxuICovXG5cbi8qKlxuICogR2V0IGNvb2tpZSBiYXNlZCBieSBuYW1lLlxuICogQHBhcmFtIG5hbWVcbiAqIEByZXR1cm5zIHsqfVxuICovXG5leHBvcnQgZnVuY3Rpb24gZ2V0Q29va2llKG5hbWUpIHtcbiAgICB2YXIgY29va2llVmFsdWUgPSBudWxsO1xuICAgIGlmIChkb2N1bWVudC5jb29raWUgJiYgZG9jdW1lbnQuY29va2llICE9PSBcIlwiKSB7XG4gICAgICAgIHZhciBjb29raWVzID0gZG9jdW1lbnQuY29va2llLnNwbGl0KCc7Jyk7XG4gICAgICAgIGZvciAodmFyIGkgPSAwOyBpIDwgY29va2llcy5sZW5ndGg7IGkgKz0gMSkge1xuICAgICAgICAgICAgdmFyIGNvb2tpZSA9ICQudHJpbShjb29raWVzW2ldKTtcbiAgICAgICAgICAgIC8vIERvZXMgdGhpcyBjb29raWUgc3RyaW5nIGJlZ2luIHdpdGggdGhlIG5hbWUgd2Ugd2FudD9cblxuICAgICAgICAgICAgaWYgKGNvb2tpZS5zdWJzdHJpbmcoMCwgbmFtZS5sZW5ndGggKyAxKSA9PT0gKG5hbWUgKyAnPScpKSB7XG4gICAgICAgICAgICAgICAgY29va2llVmFsdWUgPSBkZWNvZGVVUklDb21wb25lbnQoY29va2llLnN1YnN0cmluZyhuYW1lLmxlbmd0aCArIDEpKTtcbiAgICAgICAgICAgICAgICBicmVhaztcbiAgICAgICAgICAgIH1cbiAgICAgICAgfVxuICAgIH1cbiAgICByZXR1cm4gY29va2llVmFsdWU7XG59XG5cbi8qKlxuICogQ2hlY2sgaWYgSFRUUCBtZXRob2QgcmVxdWlyZXMgQ1NSRi5cbiAqIEBwYXJhbSBtZXRob2RcbiAqIEByZXR1cm5zIHtib29sZWFufVxuICovXG5leHBvcnQgZnVuY3Rpb24gY3NyZlNhZmVNZXRob2QobWV0aG9kKSB7XG4gICAgLy8gdGhlc2UgSFRUUCBtZXRob2RzIGRvIG5vdCByZXF1aXJlIENTUkYgcHJvdGVjdGlvblxuICAgIHJldHVybiAoL14oR0VUfEhFQUR8T1BUSU9OU3xUUkFDRSkkLy50ZXN0KG1ldGhvZCkpO1xufSIsIi8qKlxuICogQGZpbGVcbiAqIEluaXQgdGhlIFNCIHdlYnNpdGUuXG4gKiBnbG9iYWxJbml0IC0gUnVucyBvbiBhbGwgcGFnZXMuXG4gKiBVc2VyQXV0aGVkSW5pdCAtIFJ1bnMgb24gYXV0aGVkIHBhZ2VzLlxuICogdXNlckFub25Jbml0IC0gUnVucyBvbiBhbm9uIHBhZ2VzLlxuICogVE9ETzogVGhlIGluZGl2aWR1YWwgaW5pdCBmdW5jdGlvbnMgY291bGQgYmUgdHVybmVkIGludG8gYXJyYXlzIG9yIG9iamVjdHMgYW5kIHRoZW5cbiAqIGxvb3BlZCBvdmVyLlxuICovXG52YXIgaGVscGVycyA9IHJlcXVpcmUoJy4vaGVscGVycycpO1xuXG4vKipcbiAqIFNjb3BlIC0gR2xvYmFsXG4gKiBBamF4IFNldHVwXG4gKiAtLSBBdXRvbWF0aWNhbGx5IGFkZCBDU1JGIGNvb2tpZSB2YWx1ZSB0byBhbGwgYWpheCByZXF1ZXN0cy5cbiAqL1xuZnVuY3Rpb24gYWpheFNldHVwKCkge1xuICAgICQuYWpheFNldHVwKHtcbiAgICAgICAgYmVmb3JlU2VuZDogZnVuY3Rpb24gKHhociwgc2V0dGluZ3MpIHtcbiAgICAgICAgICAgIGlmICghaGVscGVycy5jc3JmU2FmZU1ldGhvZChzZXR0aW5ncy50eXBlKSAmJiAhdGhpcy5jcm9zc0RvbWFpbikge1xuICAgICAgICAgICAgICAgIHhoci5zZXRSZXF1ZXN0SGVhZGVyKFwiWC1DU1JGVG9rZW5cIiwgaGVscGVycy5nZXRDb29raWUoJ2NzcmZ0b2tlbicpKTtcbiAgICAgICAgICAgIH1cbiAgICAgICAgfVxuICAgIH0pO1xufVxuXG4vKipcbiAqICBTY29wZSAtIFVzZXIgQXV0aGVkXG4gKiAgQWRkcyBhbiBldmVudCBoYW5kbGVyIHRvIHBhZ2UgdW5sb2FkIHRoYXQgYWpheCBwb3N0cyBhbGwgdGhlIHVzZXIncyBhY3Rpb25zIHRoYXQgb2NjdXJlZCBkdXJpbmcgdGhlIHBhZ2UuXG4gKiAgVE9ETzogU3RvcCBkb2luZyB0aGlzLlxuICogIE5vdCBvbmx5IGFyZSBub24tYXN5bmMgYWpheCBjYWxscyBkZXByZWNhdGVkIGl0IGhvbGRzIHRoZSBwYWdlIGxvYWQgdXAgZm9yIHRoZSB1c2VyLlxuICogIFRoZXkgY2FuJ3QgZXZlbiBzdGFydCBsb2FkaW5nIHRoZSBuZXh0IHBhZ2UgdW50aWwgdGhpcyBpcyBjb21wbGV0ZWQuXG4gKi9cbmZ1bmN0aW9uIGNvbGxlY3RBdXRoZWRBY3Rpb25zKCkge1xuICAgICQoZG9jdW1lbnQpLnJlYWR5KGZ1bmN0aW9uICgpIHtcbiAgICAgICAgXCJ1c2Ugc3RyaWN0XCI7XG4gICAgICAgIHdpbmRvdy5vbmJlZm9yZXVubG9hZCA9IGZ1bmN0aW9uICgpIHtcbiAgICAgICAgICAgIHZhciBvYmplY3RMaXN0ID0gW107XG4gICAgICAgICAgICAkKFwiLmpzLXBhZ2Utb2JqZWN0XCIpLmVhY2goZnVuY3Rpb24gKCkge1xuICAgICAgICAgICAgICAgIG9iamVjdExpc3QucHVzaCgkKHRoaXMpLmRhdGEoJ29iamVjdF91dWlkJykpO1xuICAgICAgICAgICAgfSk7XG4gICAgICAgICAgICBpZiAob2JqZWN0TGlzdC5sZW5ndGgpIHtcbiAgICAgICAgICAgICAgICAkLmFqYXgoe1xuICAgICAgICAgICAgICAgICAgICB4aHJGaWVsZHM6IHt3aXRoQ3JlZGVudGlhbHM6IHRydWV9LFxuICAgICAgICAgICAgICAgICAgICB0eXBlOiBcIlBPU1RcIixcbiAgICAgICAgICAgICAgICAgICAgYXN5bmM6IGZhbHNlLFxuICAgICAgICAgICAgICAgICAgICB1cmw6IFwiL2RvY3N0b3JlL3VwZGF0ZV9uZW9fYXBpL1wiLFxuICAgICAgICAgICAgICAgICAgICBkYXRhOiBKU09OLnN0cmluZ2lmeSh7XG4gICAgICAgICAgICAgICAgICAgICAgICAnb2JqZWN0X3V1aWRzJzogb2JqZWN0TGlzdFxuICAgICAgICAgICAgICAgICAgICB9KSxcbiAgICAgICAgICAgICAgICAgICAgY29udGVudFR5cGU6IFwiYXBwbGljYXRpb24vanNvbjsgY2hhcnNldD11dGYtOFwiLFxuICAgICAgICAgICAgICAgICAgICBkYXRhVHlwZTogXCJqc29uXCIsXG4gICAgICAgICAgICAgICAgICAgIGVycm9yOiBmdW5jdGlvbiAoWE1MSHR0cFJlcXVlc3QpIHtcbiAgICAgICAgICAgICAgICAgICAgICAgIGlmIChYTUxIdHRwUmVxdWVzdC5zdGF0dXMgPT09IDUwMCkge1xuICAgICAgICAgICAgICAgICAgICAgICAgICAgICQoXCIjc2VydmVyX2Vycm9yXCIpLnNob3coKTtcbiAgICAgICAgICAgICAgICAgICAgICAgIH1cbiAgICAgICAgICAgICAgICAgICAgfVxuICAgICAgICAgICAgICAgIH0pO1xuICAgICAgICAgICAgfVxuICAgICAgICB9O1xuICAgIH0pO1xufVxuXG5cblxuLyoqXG4gKiBUaGlzIGZ1bmN0aW9uIGlzIGNhbGxlZCBpbiBzYWdlYnJldy5qcyBtYWluIGZpbGUuXG4gKiBFYWNoIGluaXQgdGFzayBzaG91bGQgYmUgZGVmaW5lZCBpbiBpdCdzIG93biBmdW5jdGlvbiBmb3Igd2hhdGV2ZXIgcmVhc29uLlxuICogLS0gQmV0dGVyIGNvZGUgcmVhZGFiaWxpdHk/XG4gKi9cbmV4cG9ydCBmdW5jdGlvbiBnbG9iYWxJbml0KCkge1xuICAgIGNvbnNvbGUubG9nKFwiR2xvYmFsIEluaXQgU3RhcnRcIik7XG4gICAgYWpheFNldHVwKCk7XG4gICAgY29uc29sZS5sb2coXCJHbG9iYWwgSW5pdCBTdG9wXCIpO1xufVxuXG4vKipcbiAqIEF1dGggSW5pdC5cbiAqL1xuZXhwb3J0IGZ1bmN0aW9uIHVzZXJBdXRoZWRJbml0KCkge1xuICAgIGNvbnNvbGUubG9nKFwidXNlckF1dGhlZEluaXQgU3RhcnRcIik7XG4gICAgY29sbGVjdEF1dGhlZEFjdGlvbnMoKTtcbiAgICBjb25zb2xlLmxvZyhcInVzZXJBdXRoZWRJbml0IFN0b3BcIik7XG59XG5cbi8qKlxuICogQW5vbiBJbml0LlxuICovXG5leHBvcnQgZnVuY3Rpb24gdXNlckFub25Jbml0KCkge1xuICAgIGNvbnNvbGUubG9nKFwidXNlckFub25Jbml0IFN0YXJ0XCIpO1xuICAgIGNvbnNvbGUubG9nKFwidXNlckFub25Jbml0IFN0b3BcIik7XG59XG5cblxuXG5cbiIsIi8qKlxuICogQGZpbGVcbiAqIFByaW1hcnkgSlMgZmlsZSB0aGF0IGlzIGxvYWRlZCBvbiBldmVyeSBwYWdlLlxuICogV0lQIEpTIFN0cmF0ZWd5LiBUaGlzIGlzIGEgV0lQIGFuZCBtYXkgb3IgbWF5IG5vdCBldmVuIHdvcmsuXG4gKlxuICogSlMgU2NvcGVzOlxuICogR2xvYmFsOiBKUyB0aGF0IGlzIGluY2x1ZGVkIG9uIGV2ZXJ5IHBhZ2UuXG4gKiBVc2VyOiBKUyB0aGF0IGlzIGluY2x1ZGVkIG9uIGV2ZXJ5IHBhZ2UsIGJ1dCBkZXBlbmRzIG9uIGlmIHRoZSB1c2VyIGlzIGF1dGggb3IgYW5vbi5cbiAqIFNlY3Rpb246IEpTIHRoYXQgaXMgb25seSBpbmNsdWRlZCBvbiBhIHNwZWNpZmljIHNlY3Rpb24gb2YgdGhlIHNpdGUuXG4gKlxuICogVGhpcyBmaWxlIGhhbmRsZXMgdGhlIGdsb2JhbCBzY29wZS5cbiAqXG4gKi9cblxudmFyIGdsb2JhbEluaXQgPSByZXF1aXJlKCcuL2NvbXBvbmVudHMvaW5pdCcpLmdsb2JhbEluaXQ7XG52YXIgdGVzdCA9IHJlcXVpcmUoJy4vY29tcG9uZW50cy9jb3JlJykudGVzdDtcblxuLy9cbi8vIGluaXQgcGFnZS5cbmdsb2JhbEluaXQoKTtcblxuY29uc29sZS5sb2codGVzdCgpKTtcblxuZXhwb3J0IGZ1bmN0aW9uIGFiY2QoKSB7XG4gICAgcmV0dXJuIHRlc3QoKTtcbn0iXX0=
