require=(function e(t,n,r){function s(o,u){if(!n[o]){if(!t[o]){var a=typeof require=="function"&&require;if(!u&&a)return a(o,!0);if(i)return i(o,!0);var f=new Error("Cannot find module '"+o+"'");throw f.code="MODULE_NOT_FOUND",f}var l=n[o]={exports:{}};t[o][0].call(l.exports,function(e){var n=t[o][1][e];return s(n?n:e)},l,l.exports,e,t,n,r)}return n[o].exports}var i=typeof require=="function"&&require;for(var o=0;o<r.length;o++)s(r[o]);return s})({1:[function(require,module,exports){
/**
 * @file
 * All the functionality for the navbar.
 * TODO: Reorganize.
 */
'use strict';

Object.defineProperty(exports, '__esModule', {
    value: true
});
exports.initNavbar = initNavbar;
var sagebrew = require('sagebrew');

/**
 *  Scope - User Authed
 *  All things relating to the navbar.
 */
function navbar() {
    $(document).ready(function () {
        //
        // Notifications
        // Retrieves all the notifications for a given user and gathers how
        // many have been seen or unseen.
        //Notification count in sidebar.
        sagebrew.request.get({ url: "/v1/me/notifications/render/" }).then(function (data) {
            $('#notification_wrapper').append(data.results.html);
            if (data.results.unseen > 0) {
                $('#js-notification_notifier_wrapper').append('<span class="navbar-new sb_notifier" id="js-sb_notifications_notifier">' + data.results.unseen + '</span>');
            }
        });

        // Shows the notifications when the notification icon is clicked
        $(".show_notifications-action").click(function () {
            $("#notification_div").fadeToggle();

            if ($('#js-notification_notifier_wrapper').children().length > 0) {
                sagebrew.request.get({ url: "/v1/me/notifications/?seen=true" }).then(function () {
                    $('#js-sb_notifications_notifier').remove();
                });
            }
        });

        //
        // Rep Was Viewed?
        $(".show-reputation-action").on("click", function () {
            sagebrew.request.put({
                url: "/v1/me/",
                data: JSON.stringify({
                    "reputation_update_seen": true
                })
            });
        });

        //
        // Show Rep
        sagebrew.request.get({ url: "/v1/profiles/" + $("#reputation_total").data('username') + "/reputation/" }).then(function (data) {
            $("#reputation_total").append("<p>" + data['reputation'] + "</p>");
        });

        //
        // Search
        $(".full_search-action").click(function (e) {
            var search_param = $('#sb_search_input').val();
            window.location.href = "/search/?q=" + search_param + "&page=1&filter=general";
        });
        $("#sb_search_input").keyup(function (e) {
            if (e.which === 10 || e.which === 13) {
                var search_param = $('#sb_search_input').val();
                window.location.href = "/search/?q=" + search_param + "&page=1&filter=general";
            }
        });

        //
        // Friends
        // Retrieves all the friend requests for a given user and gathers how
        // many have been seen or unseen.
        sagebrew.request.get({ url: "/v1/me/friend_requests/render/" }).then(function (data) {
            $('#friend_request_wrapper').append(data.results.html);
            if (data.results.unseen > 0) {
                $('#js-friend_request_notifier_wrapper').append('<span class="navbar-new sb_notifier" id="js-sb_friend_request_notifier">' + data.results.unseen + '</span>');
            }
        });

        // Shows the friend requests when the friend request icon is clicked
        $(".show_friend_request-action").click(function () {
            $("#friend_request_div").fadeToggle();
            if ($('#js-sb_friend_request_notifier').length > 0) {
                sagebrew.request.get({ url: "/v1/me/friend_requests/?seen=true" }).then(function () {
                    $('#js-sb_friend_request_notifier').remove();
                });
            }

            $(".respond_friend_request-accept-action").click(function (event) {
                event.preventDefault();
                var requestID = $(this).data('request_id');
                sagebrew.request.post({
                    url: "/v1/me/friend_requests/" + requestID + "/accept/",
                    data: JSON.stringify({
                        'request_id': requestID
                    })
                }).then(function () {
                    $('#friend_request_' + requestID).remove();
                });
            });

            $(".respond_friend_request-decline-action").click(function (event) {
                event.preventDefault();
                var requestID = $(this).data('request_id');
                sagebrew.request.post({
                    url: "/v1/me/friend_requests/" + requestID + "/decline/",
                    data: JSON.stringify({
                        'request_id': requestID
                    })
                }).then(function () {
                    $('#friend_request_' + requestID).remove();
                });
            });

            $(".respond_friend_request-block-action").click(function (event) {
                event.preventDefault();
                var requestID = $(this).data('request_id');
                sagebrew.request.post({
                    url: "/v1/me/friend_requests/" + requestID + "/block/",
                    data: JSON.stringify({
                        'request_id': requestID
                    })
                }).then(function () {
                    $('#friend_request_' + requestID).remove();
                });
            });
        });
    });
}

function initNavbar() {
    return navbar();
}

},{"sagebrew":"sagebrew"}],2:[function(require,module,exports){
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

},{"./helpers":2}],"user-anoned":[function(require,module,exports){
/**
 * @file
 * Used on every page with an anon user.
 */

'use strict';

var userAnonInit = require('./components/init').userAnonInit;
var loginform = require('./components/authed/navbar').initLoginForm;

//Init various things for anon user.
userAnonInit();
loginform();

},{"./components/authed/navbar":1,"./components/init":3}]},{},["user-anoned"])
//# sourceMappingURL=data:application/json;charset:utf-8;base64,eyJ2ZXJzaW9uIjozLCJzb3VyY2VzIjpbIm5vZGVfbW9kdWxlcy9icm93c2VyaWZ5L25vZGVfbW9kdWxlcy9icm93c2VyLXBhY2svX3ByZWx1ZGUuanMiLCIvVXNlcnMvbXdpc25lci9Qcm9qZWN0cy9zYWdlYnJldy9jb20uc2FnZWJyZXcud2ViL3NhZ2VicmV3L2Zyb250ZW5kL2pzL3NyYy9jb21wb25lbnRzL2F1dGhlZC9uYXZiYXIuanMiLCIvVXNlcnMvbXdpc25lci9Qcm9qZWN0cy9zYWdlYnJldy9jb20uc2FnZWJyZXcud2ViL3NhZ2VicmV3L2Zyb250ZW5kL2pzL3NyYy9jb21wb25lbnRzL2hlbHBlcnMuanMiLCIvVXNlcnMvbXdpc25lci9Qcm9qZWN0cy9zYWdlYnJldy9jb20uc2FnZWJyZXcud2ViL3NhZ2VicmV3L2Zyb250ZW5kL2pzL3NyYy9jb21wb25lbnRzL2luaXQuanMiLCIvVXNlcnMvbXdpc25lci9Qcm9qZWN0cy9zYWdlYnJldy9jb20uc2FnZWJyZXcud2ViL3NhZ2VicmV3L2Zyb250ZW5kL2pzL3NyYy91c2VyLWFub25lZC5qcyJdLCJuYW1lcyI6W10sIm1hcHBpbmdzIjoiQUFBQTs7Ozs7Ozs7Ozs7O0FDS0EsSUFBSSxRQUFRLEdBQUcsT0FBTyxDQUFDLFVBQVUsQ0FBQyxDQUFDOzs7Ozs7QUFNbkMsU0FBUyxNQUFNLEdBQUc7QUFDZCxLQUFDLENBQUMsUUFBUSxDQUFDLENBQUMsS0FBSyxDQUFDLFlBQVc7Ozs7OztBQU16QixnQkFBUSxDQUFDLE9BQU8sQ0FBQyxHQUFHLENBQUMsRUFBQyxHQUFHLEVBQUUsOEJBQThCLEVBQUMsQ0FBQyxDQUN0RCxJQUFJLENBQUMsVUFBUyxJQUFJLEVBQUM7QUFDaEIsYUFBQyxDQUFDLHVCQUF1QixDQUFDLENBQUMsTUFBTSxDQUFDLElBQUksQ0FBQyxPQUFPLENBQUMsSUFBSSxDQUFDLENBQUM7QUFDckQsZ0JBQUksSUFBSSxDQUFDLE9BQU8sQ0FBQyxNQUFNLEdBQUcsQ0FBQyxFQUFFO0FBQ3pCLGlCQUFDLENBQUMsbUNBQW1DLENBQUMs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R0FBRztBQUM3Qix3QkFBb0IsRUFBRSxDQUFDO0NBQzFCOzs7Ozs7QUFLTSxTQUFTLFlBQVksR0FBRyxFQUU5Qjs7Ozs7Ozs7OztBQ2pGRCxJQUFJLFlBQVksR0FBRyxPQUFPLENBQUMsbUJBQW1CLENBQUMsQ0FBQyxZQUFZLENBQUM7QUFDN0QsSUFBSSxTQUFTLEdBQUcsT0FBTyxDQUFDLDRCQUE0QixDQUFDLENBQUMsYUFBYSxDQUFDOzs7QUFHcEUsWUFBWSxFQUFFLENBQUM7QUFDZixTQUFTLEVBQUUsQ0FBQyIsImZpbGUiOiJnZW5lcmF0ZWQuanMiLCJzb3VyY2VSb290IjoiIiwic291cmNlc0NvbnRlbnQiOlsiKGZ1bmN0aW9uIGUodCxuLHIpe2Z1bmN0aW9uIHMobyx1KXtpZighbltvXSl7aWYoIXRbb10pe3ZhciBhPXR5cGVvZiByZXF1aXJlPT1cImZ1bmN0aW9uXCImJnJlcXVpcmU7aWYoIXUmJmEpcmV0dXJuIGEobywhMCk7aWYoaSlyZXR1cm4gaShvLCEwKTt2YXIgZj1uZXcgRXJyb3IoXCJDYW5ub3QgZmluZCBtb2R1bGUgJ1wiK28rXCInXCIpO3Rocm93IGYuY29kZT1cIk1PRFVMRV9OT1RfRk9VTkRcIixmfXZhciBsPW5bb109e2V4cG9ydHM6e319O3Rbb11bMF0uY2FsbChsLmV4cG9ydHMsZnVuY3Rpb24oZSl7dmFyIG49dFtvXVsxXVtlXTtyZXR1cm4gcyhuP246ZSl9LGwsbC5leHBvcnRzLGUsdCxuLHIpfXJldHVybiBuW29dLmV4cG9ydHN9dmFyIGk9dHlwZW9mIHJlcXVpcmU9PVwiZnVuY3Rpb25cIiYmcmVxdWlyZTtmb3IodmFyIG89MDtvPHIubGVuZ3RoO28rKylzKHJbb10pO3JldHVybiBzfSkiLCIvKipcbiAqIEBmaWxlXG4gKiBBbGwgdGhlIGZ1bmN0aW9uYWxpdHkgZm9yIHRoZSBuYXZiYXIuXG4gKiBUT0RPOiBSZW9yZ2FuaXplLlxuICovXG52YXIgc2FnZWJyZXcgPSByZXF1aXJlKCdzYWdlYnJldycpO1xuXG4vKipcbiAqICBTY29wZSAtIFVzZXIgQXV0aGVkXG4gKiAgQWxsIHRoaW5ncyByZWxhdGluZyB0byB0aGUgbmF2YmFyLlxuICovXG5mdW5jdGlvbiBuYXZiYXIoKSB7XG4gICAgJChkb2N1bWVudCkucmVhZHkoZnVuY3Rpb24oKSB7XG4gICAgICAgIC8vXG4gICAgICAgIC8vIE5vdGlmaWNhdGlvbnNcbiAgICAgICAgLy8gUmV0cmlldmVzIGFsbCB0aGUgbm90aWZpY2F0aW9ucyBmb3IgYSBnaXZlbiB1c2VyIGFuZCBnYXRoZXJzIGhvd1xuICAgICAgICAvLyBtYW55IGhhdmUgYmVlbiBzZWVuIG9yIHVuc2Vlbi5cbiAgICAgICAgLy9Ob3RpZmljYXRpb24gY291bnQgaW4gc2lkZWJhci5cbiAgICAgICAgc2FnZWJyZXcucmVxdWVzdC5nZXQoe3VybDogXCIvdjEvbWUvbm90aWZpY2F0aW9ucy9yZW5kZXIvXCJ9KVxuICAgICAgICAgICAgLnRoZW4oZnVuY3Rpb24oZGF0YSl7XG4gICAgICAgICAgICAgICAgJCgnI25vdGlmaWNhdGlvbl93cmFwcGVyJykuYXBwZW5kKGRhdGEucmVzdWx0cy5odG1sKTtcbiAgICAgICAgICAgICAgICBpZiAoZGF0YS5yZXN1bHRzLnVuc2VlbiA+IDApIHtcbiAgICAgICAgICAgICAgICAgICAgJCgnI2pzLW5vdGlmaWNhdGlvbl9ub3RpZmllcl93cmFwcGVyJykuYXBwZW5kKCc8c3BhbiBjbGFzcz1cIm5hdmJhci1uZXcgc2Jfbm90aWZpZXJcIiBpZD1cImpzLXNiX25vdGlmaWNhdGlvbnNfbm90aWZpZXJcIj4nICsgZGF0YS5yZXN1bHRzLnVuc2VlbiArICc8L3NwYW4+Jyk7XG4gICAgICAgICAgICAgICAgfVxuICAgICAgICB9KTtcblxuICAgICAgICAvLyBTaG93cyB0aGUgbm90aWZpY2F0aW9ucyB3aGVuIHRoZSBub3RpZmljYXRpb24gaWNvbiBpcyBjbGlja2VkXG4gICAgICAgICQoXCIuc2hvd19ub3RpZmljYXRpb25zLWFjdGlvblwiKS5jbGljayhmdW5jdGlvbiAoKSB7XG4gICAgICAgICAgICAkKFwiI25vdGlmaWNhdGlvbl9kaXZcIikuZmFkZVRvZ2dsZSgpO1xuXG4gICAgICAgICAgICBpZiAoJCgnI2pzLW5vdGlmaWNhdGlvbl9ub3RpZmllcl93cmFwcGVyJykuY2hpbGRyZW4oKS5sZW5ndGggPiAwKSB7XG4gICAgICAgICAgICAgICAgc2FnZWJyZXcucmVxdWVzdC5nZXQoe3VybDogIFwiL3YxL21lL25vdGlmaWNhdGlvbnMvP3NlZW49dHJ1ZVwifSlcbiAgICAgICAgICAgICAgICAgICAgLnRoZW4oZnVuY3Rpb24oKSB7XG4gICAgICAgICAgICAgICAgICAgICAgICAkKCcjanMtc2Jfbm90aWZpY2F0aW9uc19ub3RpZmllcicpLnJlbW92ZSgpO1xuICAgICAgICAgICAgICAgIH0pO1xuICAgICAgICAgICAgfVxuXG4gICAgICAgIH0pO1xuXG4gICAgICAgIC8vXG4gICAgICAgIC8vIFJlcCBXYXMgVmlld2VkP1xuICAgICAgICAkKFwiLnNob3ctcmVwdXRhdGlvbi1hY3Rpb25cIikub24oXCJjbGlja1wiLCBmdW5jdGlvbiAoKSB7XG4gICAgICAgICAgICBzYWdlYnJldy5yZXF1ZXN0LnB1dCh7XG4gICAgICAgICAgICAgICAgdXJsOiBcIi92MS9tZS9cIixcbiAgICAgICAgICAgICAgICBkYXRhOiBKU09OLnN0cmluZ2lmeSh7XG4gICAgICAgICAgICAgICAgICAgIFwicmVwdXRhdGlvbl91cGRhdGVfc2VlblwiOiB0cnVlXG4gICAgICAgICAgICAgICAgfSlcbiAgICAgICAgICAgIH0pO1xuICAgICAgICB9KTtcblxuICAgICAgICAvL1xuICAgICAgICAvLyBTaG93IFJlcFxuICAgICAgICBzYWdlYnJldy5yZXF1ZXN0LmdldCh7dXJsOiBcIi92MS9wcm9maWxlcy9cIiArICQoXCIjcmVwdXRhdGlvbl90b3RhbFwiKS5kYXRhKCd1c2VybmFtZScpICsgXCIvcmVwdXRhdGlvbi9cIn0pXG4gICAgICAgICAgICAudGhlbihmdW5jdGlvbihkYXRhKSB7XG4gICAgICAgICAgICAgICAgJChcIiNyZXB1dGF0aW9uX3RvdGFsXCIpLmFwcGVuZChcIjxwPlwiICsgZGF0YVsncmVwdXRhdGlvbiddICsgXCI8L3A+XCIpO1xuICAgICAgICB9KTtcblxuXG4gICAgICAgIC8vXG4gICAgICAgIC8vIFNlYXJjaFxuICAgICAgICAkKFwiLmZ1bGxfc2VhcmNoLWFjdGlvblwiKS5jbGljayhmdW5jdGlvbihlKSB7XG4gICAgICAgICAgICB2YXIgc2VhcmNoX3BhcmFtID0gKCQoJyNzYl9zZWFyY2hfaW5wdXQnKS52YWwoKSk7XG4gICAgICAgICAgICB3aW5kb3cubG9jYXRpb24uaHJlZiA9IFwiL3NlYXJjaC8/cT1cIiArIHNlYXJjaF9wYXJhbSArIFwiJnBhZ2U9MSZmaWx0ZXI9Z2VuZXJhbFwiO1xuICAgICAgICB9KTtcbiAgICAgICAgJChcIiNzYl9zZWFyY2hfaW5wdXRcIikua2V5dXAoZnVuY3Rpb24oZSkge1xuICAgICAgICAgICAgaWYoZS53aGljaCA9PT0gMTAgfHwgZS53aGljaCA9PT0gMTMpIHtcbiAgICAgICAgICAgICAgICB2YXIgc2VhcmNoX3BhcmFtID0gKCQoJyNzYl9zZWFyY2hfaW5wdXQnKS52YWwoKSk7XG4gICAgICAgICAgICAgICAgd2luZG93LmxvY2F0aW9uLmhyZWYgPSBcIi9zZWFyY2gvP3E9XCIgKyBzZWFyY2hfcGFyYW0gKyBcIiZwYWdlPTEmZmlsdGVyPWdlbmVyYWxcIjtcbiAgICAgICAgICAgIH1cbiAgICAgICAgfSk7XG5cbiAgICAgICAgLy9cbiAgICAgICAgLy8gRnJpZW5kc1xuICAgICAgICAvLyBSZXRyaWV2ZXMgYWxsIHRoZSBmcmllbmQgcmVxdWVzdHMgZm9yIGEgZ2l2ZW4gdXNlciBhbmQgZ2F0aGVycyBob3dcbiAgICAgICAgLy8gbWFueSBoYXZlIGJlZW4gc2VlbiBvciB1bnNlZW4uXG4gICAgICAgIHNhZ2VicmV3LnJlcXVlc3QuZ2V0KHt1cmw6IFwiL3YxL21lL2ZyaWVuZF9yZXF1ZXN0cy9yZW5kZXIvXCJ9KVxuICAgICAgICAgICAgLnRoZW4oZnVuY3Rpb24oZGF0YSkge1xuICAgICAgICAgICAgICAgICQoJyNmcmllbmRfcmVxdWVzdF93cmFwcGVyJykuYXBwZW5kKGRhdGEucmVzdWx0cy5odG1sKTtcbiAgICAgICAgICAgICAgICBpZiAoZGF0YS5yZXN1bHRzLnVuc2VlbiA+IDApIHtcbiAgICAgICAgICAgICAgICAgICAgJCgnI2pzLWZyaWVuZF9yZXF1ZXN0X25vdGlmaWVyX3dyYXBwZXInKS5hcHBlbmQoJzxzcGFuIGNsYXNzPVwibmF2YmFyLW5ldyBzYl9ub3RpZmllclwiIGlkPVwianMtc2JfZnJpZW5kX3JlcXVlc3Rfbm90aWZpZXJcIj4nICsgZGF0YS5yZXN1bHRzLnVuc2VlbiArICc8L3NwYW4+Jyk7XG4gICAgICAgICAgICAgICAgfVxuICAgICAgICAgICAgfSk7XG5cbiAgICAgICAgLy8gU2hvd3MgdGhlIGZyaWVuZCByZXF1ZXN0cyB3aGVuIHRoZSBmcmllbmQgcmVxdWVzdCBpY29uIGlzIGNsaWNrZWRcbiAgICAgICAgJChcIi5zaG93X2ZyaWVuZF9yZXF1ZXN0LWFjdGlvblwiKS5jbGljayhmdW5jdGlvbiAoKSB7XG4gICAgICAgICAgICAkKFwiI2ZyaWVuZF9yZXF1ZXN0X2RpdlwiKS5mYWRlVG9nZ2xlKCk7XG4gICAgICAgICAgICBpZiAoJCgnI2pzLXNiX2ZyaWVuZF9yZXF1ZXN0X25vdGlmaWVyJykubGVuZ3RoID4gMCkge1xuICAgICAgICAgICAgICAgIHNhZ2VicmV3LnJlcXVlc3QuZ2V0KHt1cmw6IFwiL3YxL21lL2ZyaWVuZF9yZXF1ZXN0cy8/c2Vlbj10cnVlXCJ9KVxuICAgICAgICAgICAgICAgIC50aGVuKGZ1bmN0aW9uKCkge1xuICAgICAgICAgICAgICAgICAgICAgJCgnI2pzLXNiX2ZyaWVuZF9yZXF1ZXN0X25vdGlmaWVyJykucmVtb3ZlKCk7XG4gICAgICAgICAgICAgICAgfSk7XG4gICAgICAgICAgICB9XG5cbiAgICAgICAgICAgICQoXCIucmVzcG9uZF9mcmllbmRfcmVxdWVzdC1hY2NlcHQtYWN0aW9uXCIpLmNsaWNrKGZ1bmN0aW9uIChldmVudCkge1xuICAgICAgICAgICAgICAgIGV2ZW50LnByZXZlbnREZWZhdWx0KCk7XG4gICAgICAgICAgICAgICAgdmFyIHJlcXVlc3RJRCA9ICQodGhpcykuZGF0YSgncmVxdWVzdF9pZCcpO1xuICAgICAgICAgICAgICAgIHNhZ2VicmV3LnJlcXVlc3QucG9zdCh7XG4gICAgICAgICAgICAgICAgICAgIHVybDogXCIvdjEvbWUvZnJpZW5kX3JlcXVlc3RzL1wiICsgcmVxdWVzdElEICsgXCIvYWNjZXB0L1wiLFxuICAgICAgICAgICAgICAgICAgICBkYXRhOiBKU09OLnN0cmluZ2lmeSh7XG4gICAgICAgICAgICAgICAgICAgICAgICAncmVxdWVzdF9pZCc6IHJlcXVlc3RJRFxuICAgICAgICAgICAgICAgICAgICB9KVxuICAgICAgICAgICAgICAgIH0pLnRoZW4oZnVuY3Rpb24oKSB7XG4gICAgICAgICAgICAgICAgICAgICQoJyNmcmllbmRfcmVxdWVzdF8nICsgcmVxdWVzdElEKS5yZW1vdmUoKTtcbiAgICAgICAgICAgICAgICB9KTtcbiAgICAgICAgICAgIH0pO1xuXG4gICAgICAgICAgICAkKFwiLnJlc3BvbmRfZnJpZW5kX3JlcXVlc3QtZGVjbGluZS1hY3Rpb25cIikuY2xpY2soZnVuY3Rpb24gKGV2ZW50KSB7XG4gICAgICAgICAgICAgICAgZXZlbnQucHJldmVudERlZmF1bHQoKTtcbiAgICAgICAgICAgICAgICB2YXIgcmVxdWVzdElEID0gJCh0aGlzKS5kYXRhKCdyZXF1ZXN0X2lkJyk7XG4gICAgICAgICAgICAgICAgc2FnZWJyZXcucmVxdWVzdC5wb3N0KHtcbiAgICAgICAgICAgICAgICAgICAgdXJsOiBcIi92MS9tZS9mcmllbmRfcmVxdWVzdHMvXCIgKyByZXF1ZXN0SUQgKyBcIi9kZWNsaW5lL1wiLFxuICAgICAgICAgICAgICAgICAgICBkYXRhOiBKU09OLnN0cmluZ2lmeSh7XG4gICAgICAgICAgICAgICAgICAgICAgICAncmVxdWVzdF9pZCc6IHJlcXVlc3RJRFxuICAgICAgICAgICAgICAgICAgICB9KVxuICAgICAgICAgICAgICAgIH0pLnRoZW4oZnVuY3Rpb24oKSB7XG4gICAgICAgICAgICAgICAgICAgICQoJyNmcmllbmRfcmVxdWVzdF8nICsgcmVxdWVzdElEKS5yZW1vdmUoKTtcbiAgICAgICAgICAgICAgICB9KTtcbiAgICAgICAgICAgIH0pO1xuXG4gICAgICAgICAgICAkKFwiLnJlc3BvbmRfZnJpZW5kX3JlcXVlc3QtYmxvY2stYWN0aW9uXCIpLmNsaWNrKGZ1bmN0aW9uIChldmVudCkge1xuICAgICAgICAgICAgICAgIGV2ZW50LnByZXZlbnREZWZhdWx0KCk7XG4gICAgICAgICAgICAgICAgdmFyIHJlcXVlc3RJRCA9ICQodGhpcykuZGF0YSgncmVxdWVzdF9pZCcpO1xuICAgICAgICAgICAgICAgIHNhZ2VicmV3LnJlcXVlc3QucG9zdCh7XG4gICAgICAgICAgICAgICAgICAgIHVybDogXCIvdjEvbWUvZnJpZW5kX3JlcXVlc3RzL1wiICsgcmVxdWVzdElEICsgXCIvYmxvY2svXCIsXG4gICAgICAgICAgICAgICAgICAgIGRhdGE6IEpTT04uc3RyaW5naWZ5KHtcbiAgICAgICAgICAgICAgICAgICAgICAgICdyZXF1ZXN0X2lkJzogcmVxdWVzdElEXG4gICAgICAgICAgICAgICAgICAgIH0pXG4gICAgICAgICAgICAgICAgfSkudGhlbihmdW5jdGlvbigpIHtcbiAgICAgICAgICAgICAgICAgICAgJCgnI2ZyaWVuZF9yZXF1ZXN0XycgKyByZXF1ZXN0SUQpLnJlbW92ZSgpO1xuICAgICAgICAgICAgICAgIH0pO1xuICAgICAgICAgICAgfSk7XG5cbiAgICAgICAgfSk7XG4gICAgfSk7XG59XG5cbmV4cG9ydCBmdW5jdGlvbiBpbml0TmF2YmFyKCkge1xuICAgIHJldHVybiBuYXZiYXIoKTtcbn0iLCIvKipcbiAqIEBmaWxlXG4gKiBIZWxwZXIgZnVuY3Rpb25zIHRoYXQgYXJlbid0IGdsb2JhbC5cbiAqL1xuXG4vKipcbiAqIEdldCBjb29raWUgYmFzZWQgYnkgbmFtZS5cbiAqIEBwYXJhbSBuYW1lXG4gKiBAcmV0dXJucyB7Kn1cbiAqL1xuZXhwb3J0IGZ1bmN0aW9uIGdldENvb2tpZShuYW1lKSB7XG4gICAgdmFyIGNvb2tpZVZhbHVlID0gbnVsbDtcbiAgICBpZiAoZG9jdW1lbnQuY29va2llICYmIGRvY3VtZW50LmNvb2tpZSAhPT0gXCJcIikge1xuICAgICAgICB2YXIgY29va2llcyA9IGRvY3VtZW50LmNvb2tpZS5zcGxpdCgnOycpO1xuICAgICAgICBmb3IgKHZhciBpID0gMDsgaSA8IGNvb2tpZXMubGVuZ3RoOyBpICs9IDEpIHtcbiAgICAgICAgICAgIHZhciBjb29raWUgPSAkLnRyaW0oY29va2llc1tpXSk7XG4gICAgICAgICAgICAvLyBEb2VzIHRoaXMgY29va2llIHN0cmluZyBiZWdpbiB3aXRoIHRoZSBuYW1lIHdlIHdhbnQ/XG5cbiAgICAgICAgICAgIGlmIChjb29raWUuc3Vic3RyaW5nKDAsIG5hbWUubGVuZ3RoICsgMSkgPT09IChuYW1lICsgJz0nKSkge1xuICAgICAgICAgICAgICAgIGNvb2tpZVZhbHVlID0gZGVjb2RlVVJJQ29tcG9uZW50KGNvb2tpZS5zdWJzdHJpbmcobmFtZS5sZW5ndGggKyAxKSk7XG4gICAgICAgICAgICAgICAgYnJlYWs7XG4gICAgICAgICAgICB9XG4gICAgICAgIH1cbiAgICB9XG4gICAgcmV0dXJuIGNvb2tpZVZhbHVlO1xufVxuXG4vKipcbiAqIENoZWNrIGlmIEhUVFAgbWV0aG9kIHJlcXVpcmVzIENTUkYuXG4gKiBAcGFyYW0gbWV0aG9kXG4gKiBAcmV0dXJucyB7Ym9vbGVhbn1cbiAqL1xuZXhwb3J0IGZ1bmN0aW9uIGNzcmZTYWZlTWV0aG9kKG1ldGhvZCkge1xuICAgIC8vIHRoZXNlIEhUVFAgbWV0aG9kcyBkbyBub3QgcmVxdWlyZSBDU1JGIHByb3RlY3Rpb25cbiAgICByZXR1cm4gKC9eKEdFVHxIRUFEfE9QVElPTlN8VFJBQ0UpJC8udGVzdChtZXRob2QpKTtcbn0iLCIvKipcbiAqIEBmaWxlXG4gKiBJbml0IHRoZSBTQiB3ZWJzaXRlLlxuICogZ2xvYmFsSW5pdCAtIFJ1bnMgb24gYWxsIHBhZ2VzLlxuICogVXNlckF1dGhlZEluaXQgLSBSdW5zIG9uIGF1dGhlZCBwYWdlcy5cbiAqIHVzZXJBbm9uSW5pdCAtIFJ1bnMgb24gYW5vbiBwYWdlcy5cbiAqIFRPRE86IFRoZSBpbmRpdmlkdWFsIGluaXQgZnVuY3Rpb25zIGNvdWxkIGJlIHR1cm5lZCBpbnRvIGFycmF5cyBvciBvYmplY3RzIGFuZCB0aGVuXG4gKiBsb29wZWQgb3Zlci5cbiAqL1xudmFyIGhlbHBlcnMgPSByZXF1aXJlKCcuL2hlbHBlcnMnKTtcblxuLyoqXG4gKiBTY29wZSAtIEdsb2JhbFxuICogQWpheCBTZXR1cFxuICogLS0gQXV0b21hdGljYWxseSBhZGQgQ1NSRiBjb29raWUgdmFsdWUgdG8gYWxsIGFqYXggcmVxdWVzdHMuXG4gKi9cbmZ1bmN0aW9uIGFqYXhTZXR1cCgpIHtcbiAgICAkLmFqYXhTZXR1cCh7XG4gICAgICAgIGJlZm9yZVNlbmQ6IGZ1bmN0aW9uICh4aHIsIHNldHRpbmdzKSB7XG4gICAgICAgICAgICBpZiAoIWhlbHBlcnMuY3NyZlNhZmVNZXRob2Qoc2V0dGluZ3MudHlwZSkgJiYgIXRoaXMuY3Jvc3NEb21haW4pIHtcbiAgICAgICAgICAgICAgICB4aHIuc2V0UmVxdWVzdEhlYWRlcihcIlgtQ1NSRlRva2VuXCIsIGhlbHBlcnMuZ2V0Q29va2llKCdjc3JmdG9rZW4nKSk7XG4gICAgICAgICAgICB9XG4gICAgICAgIH1cbiAgICB9KTtcbn1cblxuLyoqXG4gKiAgU2NvcGUgLSBVc2VyIEF1dGhlZFxuICogIEFkZHMgYW4gZXZlbnQgaGFuZGxlciB0byBwYWdlIHVubG9hZCB0aGF0IGFqYXggcG9zdHMgYWxsIHRoZSB1c2VyJ3MgYWN0aW9ucyB0aGF0IG9jY3VyZWQgZHVyaW5nIHRoZSBwYWdlLlxuICogIFRPRE86IFN0b3AgZG9pbmcgdGhpcy5cbiAqICBOb3Qgb25seSBhcmUgbm9uLWFzeW5jIGFqYXggY2FsbHMgZGVwcmVjYXRlZCBpdCBob2xkcyB0aGUgcGFnZSBsb2FkIHVwIGZvciB0aGUgdXNlci5cbiAqICBUaGV5IGNhbid0IGV2ZW4gc3RhcnQgbG9hZGluZyB0aGUgbmV4dCBwYWdlIHVudGlsIHRoaXMgaXMgY29tcGxldGVkLlxuICovXG5mdW5jdGlvbiBjb2xsZWN0QXV0aGVkQWN0aW9ucygpIHtcbiAgICAkKGRvY3VtZW50KS5yZWFkeShmdW5jdGlvbiAoKSB7XG4gICAgICAgIFwidXNlIHN0cmljdFwiO1xuICAgICAgICB3aW5kb3cub25iZWZvcmV1bmxvYWQgPSBmdW5jdGlvbiAoKSB7XG4gICAgICAgICAgICB2YXIgb2JqZWN0TGlzdCA9IFtdO1xuICAgICAgICAgICAgJChcIi5qcy1wYWdlLW9iamVjdFwiKS5lYWNoKGZ1bmN0aW9uICgpIHtcbiAgICAgICAgICAgICAgICBvYmplY3RMaXN0LnB1c2goJCh0aGlzKS5kYXRhKCdvYmplY3RfdXVpZCcpKTtcbiAgICAgICAgICAgIH0pO1xuICAgICAgICAgICAgaWYgKG9iamVjdExpc3QubGVuZ3RoKSB7XG4gICAgICAgICAgICAgICAgJC5hamF4KHtcbiAgICAgICAgICAgICAgICAgICAgeGhyRmllbGRzOiB7d2l0aENyZWRlbnRpYWxzOiB0cnVlfSxcbiAgICAgICAgICAgICAgICAgICAgdHlwZTogXCJQT1NUXCIsXG4gICAgICAgICAgICAgICAgICAgIGFzeW5jOiBmYWxzZSxcbiAgICAgICAgICAgICAgICAgICAgdXJsOiBcIi9kb2NzdG9yZS91cGRhdGVfbmVvX2FwaS9cIixcbiAgICAgICAgICAgICAgICAgICAgZGF0YTogSlNPTi5zdHJpbmdpZnkoe1xuICAgICAgICAgICAgICAgICAgICAgICAgJ29iamVjdF91dWlkcyc6IG9iamVjdExpc3RcbiAgICAgICAgICAgICAgICAgICAgfSksXG4gICAgICAgICAgICAgICAgICAgIGNvbnRlbnRUeXBlOiBcImFwcGxpY2F0aW9uL2pzb247IGNoYXJzZXQ9dXRmLThcIixcbiAgICAgICAgICAgICAgICAgICAgZGF0YVR5cGU6IFwianNvblwiLFxuICAgICAgICAgICAgICAgICAgICBlcnJvcjogZnVuY3Rpb24gKFhNTEh0dHBSZXF1ZXN0KSB7XG4gICAgICAgICAgICAgICAgICAgICAgICBpZiAoWE1MSHR0cFJlcXVlc3Quc3RhdHVzID09PSA1MDApIHtcbiAgICAgICAgICAgICAgICAgICAgICAgICAgICAkKFwiI3NlcnZlcl9lcnJvclwiKS5zaG93KCk7XG4gICAgICAgICAgICAgICAgICAgICAgICB9XG4gICAgICAgICAgICAgICAgICAgIH1cbiAgICAgICAgICAgICAgICB9KTtcbiAgICAgICAgICAgIH1cbiAgICAgICAgfTtcbiAgICB9KTtcbn1cblxuXG5cbi8qKlxuICogVGhpcyBmdW5jdGlvbiBpcyBjYWxsZWQgaW4gc2FnZWJyZXcuanMgbWFpbiBmaWxlLlxuICogRWFjaCBpbml0IHRhc2sgc2hvdWxkIGJlIGRlZmluZWQgaW4gaXQncyBvd24gZnVuY3Rpb24gZm9yIHdoYXRldmVyIHJlYXNvbi5cbiAqIC0tIEJldHRlciBjb2RlIHJlYWRhYmlsaXR5P1xuICovXG5leHBvcnQgZnVuY3Rpb24gZ2xvYmFsSW5pdCgpIHtcbiAgICBhamF4U2V0dXAoKTtcbn1cblxuLyoqXG4gKiBBdXRoIEluaXQuXG4gKi9cbmV4cG9ydCBmdW5jdGlvbiB1c2VyQXV0aGVkSW5pdCgpIHtcbiAgICBjb2xsZWN0QXV0aGVkQWN0aW9ucygpO1xufVxuXG4vKipcbiAqIEFub24gSW5pdC5cbiAqL1xuZXhwb3J0IGZ1bmN0aW9uIHVzZXJBbm9uSW5pdCgpIHtcblxufVxuXG5cblxuXG4iLCIvKipcbiAqIEBmaWxlXG4gKiBVc2VkIG9uIGV2ZXJ5IHBhZ2Ugd2l0aCBhbiBhbm9uIHVzZXIuXG4gKi9cblxudmFyIHVzZXJBbm9uSW5pdCA9IHJlcXVpcmUoJy4vY29tcG9uZW50cy9pbml0JykudXNlckFub25Jbml0O1xudmFyIGxvZ2luZm9ybSA9IHJlcXVpcmUoJy4vY29tcG9uZW50cy9hdXRoZWQvbmF2YmFyJykuaW5pdExvZ2luRm9ybTtcblxuLy9Jbml0IHZhcmlvdXMgdGhpbmdzIGZvciBhbm9uIHVzZXIuXG51c2VyQW5vbkluaXQoKTtcbmxvZ2luZm9ybSgpO1xuXG5cbiJdfQ==
