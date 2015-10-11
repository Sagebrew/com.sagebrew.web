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
 * Init the SB website. This runs on all pages.
 */
'use strict';

Object.defineProperty(exports, '__esModule', {
    value: true
});
exports.init = init;
var helpers = require('./helpers');

/**
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
 * This function is called in sagebrew.js main file.
 * Each init task should be defined in it's own function for whatever reason.
 * -- Better code readability?
 */

function init() {
    ajaxSetup();
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
var init = require('./components/init').init;
var test = require('./components/core').test;

//
// init page.
init();

console.log(test());

function abcd() {
  return test();
}

},{"./components/core":1,"./components/init":3}]},{},["sagebrew"])
//# sourceMappingURL=data:application/json;charset:utf-8;base64,eyJ2ZXJzaW9uIjozLCJzb3VyY2VzIjpbIm5vZGVfbW9kdWxlcy9icm93c2VyaWZ5L25vZGVfbW9kdWxlcy9icm93c2VyLXBhY2svX3ByZWx1ZGUuanMiLCIvVXNlcnMvbXdpc25lci9Qcm9qZWN0cy9zYWdlYnJldy9jb20uc2FnZWJyZXcud2ViL3NhZ2VicmV3L3NhZ2VicmV3L3N0YXRpYy9qcy9zcmMvY29tcG9uZW50cy9jb3JlLmpzIiwiL1VzZXJzL213aXNuZXIvUHJvamVjdHMvc2FnZWJyZXcvY29tLnNhZ2VicmV3LndlYi9zYWdlYnJldy9zYWdlYnJldy9zdGF0aWMvanMvc3JjL2NvbXBvbmVudHMvaGVscGVycy5qcyIsIi9Vc2Vycy9td2lzbmVyL1Byb2plY3RzL3NhZ2VicmV3L2NvbS5zYWdlYnJldy53ZWIvc2FnZWJyZXcvc2FnZWJyZXcvc3RhdGljL2pzL3NyYy9jb21wb25lbnRzL2luaXQuanMiLCIvVXNlcnMvbXdpc25lci9Qcm9qZWN0cy9zYWdlYnJldy9jb20uc2FnZWJyZXcud2ViL3NhZ2VicmV3L3NhZ2VicmV3L3N0YXRpYy9qcy9zcmMvc2FnZWJyZXcuanMiXSwibmFtZXMiOltdLCJtYXBwaW5ncyI6IkFBQUE7Ozs7Ozs7Ozs7Ozs7QUNLTyxTQUFTLElBQUksR0FBRztBQUNuQixTQUFPLENBQUMsR0FBRyxDQUFDLFVBQVUsQ0FBQyxDQUFDO0FBQ3hCLFNBQU8sU0FBUyxDQUFDO0NBQ3BCOzs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7QUNFTSxTQUFTLFNBQVMsQ0FBQyxJQUFJLEVBQUU7QUFDNUIsUUFBSSxXQUFXLEdBQUcsSUFBSSxDQUFDO0FBQ3ZCLFFBQUksUUFBUSxDQUFDLE1BQU0sSUFBSSxRQUFRLENBQUMsTUFBTSxLQUFLLEVBQUUsRUFBRTtBQUMzQyxZQUFJLE9BQU8sR0FBRyxRQUFRLENBQUMsTUFBTSxDQUFDLEtBQUssQ0FBQyxHQUFHLENBQUMsQ0FBQztBQUN6QyxhQUFLLElBQUksQ0FBQyxHQUFHLENBQUMsRUFBRSxDQUFDLEdBQUcsT0FBTyxDQUFDLE1BQU0sRUFBRSxDQUFDLElBQUksQ0FBQyxFQUFFO0FBQ3hDLGdCQUFJLE1BQU0sR0FBRyxDQUFDLENBQUMsSUFBSSxDQUFDLE9BQU8sQ0FBQyxDQUFDLENBQUMsQ0FBQyxDQUFDOzs7QUFHaEMsZ0JBQUksTUFBTSxDQUFDLFNBQVMsQ0FBQyxDQUFDLEVBQUUsSUFBSSxDQUFDLE1BQU0sR0FBRyxDQUFDLENBQUMsS0FBTSxJQUFJLEdBQUcsR0FBRyxBQUFDLEVBQUU7QUFDdkQsMkJBQVcsR0FBRyxrQkFBa0IsQ0FBQyxNQUFNLENBQUMsU0FBUyxDQUFDLElBQUksQ0FBQyxNQUFNLEdBQUcsQ0FBQyxDQUFDLENBQUMsQ0FBQztBQUNwRSxzQkFBTTthQUNUO1NBQ0o7S0FDSjtBQUNELFdBQU8sV0FBVyxDQUFDO0NBQ3RCOzs7Ozs7OztBQU9NLFNBQVMsY0FBYyxDQUFDLE1BQU0sRUFBRTs7QUFFbkMsV0FBUSw2QkFBNEIsQ0FBQyxJQUFJLENBQUMsTUFBTSxDQUFDO01BQUU7Q0FDdEQ7Ozs7Ozs7Ozs7Ozs7QUMvQkQsSUFBSSxPQUFPLEdBQUcsT0FBTyxDQUFDLFdBQVcsQ0FBQyxDQUFDOzs7Ozs7QUFNbkMsU0FBUyxTQUFTLEdBQUc7QUFDakIsS0FBQyxDQUFDLFNBQVMsQ0FBQztBQUNSLGtCQUFVLEVBQUUsb0JBQVUsR0FBRyxFQUFFLFFBQVEsRUFBRTtBQUNqQyxnQkFBSSxDQUFDLE9BQU8sQ0FBQyxjQUFjLENBQUMsUUFBUSxDQUFDLElBQUksQ0FBQyxJQUFJLENBQUMsSUFBSSxDQUFDLFdBQVcsRUFBRTtBQUM3RCxtQkFBRyxDQUFDLGdCQUFnQixDQUFDLGFBQWEsRUFBRSxPQUFPLENBQUMsU0FBUyxDQUFDLFdBQVcsQ0FBQyxDQUFDLENBQUM7YUFDdkU7U0FDSjtLQUNKLENBQUMsQ0FBQztDQUNOOzs7Ozs7OztBQU9NLFNBQVMsSUFBSSxHQUFHO0FBQ25CLGFBQVMsRUFBRSxDQUFDO0NBQ2Y7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7O0FDYkQsSUFBSSxJQUFJLEdBQUcsT0FBTyxDQUFDLG1CQUFtQixDQUFDLENBQUMsSUFBSSxDQUFDO0FBQzdDLElBQUksSUFBSSxHQUFHLE9BQU8sQ0FBQyxtQkFBbUIsQ0FBQyxDQUFDLElBQUksQ0FBQzs7OztBQUk3QyxJQUFJLEVBQUUsQ0FBQzs7QUFFUCxPQUFPLENBQUMsR0FBRyxDQUFDLElBQUksRUFBRSxDQUFDLENBQUM7O0FBRWIsU0FBUyxJQUFJLEdBQUc7QUFDbkIsU0FBTyxJQUFJLEVBQUUsQ0FBQztDQUNqQiIsImZpbGUiOiJnZW5lcmF0ZWQuanMiLCJzb3VyY2VSb290IjoiIiwic291cmNlc0NvbnRlbnQiOlsiKGZ1bmN0aW9uIGUodCxuLHIpe2Z1bmN0aW9uIHMobyx1KXtpZighbltvXSl7aWYoIXRbb10pe3ZhciBhPXR5cGVvZiByZXF1aXJlPT1cImZ1bmN0aW9uXCImJnJlcXVpcmU7aWYoIXUmJmEpcmV0dXJuIGEobywhMCk7aWYoaSlyZXR1cm4gaShvLCEwKTt2YXIgZj1uZXcgRXJyb3IoXCJDYW5ub3QgZmluZCBtb2R1bGUgJ1wiK28rXCInXCIpO3Rocm93IGYuY29kZT1cIk1PRFVMRV9OT1RfRk9VTkRcIixmfXZhciBsPW5bb109e2V4cG9ydHM6e319O3Rbb11bMF0uY2FsbChsLmV4cG9ydHMsZnVuY3Rpb24oZSl7dmFyIG49dFtvXVsxXVtlXTtyZXR1cm4gcyhuP246ZSl9LGwsbC5leHBvcnRzLGUsdCxuLHIpfXJldHVybiBuW29dLmV4cG9ydHN9dmFyIGk9dHlwZW9mIHJlcXVpcmU9PVwiZnVuY3Rpb25cIiYmcmVxdWlyZTtmb3IodmFyIG89MDtvPHIubGVuZ3RoO28rKylzKHJbb10pO3JldHVybiBzfSkiLCIvKipcbiAqIEBmaWxlXG4gKiBibGFoIGJsYWg/XG4gKi9cblxuZXhwb3J0IGZ1bmN0aW9uIHRlc3QoKSB7XG4gICAgY29uc29sZS5sb2coXCJhc2RmYXNkZlwiKTtcbiAgICByZXR1cm4gJ2FzZGZhZGYnO1xufSIsIi8qKlxuICogQGZpbGVcbiAqIEhlbHBlciBmdW5jdGlvbnMgdGhhdCBhcmVuJ3QgZ2xvYmFsLlxuICovXG5cbi8qKlxuICogR2V0IGNvb2tpZSBiYXNlZCBieSBuYW1lLlxuICogQHBhcmFtIG5hbWVcbiAqIEByZXR1cm5zIHsqfVxuICovXG5leHBvcnQgZnVuY3Rpb24gZ2V0Q29va2llKG5hbWUpIHtcbiAgICB2YXIgY29va2llVmFsdWUgPSBudWxsO1xuICAgIGlmIChkb2N1bWVudC5jb29raWUgJiYgZG9jdW1lbnQuY29va2llICE9PSBcIlwiKSB7XG4gICAgICAgIHZhciBjb29raWVzID0gZG9jdW1lbnQuY29va2llLnNwbGl0KCc7Jyk7XG4gICAgICAgIGZvciAodmFyIGkgPSAwOyBpIDwgY29va2llcy5sZW5ndGg7IGkgKz0gMSkge1xuICAgICAgICAgICAgdmFyIGNvb2tpZSA9ICQudHJpbShjb29raWVzW2ldKTtcbiAgICAgICAgICAgIC8vIERvZXMgdGhpcyBjb29raWUgc3RyaW5nIGJlZ2luIHdpdGggdGhlIG5hbWUgd2Ugd2FudD9cblxuICAgICAgICAgICAgaWYgKGNvb2tpZS5zdWJzdHJpbmcoMCwgbmFtZS5sZW5ndGggKyAxKSA9PT0gKG5hbWUgKyAnPScpKSB7XG4gICAgICAgICAgICAgICAgY29va2llVmFsdWUgPSBkZWNvZGVVUklDb21wb25lbnQoY29va2llLnN1YnN0cmluZyhuYW1lLmxlbmd0aCArIDEpKTtcbiAgICAgICAgICAgICAgICBicmVhaztcbiAgICAgICAgICAgIH1cbiAgICAgICAgfVxuICAgIH1cbiAgICByZXR1cm4gY29va2llVmFsdWU7XG59XG5cbi8qKlxuICogQ2hlY2sgaWYgSFRUUCBtZXRob2QgcmVxdWlyZXMgQ1NSRi5cbiAqIEBwYXJhbSBtZXRob2RcbiAqIEByZXR1cm5zIHtib29sZWFufVxuICovXG5leHBvcnQgZnVuY3Rpb24gY3NyZlNhZmVNZXRob2QobWV0aG9kKSB7XG4gICAgLy8gdGhlc2UgSFRUUCBtZXRob2RzIGRvIG5vdCByZXF1aXJlIENTUkYgcHJvdGVjdGlvblxuICAgIHJldHVybiAoL14oR0VUfEhFQUR8T1BUSU9OU3xUUkFDRSkkLy50ZXN0KG1ldGhvZCkpO1xufSIsIi8qKlxuICogQGZpbGVcbiAqIEluaXQgdGhlIFNCIHdlYnNpdGUuIFRoaXMgcnVucyBvbiBhbGwgcGFnZXMuXG4gKi9cbnZhciBoZWxwZXJzID0gcmVxdWlyZSgnLi9oZWxwZXJzJyk7XG5cbi8qKlxuICogQWpheCBTZXR1cFxuICogLS0gQXV0b21hdGljYWxseSBhZGQgQ1NSRiBjb29raWUgdmFsdWUgdG8gYWxsIGFqYXggcmVxdWVzdHMuXG4gKi9cbmZ1bmN0aW9uIGFqYXhTZXR1cCgpIHtcbiAgICAkLmFqYXhTZXR1cCh7XG4gICAgICAgIGJlZm9yZVNlbmQ6IGZ1bmN0aW9uICh4aHIsIHNldHRpbmdzKSB7XG4gICAgICAgICAgICBpZiAoIWhlbHBlcnMuY3NyZlNhZmVNZXRob2Qoc2V0dGluZ3MudHlwZSkgJiYgIXRoaXMuY3Jvc3NEb21haW4pIHtcbiAgICAgICAgICAgICAgICB4aHIuc2V0UmVxdWVzdEhlYWRlcihcIlgtQ1NSRlRva2VuXCIsIGhlbHBlcnMuZ2V0Q29va2llKCdjc3JmdG9rZW4nKSk7XG4gICAgICAgICAgICB9XG4gICAgICAgIH1cbiAgICB9KTtcbn1cblxuLyoqXG4gKiBUaGlzIGZ1bmN0aW9uIGlzIGNhbGxlZCBpbiBzYWdlYnJldy5qcyBtYWluIGZpbGUuXG4gKiBFYWNoIGluaXQgdGFzayBzaG91bGQgYmUgZGVmaW5lZCBpbiBpdCdzIG93biBmdW5jdGlvbiBmb3Igd2hhdGV2ZXIgcmVhc29uLlxuICogLS0gQmV0dGVyIGNvZGUgcmVhZGFiaWxpdHk/XG4gKi9cbmV4cG9ydCBmdW5jdGlvbiBpbml0KCkge1xuICAgIGFqYXhTZXR1cCgpO1xufVxuXG5cblxuXG5cbiIsIi8qKlxuICogQGZpbGVcbiAqIFByaW1hcnkgSlMgZmlsZSB0aGF0IGlzIGxvYWRlZCBvbiBldmVyeSBwYWdlLlxuICogV0lQIEpTIFN0cmF0ZWd5LiBUaGlzIGlzIGEgV0lQIGFuZCBtYXkgb3IgbWF5IG5vdCBldmVuIHdvcmsuXG4gKlxuICogSlMgU2NvcGVzOlxuICogR2xvYmFsOiBKUyB0aGF0IGlzIGluY2x1ZGVkIG9uIGV2ZXJ5IHBhZ2UuXG4gKiBVc2VyOiBKUyB0aGF0IGlzIGluY2x1ZGVkIG9uIGV2ZXJ5IHBhZ2UsIGJ1dCBkZXBlbmRzIG9uIGlmIHRoZSB1c2VyIGlzIGF1dGggb3IgYW5vbi5cbiAqIFNlY3Rpb246IEpTIHRoYXQgaXMgb25seSBpbmNsdWRlZCBvbiBhIHNwZWNpZmljIHNlY3Rpb24gb2YgdGhlIHNpdGUuXG4gKlxuICogVGhpcyBmaWxlIGhhbmRsZXMgdGhlIGdsb2JhbCBzY29wZS5cbiAqXG4gKi9cblxudmFyIGluaXQgPSByZXF1aXJlKCcuL2NvbXBvbmVudHMvaW5pdCcpLmluaXQ7XG52YXIgdGVzdCA9IHJlcXVpcmUoJy4vY29tcG9uZW50cy9jb3JlJykudGVzdDtcblxuLy9cbi8vIGluaXQgcGFnZS5cbmluaXQoKTtcblxuY29uc29sZS5sb2codGVzdCgpKTtcblxuZXhwb3J0IGZ1bmN0aW9uIGFiY2QoKSB7XG4gICAgcmV0dXJuIHRlc3QoKTtcbn0iXX0=
