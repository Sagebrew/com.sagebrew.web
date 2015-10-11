require=(function e(t,n,r){function s(o,u){if(!n[o]){if(!t[o]){var a=typeof require=="function"&&require;if(!u&&a)return a(o,!0);if(i)return i(o,!0);var f=new Error("Cannot find module '"+o+"'");throw f.code="MODULE_NOT_FOUND",f}var l=n[o]={exports:{}};t[o][0].call(l.exports,function(e){var n=t[o][1][e];return s(n?n:e)},l,l.exports,e,t,n,r)}return n[o].exports}var i=typeof require=="function"&&require;for(var o=0;o<r.length;o++)s(r[o]);return s})({1:[function(require,module,exports){
/**
 * @file
 * blah blah?
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
exports.test = test;
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

/**
 * Ajax Setup
 * -- Automatically add CSRF cookie value to all ajax requests.
 */
$.ajaxSetup({
    beforeSend: function beforeSend(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        }
    }
});

function test() {
    console.log("asdfasdf");
    return 'asdfadf';
}

},{}],"sagebrew":[function(require,module,exports){
'use strict';

Object.defineProperty(exports, '__esModule', {
    value: true
});
exports.abcd = abcd;
var test = require('./components/core').test;

console.log(test());

function abcd() {
    return test();
}

},{"./components/core":1}]},{},["sagebrew"])
//# sourceMappingURL=data:application/json;charset:utf-8;base64,eyJ2ZXJzaW9uIjozLCJzb3VyY2VzIjpbIm5vZGVfbW9kdWxlcy9icm93c2VyaWZ5L25vZGVfbW9kdWxlcy9icm93c2VyLXBhY2svX3ByZWx1ZGUuanMiLCIvVXNlcnMvbXdpc25lci9Qcm9qZWN0cy9zYWdlYnJldy9jb20uc2FnZWJyZXcud2ViL3NhZ2VicmV3L3NhZ2VicmV3L3N0YXRpYy9qcy9zcmMvY29tcG9uZW50cy9jb3JlLmpzIiwiL1VzZXJzL213aXNuZXIvUHJvamVjdHMvc2FnZWJyZXcvY29tLnNhZ2VicmV3LndlYi9zYWdlYnJldy9zYWdlYnJldy9zdGF0aWMvanMvc3JjL3NhZ2VicmV3LmpzIl0sIm5hbWVzIjpbXSwibWFwcGluZ3MiOiJBQUFBOzs7Ozs7Ozs7Ozs7Ozs7OztBQ1VBLFNBQVMsU0FBUyxDQUFDLElBQUksRUFBRTtBQUNyQixRQUFJLFdBQVcsR0FBRyxJQUFJLENBQUM7QUFDdkIsUUFBSSxRQUFRLENBQUMsTUFBTSxJQUFJLFFBQVEsQ0FBQyxNQUFNLEtBQUssRUFBRSxFQUFFO0FBQzNDLFlBQUksT0FBTyxHQUFHLFFBQVEsQ0FBQyxNQUFNLENBQUMsS0FBSyxDQUFDLEdBQUcsQ0FBQyxDQUFDO0FBQ3pDLGFBQUssSUFBSSxDQUFDLEdBQUcsQ0FBQyxFQUFFLENBQUMsR0FBRyxPQUFPLENBQUMsTUFBTSxFQUFFLENBQUMsSUFBSSxDQUFDLEVBQUU7QUFDeEMsZ0JBQUksTUFBTSxHQUFHLENBQUMsQ0FBQyxJQUFJLENBQUMsT0FBTyxDQUFDLENBQUMsQ0FBQyxDQUFDLENBQUM7OztBQUdoQyxnQkFBSSxNQUFNLENBQUMsU0FBUyxDQUFDLENBQUMsRUFBRSxJQUFJLENBQUMsTUFBTSxHQUFHLENBQUMsQ0FBQyxLQUFNLElBQUksR0FBRyxHQUFHLEFBQUMsRUFBRTtBQUN2RCwyQkFBVyxHQUFHLGtCQUFrQixDQUFDLE1BQU0sQ0FBQyxTQUFTLENBQUMsSUFBSSxDQUFDLE1BQU0sR0FBRyxDQUFDLENBQUMsQ0FBQyxDQUFDO0FBQ3BFLHNCQUFNO2FBQ1Q7U0FDSjtLQUNKO0FBQ0QsV0FBTyxXQUFXLENBQUM7Q0FDdEI7Ozs7Ozs7QUFPRCxTQUFTLGNBQWMsQ0FBQyxNQUFNLEVBQUU7O0FBRTVCLFdBQVEsNkJBQTRCLENBQUMsSUFBSSxDQUFDLE1BQU0sQ0FBQztNQUFFO0NBQ3REOzs7Ozs7QUFNRCxDQUFDLENBQUMsU0FBUyxDQUFDO0FBQ1IsY0FBVSxFQUFFLG9CQUFVLEdBQUcsRUFBRSxRQUFRLEVBQUU7QUFDakMsWUFBSSxDQUFDLGNBQWMsQ0FBQyxRQUFRLENBQUMsSUFBSSxDQUFDLElBQUksQ0FBQyxJQUFJLENBQUMsV0FBVyxFQUFFO0FBQ3JELGVBQUcsQ0FBQyxnQkFBZ0IsQ0FBQyxhQUFhLEVBQUUsU0FBUyxDQUFDLFdBQVcsQ0FBQyxDQUFDLENBQUM7U0FDL0Q7S0FDSjtDQUNKLENBQUMsQ0FBQzs7QUFFSSxTQUFTLElBQUksR0FBRztBQUNuQixXQUFPLENBQUMsR0FBRyxDQUFDLFVBQVUsQ0FBQyxDQUFDO0FBQ3hCLFdBQU8sU0FBUyxDQUFDO0NBQ3BCOzs7Ozs7Ozs7QUNwREQsSUFBSSxJQUFJLEdBQUcsT0FBTyxDQUFDLG1CQUFtQixDQUFDLENBQUMsSUFBSSxDQUFDOztBQUU3QyxPQUFPLENBQUMsR0FBRyxDQUFDLElBQUksRUFBRSxDQUFDLENBQUM7O0FBRWIsU0FBUyxJQUFJLEdBQUc7QUFDbkIsV0FBTyxJQUFJLEVBQUUsQ0FBQztDQUNqQiIsImZpbGUiOiJnZW5lcmF0ZWQuanMiLCJzb3VyY2VSb290IjoiIiwic291cmNlc0NvbnRlbnQiOlsiKGZ1bmN0aW9uIGUodCxuLHIpe2Z1bmN0aW9uIHMobyx1KXtpZighbltvXSl7aWYoIXRbb10pe3ZhciBhPXR5cGVvZiByZXF1aXJlPT1cImZ1bmN0aW9uXCImJnJlcXVpcmU7aWYoIXUmJmEpcmV0dXJuIGEobywhMCk7aWYoaSlyZXR1cm4gaShvLCEwKTt2YXIgZj1uZXcgRXJyb3IoXCJDYW5ub3QgZmluZCBtb2R1bGUgJ1wiK28rXCInXCIpO3Rocm93IGYuY29kZT1cIk1PRFVMRV9OT1RfRk9VTkRcIixmfXZhciBsPW5bb109e2V4cG9ydHM6e319O3Rbb11bMF0uY2FsbChsLmV4cG9ydHMsZnVuY3Rpb24oZSl7dmFyIG49dFtvXVsxXVtlXTtyZXR1cm4gcyhuP246ZSl9LGwsbC5leHBvcnRzLGUsdCxuLHIpfXJldHVybiBuW29dLmV4cG9ydHN9dmFyIGk9dHlwZW9mIHJlcXVpcmU9PVwiZnVuY3Rpb25cIiYmcmVxdWlyZTtmb3IodmFyIG89MDtvPHIubGVuZ3RoO28rKylzKHJbb10pO3JldHVybiBzfSkiLCIvKipcbiAqIEBmaWxlXG4gKiBibGFoIGJsYWg/XG4gKi9cblxuLyoqXG4gKiBHZXQgY29va2llIGJhc2VkIGJ5IG5hbWUuXG4gKiBAcGFyYW0gbmFtZVxuICogQHJldHVybnMgeyp9XG4gKi9cbmZ1bmN0aW9uIGdldENvb2tpZShuYW1lKSB7XG4gICAgdmFyIGNvb2tpZVZhbHVlID0gbnVsbDtcbiAgICBpZiAoZG9jdW1lbnQuY29va2llICYmIGRvY3VtZW50LmNvb2tpZSAhPT0gXCJcIikge1xuICAgICAgICB2YXIgY29va2llcyA9IGRvY3VtZW50LmNvb2tpZS5zcGxpdCgnOycpO1xuICAgICAgICBmb3IgKHZhciBpID0gMDsgaSA8IGNvb2tpZXMubGVuZ3RoOyBpICs9IDEpIHtcbiAgICAgICAgICAgIHZhciBjb29raWUgPSAkLnRyaW0oY29va2llc1tpXSk7XG4gICAgICAgICAgICAvLyBEb2VzIHRoaXMgY29va2llIHN0cmluZyBiZWdpbiB3aXRoIHRoZSBuYW1lIHdlIHdhbnQ/XG5cbiAgICAgICAgICAgIGlmIChjb29raWUuc3Vic3RyaW5nKDAsIG5hbWUubGVuZ3RoICsgMSkgPT09IChuYW1lICsgJz0nKSkge1xuICAgICAgICAgICAgICAgIGNvb2tpZVZhbHVlID0gZGVjb2RlVVJJQ29tcG9uZW50KGNvb2tpZS5zdWJzdHJpbmcobmFtZS5sZW5ndGggKyAxKSk7XG4gICAgICAgICAgICAgICAgYnJlYWs7XG4gICAgICAgICAgICB9XG4gICAgICAgIH1cbiAgICB9XG4gICAgcmV0dXJuIGNvb2tpZVZhbHVlO1xufVxuXG4vKipcbiAqIENoZWNrIGlmIEhUVFAgbWV0aG9kIHJlcXVpcmVzIENTUkYuXG4gKiBAcGFyYW0gbWV0aG9kXG4gKiBAcmV0dXJucyB7Ym9vbGVhbn1cbiAqL1xuZnVuY3Rpb24gY3NyZlNhZmVNZXRob2QobWV0aG9kKSB7XG4gICAgLy8gdGhlc2UgSFRUUCBtZXRob2RzIGRvIG5vdCByZXF1aXJlIENTUkYgcHJvdGVjdGlvblxuICAgIHJldHVybiAoL14oR0VUfEhFQUR8T1BUSU9OU3xUUkFDRSkkLy50ZXN0KG1ldGhvZCkpO1xufVxuXG4vKipcbiAqIEFqYXggU2V0dXBcbiAqIC0tIEF1dG9tYXRpY2FsbHkgYWRkIENTUkYgY29va2llIHZhbHVlIHRvIGFsbCBhamF4IHJlcXVlc3RzLlxuICovXG4kLmFqYXhTZXR1cCh7XG4gICAgYmVmb3JlU2VuZDogZnVuY3Rpb24gKHhociwgc2V0dGluZ3MpIHtcbiAgICAgICAgaWYgKCFjc3JmU2FmZU1ldGhvZChzZXR0aW5ncy50eXBlKSAmJiAhdGhpcy5jcm9zc0RvbWFpbikge1xuICAgICAgICAgICAgeGhyLnNldFJlcXVlc3RIZWFkZXIoXCJYLUNTUkZUb2tlblwiLCBnZXRDb29raWUoJ2NzcmZ0b2tlbicpKTtcbiAgICAgICAgfVxuICAgIH1cbn0pO1xuXG5leHBvcnQgZnVuY3Rpb24gdGVzdCgpIHtcbiAgICBjb25zb2xlLmxvZyhcImFzZGZhc2RmXCIpO1xuICAgIHJldHVybiAnYXNkZmFkZic7XG59IiwidmFyIHRlc3QgPSByZXF1aXJlKCcuL2NvbXBvbmVudHMvY29yZScpLnRlc3Q7XG5cbmNvbnNvbGUubG9nKHRlc3QoKSk7XG5cbmV4cG9ydCBmdW5jdGlvbiBhYmNkKCkge1xuICAgIHJldHVybiB0ZXN0KCk7XG59Il19
