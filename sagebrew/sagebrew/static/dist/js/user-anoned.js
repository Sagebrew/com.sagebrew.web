require=(function e(t,n,r){function s(o,u){if(!n[o]){if(!t[o]){var a=typeof require=="function"&&require;if(!u&&a)return a(o,!0);if(i)return i(o,!0);var f=new Error("Cannot find module '"+o+"'");throw f.code="MODULE_NOT_FOUND",f}var l=n[o]={exports:{}};t[o][0].call(l.exports,function(e){var n=t[o][1][e];return s(n?n:e)},l,l.exports,e,t,n,r)}return n[o].exports}var i=typeof require=="function"&&require;for(var o=0;o<r.length;o++)s(r[o]);return s})({1:[function(require,module,exports){
/**
 * @file
 * All the functionality for the navbar.
 * TODO: Reorganize.
 */
"use strict";

Object.defineProperty(exports, "__esModule", {
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
        console.log("Navbar Start");

        sagebrew.resource.get({ url: "/v1/me/notifications/render/" }).then(function (data) {
            $('#notification_wrapper').append(data.results.html);
            if (data.results.unseen > 0) {
                $('#js-notification_notifier_wrapper').append('<span class="navbar-new sb_notifier" id="js-sb_notifications_notifier">' + data.results.unseen + '</span>');
            }
        });

        // Shows the notifications when the notification icon is clicked
        $(".show_notifications-action").click(function () {
            $("#notification_div").fadeToggle();
            if ($('#js-notification_notifier_wrapper').children().length > 0) {
                $.ajax({
                    xhrFields: { withCredentials: true },
                    type: "GET",
                    url: "/v1/me/notifications/?seen=true",
                    contentType: "application/json; charset=utf-8",
                    dataType: "json",
                    success: function success() {
                        $('#js-sb_notifications_notifier').remove();
                    },
                    error: function error(XMLHttpRequest) {
                        errorDisplay(XMLHttpRequest);
                    }
                });
            }
        });

        //
        // Rep Was Viewed?
        $(".show-reputation-action").on("click", function () {
            $.ajax({
                xhrFields: { withCredentials: true },
                type: "PUT",
                url: "/v1/me/",
                contentType: "application/json; charset=utf-8",
                dataType: "json",
                data: JSON.stringify({
                    "reputation_update_seen": true
                })
            });
        });

        //
        // Show Rep
        $.ajax({
            xhrFields: { withCredentials: true },
            type: "GET",
            url: "/v1/profiles/" + $("#reputation_total").data('username') + "/reputation/",
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function success(data) {
                $("#reputation_total").append("<p>" + data["reputation"] + "</p>");
            },
            error: function error(XMLHttpRequest, textStatus, errorThrown) {
                if (XMLHttpRequest.status === 500) {
                    $("#server_error").show();
                }
            }
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
        //

        //
        // Friends
        // Retrieves all the friend requests for a given user and gathers how
        // many have been seen or unseen.
        $.ajax({
            xhrFields: { withCredentials: true },
            type: "GET",
            url: "/v1/me/friend_requests/render/",
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function success(data) {
                $('#friend_request_wrapper').append(data.results.html);
                if (data.results.unseen > 0) {
                    $('#js-friend_request_notifier_wrapper').append('<span class="navbar-new sb_notifier" id="js-sb_friend_request_notifier">' + data.results.unseen + '</span>');
                }
            },
            error: function error(XMLHttpRequest) {
                if (XMLHttpRequest.status === 500) {
                    $("#server_error").show();
                }
            }
        });

        // Shows the friend requests when the friend request icon is clicked
        $(".show_friend_request-action").click(function () {
            $("#friend_request_div").fadeToggle();
            if ($('#js-sb_friend_request_notifier').length > 0) {
                $.ajax({
                    xhrFields: { withCredentials: true },
                    type: "GET",
                    url: "/v1/me/friend_requests/?seen=true",
                    contentType: "application/json; charset=utf-8",
                    dataType: "json",
                    success: function success() {
                        $('#js-sb_friend_request_notifier').remove();
                    },
                    error: function error() {
                        $("#server_error").show();
                    }
                });
            }
            $(".respond_friend_request-accept-action").click(function (event) {
                event.preventDefault();
                var requestID = $(this).data('request_id');
                $.ajax({
                    xhrFields: { withCredentials: true },
                    type: "POST",
                    url: "/v1/me/friend_requests/" + requestID + "/accept/",
                    data: JSON.stringify({
                        'request_id': requestID
                    }),
                    contentType: "application/json; charset=utf-8",
                    dataType: "json",
                    success: function success() {
                        $('#friend_request_' + requestID).remove();
                    },
                    error: function error(XMLHttpRequest) {
                        if (XMLHttpRequest.status === 500) {
                            $("#server_error").show();
                        }
                    }
                });
            });
            $(".respond_friend_request-decline-action").click(function (event) {
                event.preventDefault();
                var requestID = $(this).data('request_id');
                $.ajax({
                    xhrFields: { withCredentials: true },
                    type: "POST",
                    url: "/v1/me/friend_requests/" + requestID + "/decline/",
                    data: JSON.stringify({
                        'request_id': requestID
                    }),
                    contentType: "application/json; charset=utf-8",
                    dataType: "json",
                    success: function success() {
                        $('#friend_request_' + requestID).remove();
                    },
                    error: function error(XMLHttpRequest) {
                        if (XMLHttpRequest.status === 500) {
                            $("#server_error").show();
                        }
                    }
                });
            });
            $(".respond_friend_request-block-action").click(function (event) {
                event.preventDefault();
                var requestID = $(this).data('request_id');
                $.ajax({
                    xhrFields: { withCredentials: true },
                    type: "POST",
                    url: "/v1/me/friend_requests/" + requestID + "/block/",
                    data: JSON.stringify({
                        'request_id': requestID
                    }),
                    contentType: "application/json; charset=utf-8",
                    dataType: "json",
                    success: function success() {
                        $('#friend_request_' + requestID).remove();
                    },
                    error: function error(XMLHttpRequest) {
                        if (XMLHttpRequest.status === 500) {
                            $("#server_error").show();
                        }
                    }
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
//# sourceMappingURL=data:application/json;charset:utf-8;base64,eyJ2ZXJzaW9uIjozLCJzb3VyY2VzIjpbIm5vZGVfbW9kdWxlcy9icm93c2VyaWZ5L25vZGVfbW9kdWxlcy9icm93c2VyLXBhY2svX3ByZWx1ZGUuanMiLCIvVXNlcnMvbXdpc25lci9Qcm9qZWN0cy9zYWdlYnJldy9jb20uc2FnZWJyZXcud2ViL3NhZ2VicmV3L3NhZ2VicmV3L3N0YXRpYy9qcy9zcmMvY29tcG9uZW50cy9hdXRoZWQvbmF2YmFyLmpzIiwiL1VzZXJzL213aXNuZXIvUHJvamVjdHMvc2FnZWJyZXcvY29tLnNhZ2VicmV3LndlYi9zYWdlYnJldy9zYWdlYnJldy9zdGF0aWMvanMvc3JjL2NvbXBvbmVudHMvaGVscGVycy5qcyIsIi9Vc2Vycy9td2lzbmVyL1Byb2plY3RzL3NhZ2VicmV3L2NvbS5zYWdlYnJldy53ZWIvc2FnZWJyZXcvc2FnZWJyZXcvc3RhdGljL2pzL3NyYy9jb21wb25lbnRzL2luaXQuanMiLCIvVXNlcnMvbXdpc25lci9Qcm9qZWN0cy9zYWdlYnJldy9jb20uc2FnZWJyZXcud2ViL3NhZ2VicmV3L3NhZ2VicmV3L3N0YXRpYy9qcy9zcmMvdXNlci1hbm9uZWQuanMiXSwibmFtZXMiOltdLCJtYXBwaW5ncyI6IkFBQUE7Ozs7Ozs7Ozs7OztBQ0tBLElBQUksUUFBUSxHQUFHLE9BQU8sQ0FBQyxVQUFVLENBQUMsQ0FBQzs7Ozs7O0FBTW5DLFNBQVMsTUFBTSxHQUFHO0FBQ2QsS0FBQyxDQUFDLFFBQVEsQ0FBQyxDQUFDLEtBQUssQ0FBQyxZQUFXOzs7OztBQUt6QixlQUFPLENBQUMsR0FBRyxDQUFDLGNBQWMsQ0FBQyxDQUFDOztBQUU1QixnQkFBUSxDQUFDLFFBQVEsQ0FBQyxHQUFHLENBQUMsRUFBQyxHQUFHLEVBQUUsOEJBQThCLEVBQUMsQ0FBQyxDQUFDLElBQUksQ0FBQyxVQUFTLElBQUksRUFBQztBQUM1RSxhQUFDLENBQUMsdUJBQXVCLENBQUMsQ0FBQyxNQUFNLENBQUMsSUFBSSxDQUFDLE9BQU8sQ0FBQyxJQUFJLENBQUMsQ0FBQztBQUNyRCxnQkFBSSxJ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Q0FBQztBQUNwQyx3QkFBb0IsRUFBRSxDQUFDO0FBQ3ZCLFdBQU8sQ0FBQyxHQUFHLENBQUMscUJBQXFCLENBQUMsQ0FBQztDQUN0Qzs7Ozs7O0FBS00sU0FBUyxZQUFZLEdBQUc7QUFDM0IsV0FBTyxDQUFDLEdBQUcsQ0FBQyxvQkFBb0IsQ0FBQyxDQUFDO0FBQ2xDLFdBQU8sQ0FBQyxHQUFHLENBQUMsbUJBQW1CLENBQUMsQ0FBQztDQUNwQzs7Ozs7Ozs7OztBQ3RGRCxJQUFJLFlBQVksR0FBRyxPQUFPLENBQUMsbUJBQW1CLENBQUMsQ0FBQyxZQUFZLENBQUM7QUFDN0QsSUFBSSxTQUFTLEdBQUcsT0FBTyxDQUFDLDRCQUE0QixDQUFDLENBQUMsYUFBYSxDQUFDOzs7QUFHcEUsWUFBWSxFQUFFLENBQUM7QUFDZixTQUFTLEVBQUUsQ0FBQyIsImZpbGUiOiJnZW5lcmF0ZWQuanMiLCJzb3VyY2VSb290IjoiIiwic291cmNlc0NvbnRlbnQiOlsiKGZ1bmN0aW9uIGUodCxuLHIpe2Z1bmN0aW9uIHMobyx1KXtpZighbltvXSl7aWYoIXRbb10pe3ZhciBhPXR5cGVvZiByZXF1aXJlPT1cImZ1bmN0aW9uXCImJnJlcXVpcmU7aWYoIXUmJmEpcmV0dXJuIGEobywhMCk7aWYoaSlyZXR1cm4gaShvLCEwKTt2YXIgZj1uZXcgRXJyb3IoXCJDYW5ub3QgZmluZCBtb2R1bGUgJ1wiK28rXCInXCIpO3Rocm93IGYuY29kZT1cIk1PRFVMRV9OT1RfRk9VTkRcIixmfXZhciBsPW5bb109e2V4cG9ydHM6e319O3Rbb11bMF0uY2FsbChsLmV4cG9ydHMsZnVuY3Rpb24oZSl7dmFyIG49dFtvXVsxXVtlXTtyZXR1cm4gcyhuP246ZSl9LGwsbC5leHBvcnRzLGUsdCxuLHIpfXJldHVybiBuW29dLmV4cG9ydHN9dmFyIGk9dHlwZW9mIHJlcXVpcmU9PVwiZnVuY3Rpb25cIiYmcmVxdWlyZTtmb3IodmFyIG89MDtvPHIubGVuZ3RoO28rKylzKHJbb10pO3JldHVybiBzfSkiLCIvKipcbiAqIEBmaWxlXG4gKiBBbGwgdGhlIGZ1bmN0aW9uYWxpdHkgZm9yIHRoZSBuYXZiYXIuXG4gKiBUT0RPOiBSZW9yZ2FuaXplLlxuICovXG52YXIgc2FnZWJyZXcgPSByZXF1aXJlKCdzYWdlYnJldycpO1xuXG4vKipcbiAqICBTY29wZSAtIFVzZXIgQXV0aGVkXG4gKiAgQWxsIHRoaW5ncyByZWxhdGluZyB0byB0aGUgbmF2YmFyLlxuICovXG5mdW5jdGlvbiBuYXZiYXIoKSB7XG4gICAgJChkb2N1bWVudCkucmVhZHkoZnVuY3Rpb24oKSB7XG4gICAgICAgIC8vXG4gICAgICAgIC8vIE5vdGlmaWNhdGlvbnNcbiAgICAgICAgLy8gUmV0cmlldmVzIGFsbCB0aGUgbm90aWZpY2F0aW9ucyBmb3IgYSBnaXZlbiB1c2VyIGFuZCBnYXRoZXJzIGhvd1xuICAgICAgICAvLyBtYW55IGhhdmUgYmVlbiBzZWVuIG9yIHVuc2Vlbi5cbiAgICAgICAgY29uc29sZS5sb2coXCJOYXZiYXIgU3RhcnRcIik7XG5cbiAgICAgICAgc2FnZWJyZXcucmVzb3VyY2UuZ2V0KHt1cmw6IFwiL3YxL21lL25vdGlmaWNhdGlvbnMvcmVuZGVyL1wifSkudGhlbihmdW5jdGlvbihkYXRhKXtcbiAgICAgICAgICAgICQoJyNub3RpZmljYXRpb25fd3JhcHBlcicpLmFwcGVuZChkYXRhLnJlc3VsdHMuaHRtbCk7XG4gICAgICAgICAgICBpZiAoZGF0YS5yZXN1bHRzLnVuc2VlbiA+IDApIHtcbiAgICAgICAgICAgICAgICAkKCcjanMtbm90aWZpY2F0aW9uX25vdGlmaWVyX3dyYXBwZXInKS5hcHBlbmQoJzxzcGFuIGNsYXNzPVwibmF2YmFyLW5ldyBzYl9ub3RpZmllclwiIGlkPVwianMtc2Jfbm90aWZpY2F0aW9uc19ub3RpZmllclwiPicgKyBkYXRhLnJlc3VsdHMudW5zZWVuICsgJzwvc3Bhbj4nKTtcbiAgICAgICAgICAgIH1cbiAgICAgICAgfSk7XG5cbiAgICAgICAgLy8gU2hvd3MgdGhlIG5vdGlmaWNhdGlvbnMgd2hlbiB0aGUgbm90aWZpY2F0aW9uIGljb24gaXMgY2xpY2tlZFxuICAgICAgICAkKFwiLnNob3dfbm90aWZpY2F0aW9ucy1hY3Rpb25cIikuY2xpY2soZnVuY3Rpb24gKCkge1xuICAgICAgICAgICAgJChcIiNub3RpZmljYXRpb25fZGl2XCIpLmZhZGVUb2dnbGUoKTtcbiAgICAgICAgICAgIGlmICgkKCcjanMtbm90aWZpY2F0aW9uX25vdGlmaWVyX3dyYXBwZXInKS5jaGlsZHJlbigpLmxlbmd0aCA+IDApIHtcbiAgICAgICAgICAgICAgICAkLmFqYXgoe1xuICAgICAgICAgICAgICAgICAgICB4aHJGaWVsZHM6IHt3aXRoQ3JlZGVudGlhbHM6IHRydWV9LFxuICAgICAgICAgICAgICAgICAgICB0eXBlOiBcIkdFVFwiLFxuICAgICAgICAgICAgICAgICAgICB1cmw6IFwiL3YxL21lL25vdGlmaWNhdGlvbnMvP3NlZW49dHJ1ZVwiLFxuICAgICAgICAgICAgICAgICAgICBjb250ZW50VHlwZTogXCJhcHBsaWNhdGlvbi9qc29uOyBjaGFyc2V0PXV0Zi04XCIsXG4gICAgICAgICAgICAgICAgICAgIGRhdGFUeXBlOiBcImpzb25cIixcbiAgICAgICAgICAgICAgICAgICAgc3VjY2VzczogZnVuY3Rpb24gKCkge1xuICAgICAgICAgICAgICAgICAgICAgICAgJCgnI2pzLXNiX25vdGlmaWNhdGlvbnNfbm90aWZpZXInKS5yZW1vdmUoKTtcbiAgICAgICAgICAgICAgICAgICAgfSxcbiAgICAgICAgICAgICAgICAgICAgZXJyb3I6IGZ1bmN0aW9uIChYTUxIdHRwUmVxdWVzdCkge1xuICAgICAgICAgICAgICAgICAgICAgICAgZXJyb3JEaXNwbGF5KFhNTEh0dHBSZXF1ZXN0KTtcbiAgICAgICAgICAgICAgICAgICAgfVxuICAgICAgICAgICAgICAgIH0pO1xuICAgICAgICAgICAgfVxuICAgICAgICB9KTtcblxuICAgICAgICAvL1xuICAgICAgICAvLyBSZXAgV2FzIFZpZXdlZD9cbiAgICAgICAgJChcIi5zaG93LXJlcHV0YXRpb24tYWN0aW9uXCIpLm9uKFwiY2xpY2tcIiwgZnVuY3Rpb24gKCkge1xuICAgICAgICAgICAgJC5hamF4KHtcbiAgICAgICAgICAgICAgICB4aHJGaWVsZHM6IHt3aXRoQ3JlZGVudGlhbHM6IHRydWV9LFxuICAgICAgICAgICAgICAgIHR5cGU6IFwiUFVUXCIsXG4gICAgICAgICAgICAgICAgdXJsOiBcIi92MS9tZS9cIixcbiAgICAgICAgICAgICAgICBjb250ZW50VHlwZTogXCJhcHBsaWNhdGlvbi9qc29uOyBjaGFyc2V0PXV0Zi04XCIsXG4gICAgICAgICAgICAgICAgZGF0YVR5cGU6IFwianNvblwiLFxuICAgICAgICAgICAgICAgIGRhdGE6IEpTT04uc3RyaW5naWZ5KHtcbiAgICAgICAgICAgICAgICAgICAgXCJyZXB1dGF0aW9uX3VwZGF0ZV9zZWVuXCI6IHRydWVcbiAgICAgICAgICAgICAgICB9KVxuICAgICAgICAgICAgfSk7XG4gICAgICAgIH0pO1xuXG4gICAgICAgIC8vXG4gICAgICAgIC8vIFNob3cgUmVwXG4gICAgICAgICQuYWpheCh7XG4gICAgICAgICAgICB4aHJGaWVsZHM6IHt3aXRoQ3JlZGVudGlhbHM6IHRydWV9LFxuICAgICAgICAgICAgdHlwZTogXCJHRVRcIixcbiAgICAgICAgICAgIHVybDogXCIvdjEvcHJvZmlsZXMvXCIgKyAkKFwiI3JlcHV0YXRpb25fdG90YWxcIikuZGF0YSgndXNlcm5hbWUnKSArIFwiL3JlcHV0YXRpb24vXCIsXG4gICAgICAgICAgICBjb250ZW50VHlwZTogXCJhcHBsaWNhdGlvbi9qc29uOyBjaGFyc2V0PXV0Zi04XCIsXG4gICAgICAgICAgICBkYXRhVHlwZTogXCJqc29uXCIsXG4gICAgICAgICAgICBzdWNjZXNzOiBmdW5jdGlvbiAoZGF0YSkge1xuICAgICAgICAgICAgICAgICQoXCIjcmVwdXRhdGlvbl90b3RhbFwiKS5hcHBlbmQoXCI8cD5cIiArIGRhdGFbXCJyZXB1dGF0aW9uXCJdICsgXCI8L3A+XCIpO1xuICAgICAgICAgICAgfSxcbiAgICAgICAgICAgIGVycm9yOiBmdW5jdGlvbihYTUxIdHRwUmVxdWVzdCwgdGV4dFN0YXR1cywgZXJyb3JUaHJvd24pIHtcbiAgICAgICAgICAgICAgICBpZihYTUxIdHRwUmVxdWVzdC5zdGF0dXMgPT09IDUwMCl7XG4gICAgICAgICAgICAgICAgICAgICQoXCIjc2VydmVyX2Vycm9yXCIpLnNob3coKTtcbiAgICAgICAgICAgICAgICB9XG4gICAgICAgICAgICB9XG4gICAgICAgIH0pO1xuXG4gICAgICAgIC8vXG4gICAgICAgIC8vIFNlYXJjaFxuICAgICAgICAkKFwiLmZ1bGxfc2VhcmNoLWFjdGlvblwiKS5jbGljayhmdW5jdGlvbihlKSB7XG4gICAgICAgICAgICB2YXIgc2VhcmNoX3BhcmFtID0gKCQoJyNzYl9zZWFyY2hfaW5wdXQnKS52YWwoKSk7XG4gICAgICAgICAgICB3aW5kb3cubG9jYXRpb24uaHJlZiA9IFwiL3NlYXJjaC8/cT1cIiArIHNlYXJjaF9wYXJhbSArIFwiJnBhZ2U9MSZmaWx0ZXI9Z2VuZXJhbFwiO1xuICAgICAgICB9KTtcbiAgICAgICAgJChcIiNzYl9zZWFyY2hfaW5wdXRcIikua2V5dXAoZnVuY3Rpb24oZSkge1xuICAgICAgICAgICAgaWYoZS53aGljaCA9PT0gMTAgfHwgZS53aGljaCA9PT0gMTMpIHtcbiAgICAgICAgICAgICAgICB2YXIgc2VhcmNoX3BhcmFtID0gKCQoJyNzYl9zZWFyY2hfaW5wdXQnKS52YWwoKSk7XG4gICAgICAgICAgICAgICAgd2luZG93LmxvY2F0aW9uLmhyZWYgPSBcIi9zZWFyY2gvP3E9XCIgKyBzZWFyY2hfcGFyYW0gKyBcIiZwYWdlPTEmZmlsdGVyPWdlbmVyYWxcIjtcbiAgICAgICAgICAgIH1cbiAgICAgICAgfSk7XG5cbiAgICAgICAgLy9cbiAgICAgICAgLy9cblxuICAgICAgICAvL1xuICAgICAgICAvLyBGcmllbmRzXG4gICAgICAgIC8vIFJldHJpZXZlcyBhbGwgdGhlIGZyaWVuZCByZXF1ZXN0cyBmb3IgYSBnaXZlbiB1c2VyIGFuZCBnYXRoZXJzIGhvd1xuICAgICAgICAvLyBtYW55IGhhdmUgYmVlbiBzZWVuIG9yIHVuc2Vlbi5cbiAgICAgICAgJC5hamF4KHtcbiAgICAgICAgICAgIHhockZpZWxkczoge3dpdGhDcmVkZW50aWFsczogdHJ1ZX0sXG4gICAgICAgICAgICB0eXBlOiBcIkdFVFwiLFxuICAgICAgICAgICAgdXJsOiBcIi92MS9tZS9mcmllbmRfcmVxdWVzdHMvcmVuZGVyL1wiLFxuICAgICAgICAgICAgY29udGVudFR5cGU6IFwiYXBwbGljYXRpb24vanNvbjsgY2hhcnNldD11dGYtOFwiLFxuICAgICAgICAgICAgZGF0YVR5cGU6IFwianNvblwiLFxuICAgICAgICAgICAgc3VjY2VzczogZnVuY3Rpb24gKGRhdGEpIHtcbiAgICAgICAgICAgICAgICAkKCcjZnJpZW5kX3JlcXVlc3Rfd3JhcHBlcicpLmFwcGVuZChkYXRhLnJlc3VsdHMuaHRtbCk7XG4gICAgICAgICAgICAgICAgaWYgKGRhdGEucmVzdWx0cy51bnNlZW4gPiAwKSB7XG4gICAgICAgICAgICAgICAgICAgICQoJyNqcy1mcmllbmRfcmVxdWVzdF9ub3RpZmllcl93cmFwcGVyJykuYXBwZW5kKCc8c3BhbiBjbGFzcz1cIm5hdmJhci1uZXcgc2Jfbm90aWZpZXJcIiBpZD1cImpzLXNiX2ZyaWVuZF9yZXF1ZXN0X25vdGlmaWVyXCI+JyArIGRhdGEucmVzdWx0cy51bnNlZW4gKyAnPC9zcGFuPicpO1xuICAgICAgICAgICAgICAgIH1cbiAgICAgICAgICAgIH0sXG4gICAgICAgICAgICBlcnJvcjogZnVuY3Rpb24gKFhNTEh0dHBSZXF1ZXN0KSB7XG4gICAgICAgICAgICAgICAgaWYgKFhNTEh0dHBSZXF1ZXN0LnN0YXR1cyA9PT0gNTAwKSB7XG4gICAgICAgICAgICAgICAgICAgICQoXCIjc2VydmVyX2Vycm9yXCIpLnNob3coKTtcbiAgICAgICAgICAgICAgICB9XG4gICAgICAgICAgICB9XG4gICAgICAgIH0pO1xuXG4gICAgICAgIC8vIFNob3dzIHRoZSBmcmllbmQgcmVxdWVzdHMgd2hlbiB0aGUgZnJpZW5kIHJlcXVlc3QgaWNvbiBpcyBjbGlja2VkXG4gICAgICAgICQoXCIuc2hvd19mcmllbmRfcmVxdWVzdC1hY3Rpb25cIikuY2xpY2soZnVuY3Rpb24gKCkge1xuICAgICAgICAgICAgJChcIiNmcmllbmRfcmVxdWVzdF9kaXZcIikuZmFkZVRvZ2dsZSgpO1xuICAgICAgICAgICAgaWYgKCQoJyNqcy1zYl9mcmllbmRfcmVxdWVzdF9ub3RpZmllcicpLmxlbmd0aCA+IDApIHtcbiAgICAgICAgICAgICAgICAkLmFqYXgoe1xuICAgICAgICAgICAgICAgICAgICB4aHJGaWVsZHM6IHt3aXRoQ3JlZGVudGlhbHM6IHRydWV9LFxuICAgICAgICAgICAgICAgICAgICB0eXBlOiBcIkdFVFwiLFxuICAgICAgICAgICAgICAgICAgICB1cmw6IFwiL3YxL21lL2ZyaWVuZF9yZXF1ZXN0cy8/c2Vlbj10cnVlXCIsXG4gICAgICAgICAgICAgICAgICAgIGNvbnRlbnRUeXBlOiBcImFwcGxpY2F0aW9uL2pzb247IGNoYXJzZXQ9dXRmLThcIixcbiAgICAgICAgICAgICAgICAgICAgZGF0YVR5cGU6IFwianNvblwiLFxuICAgICAgICAgICAgICAgICAgICBzdWNjZXNzOiBmdW5jdGlvbiAoKSB7XG4gICAgICAgICAgICAgICAgICAgICAgICAkKCcjanMtc2JfZnJpZW5kX3JlcXVlc3Rfbm90aWZpZXInKS5yZW1vdmUoKTtcbiAgICAgICAgICAgICAgICAgICAgfSxcbiAgICAgICAgICAgICAgICAgICAgZXJyb3I6IGZ1bmN0aW9uICgpIHtcbiAgICAgICAgICAgICAgICAgICAgICAgICQoXCIjc2VydmVyX2Vycm9yXCIpLnNob3coKTtcbiAgICAgICAgICAgICAgICAgICAgfVxuICAgICAgICAgICAgICAgIH0pO1xuICAgICAgICAgICAgfVxuICAgICAgICAgICAgJChcIi5yZXNwb25kX2ZyaWVuZF9yZXF1ZXN0LWFjY2VwdC1hY3Rpb25cIikuY2xpY2soZnVuY3Rpb24gKGV2ZW50KSB7XG4gICAgICAgICAgICAgICAgZXZlbnQucHJldmVudERlZmF1bHQoKTtcbiAgICAgICAgICAgICAgICB2YXIgcmVxdWVzdElEID0gJCh0aGlzKS5kYXRhKCdyZXF1ZXN0X2lkJyk7XG4gICAgICAgICAgICAgICAgJC5hamF4KHtcbiAgICAgICAgICAgICAgICAgICAgeGhyRmllbGRzOiB7d2l0aENyZWRlbnRpYWxzOiB0cnVlfSxcbiAgICAgICAgICAgICAgICAgICAgdHlwZTogXCJQT1NUXCIsXG4gICAgICAgICAgICAgICAgICAgIHVybDogXCIvdjEvbWUvZnJpZW5kX3JlcXVlc3RzL1wiICsgcmVxdWVzdElEICsgXCIvYWNjZXB0L1wiLFxuICAgICAgICAgICAgICAgICAgICBkYXRhOiBKU09OLnN0cmluZ2lmeSh7XG4gICAgICAgICAgICAgICAgICAgICAgICAncmVxdWVzdF9pZCc6IHJlcXVlc3RJRFxuICAgICAgICAgICAgICAgICAgICB9KSxcbiAgICAgICAgICAgICAgICAgICAgY29udGVudFR5cGU6IFwiYXBwbGljYXRpb24vanNvbjsgY2hhcnNldD11dGYtOFwiLFxuICAgICAgICAgICAgICAgICAgICBkYXRhVHlwZTogXCJqc29uXCIsXG4gICAgICAgICAgICAgICAgICAgIHN1Y2Nlc3M6IGZ1bmN0aW9uICgpIHtcbiAgICAgICAgICAgICAgICAgICAgICAgICQoJyNmcmllbmRfcmVxdWVzdF8nICsgcmVxdWVzdElEKS5yZW1vdmUoKTtcbiAgICAgICAgICAgICAgICAgICAgfSxcbiAgICAgICAgICAgICAgICAgICAgZXJyb3I6IGZ1bmN0aW9uIChYTUxIdHRwUmVxdWVzdCkge1xuICAgICAgICAgICAgICAgICAgICAgICAgaWYgKFhNTEh0dHBSZXF1ZXN0LnN0YXR1cyA9PT0gNTAwKSB7XG4gICAgICAgICAgICAgICAgICAgICAgICAgICAgJChcIiNzZXJ2ZXJfZXJyb3JcIikuc2hvdygpO1xuICAgICAgICAgICAgICAgICAgICAgICAgfVxuICAgICAgICAgICAgICAgICAgICB9XG4gICAgICAgICAgICAgICAgfSk7XG4gICAgICAgICAgICB9KTtcbiAgICAgICAgICAgICQoXCIucmVzcG9uZF9mcmllbmRfcmVxdWVzdC1kZWNsaW5lLWFjdGlvblwiKS5jbGljayhmdW5jdGlvbiAoZXZlbnQpIHtcbiAgICAgICAgICAgICAgICBldmVudC5wcmV2ZW50RGVmYXVsdCgpO1xuICAgICAgICAgICAgICAgIHZhciByZXF1ZXN0SUQgPSAkKHRoaXMpLmRhdGEoJ3JlcXVlc3RfaWQnKTtcbiAgICAgICAgICAgICAgICAkLmFqYXgoe1xuICAgICAgICAgICAgICAgICAgICB4aHJGaWVsZHM6IHt3aXRoQ3JlZGVudGlhbHM6IHRydWV9LFxuICAgICAgICAgICAgICAgICAgICB0eXBlOiBcIlBPU1RcIixcbiAgICAgICAgICAgICAgICAgICAgdXJsOiBcIi92MS9tZS9mcmllbmRfcmVxdWVzdHMvXCIgKyByZXF1ZXN0SUQgKyBcIi9kZWNsaW5lL1wiLFxuICAgICAgICAgICAgICAgICAgICBkYXRhOiBKU09OLnN0cmluZ2lmeSh7XG4gICAgICAgICAgICAgICAgICAgICAgICAncmVxdWVzdF9pZCc6IHJlcXVlc3RJRFxuICAgICAgICAgICAgICAgICAgICB9KSxcbiAgICAgICAgICAgICAgICAgICAgY29udGVudFR5cGU6IFwiYXBwbGljYXRpb24vanNvbjsgY2hhcnNldD11dGYtOFwiLFxuICAgICAgICAgICAgICAgICAgICBkYXRhVHlwZTogXCJqc29uXCIsXG4gICAgICAgICAgICAgICAgICAgIHN1Y2Nlc3M6IGZ1bmN0aW9uICgpIHtcbiAgICAgICAgICAgICAgICAgICAgICAgICQoJyNmcmllbmRfcmVxdWVzdF8nICsgcmVxdWVzdElEKS5yZW1vdmUoKTtcbiAgICAgICAgICAgICAgICAgICAgfSxcbiAgICAgICAgICAgICAgICAgICAgZXJyb3I6IGZ1bmN0aW9uIChYTUxIdHRwUmVxdWVzdCkge1xuICAgICAgICAgICAgICAgICAgICAgICAgaWYgKFhNTEh0dHBSZXF1ZXN0LnN0YXR1cyA9PT0gNTAwKSB7XG4gICAgICAgICAgICAgICAgICAgICAgICAgICAgJChcIiNzZXJ2ZXJfZXJyb3JcIikuc2hvdygpO1xuICAgICAgICAgICAgICAgICAgICAgICAgfVxuICAgICAgICAgICAgICAgICAgICB9XG4gICAgICAgICAgICAgICAgfSk7XG4gICAgICAgICAgICB9KTtcbiAgICAgICAgICAgICQoXCIucmVzcG9uZF9mcmllbmRfcmVxdWVzdC1ibG9jay1hY3Rpb25cIikuY2xpY2soZnVuY3Rpb24gKGV2ZW50KSB7XG4gICAgICAgICAgICAgICAgZXZlbnQucHJldmVudERlZmF1bHQoKTtcbiAgICAgICAgICAgICAgICB2YXIgcmVxdWVzdElEID0gJCh0aGlzKS5kYXRhKCdyZXF1ZXN0X2lkJyk7XG4gICAgICAgICAgICAgICAgJC5hamF4KHtcbiAgICAgICAgICAgICAgICAgICAgeGhyRmllbGRzOiB7d2l0aENyZWRlbnRpYWxzOiB0cnVlfSxcbiAgICAgICAgICAgICAgICAgICAgdHlwZTogXCJQT1NUXCIsXG4gICAgICAgICAgICAgICAgICAgIHVybDogXCIvdjEvbWUvZnJpZW5kX3JlcXVlc3RzL1wiICsgcmVxdWVzdElEICsgXCIvYmxvY2svXCIsXG4gICAgICAgICAgICAgICAgICAgIGRhdGE6IEpTT04uc3RyaW5naWZ5KHtcbiAgICAgICAgICAgICAgICAgICAgICAgICdyZXF1ZXN0X2lkJzogcmVxdWVzdElEXG4gICAgICAgICAgICAgICAgICAgIH0pLFxuICAgICAgICAgICAgICAgICAgICBjb250ZW50VHlwZTogXCJhcHBsaWNhdGlvbi9qc29uOyBjaGFyc2V0PXV0Zi04XCIsXG4gICAgICAgICAgICAgICAgICAgIGRhdGFUeXBlOiBcImpzb25cIixcbiAgICAgICAgICAgICAgICAgICAgc3VjY2VzczogZnVuY3Rpb24gKCkge1xuICAgICAgICAgICAgICAgICAgICAgICAgJCgnI2ZyaWVuZF9yZXF1ZXN0XycgKyByZXF1ZXN0SUQpLnJlbW92ZSgpO1xuICAgICAgICAgICAgICAgICAgICB9LFxuICAgICAgICAgICAgICAgICAgICBlcnJvcjogZnVuY3Rpb24gKFhNTEh0dHBSZXF1ZXN0KSB7XG4gICAgICAgICAgICAgICAgICAgICAgICBpZiAoWE1MSHR0cFJlcXVlc3Quc3RhdHVzID09PSA1MDApIHtcbiAgICAgICAgICAgICAgICAgICAgICAgICAgICAkKFwiI3NlcnZlcl9lcnJvclwiKS5zaG93KCk7XG4gICAgICAgICAgICAgICAgICAgICAgICB9XG4gICAgICAgICAgICAgICAgICAgIH1cbiAgICAgICAgICAgICAgICB9KTtcbiAgICAgICAgICAgIH0pO1xuICAgICAgICB9KTtcbiAgICB9KTtcbn1cblxuZXhwb3J0IGZ1bmN0aW9uIGluaXROYXZiYXIoKSB7XG4gICAgcmV0dXJuIG5hdmJhcigpO1xufSIsIi8qKlxuICogQGZpbGVcbiAqIEhlbHBlciBmdW5jdGlvbnMgdGhhdCBhcmVuJ3QgZ2xvYmFsLlxuICovXG5cbi8qKlxuICogR2V0IGNvb2tpZSBiYXNlZCBieSBuYW1lLlxuICogQHBhcmFtIG5hbWVcbiAqIEByZXR1cm5zIHsqfVxuICovXG5leHBvcnQgZnVuY3Rpb24gZ2V0Q29va2llKG5hbWUpIHtcbiAgICB2YXIgY29va2llVmFsdWUgPSBudWxsO1xuICAgIGlmIChkb2N1bWVudC5jb29raWUgJiYgZG9jdW1lbnQuY29va2llICE9PSBcIlwiKSB7XG4gICAgICAgIHZhciBjb29raWVzID0gZG9jdW1lbnQuY29va2llLnNwbGl0KCc7Jyk7XG4gICAgICAgIGZvciAodmFyIGkgPSAwOyBpIDwgY29va2llcy5sZW5ndGg7IGkgKz0gMSkge1xuICAgICAgICAgICAgdmFyIGNvb2tpZSA9ICQudHJpbShjb29raWVzW2ldKTtcbiAgICAgICAgICAgIC8vIERvZXMgdGhpcyBjb29raWUgc3RyaW5nIGJlZ2luIHdpdGggdGhlIG5hbWUgd2Ugd2FudD9cblxuICAgICAgICAgICAgaWYgKGNvb2tpZS5zdWJzdHJpbmcoMCwgbmFtZS5sZW5ndGggKyAxKSA9PT0gKG5hbWUgKyAnPScpKSB7XG4gICAgICAgICAgICAgICAgY29va2llVmFsdWUgPSBkZWNvZGVVUklDb21wb25lbnQoY29va2llLnN1YnN0cmluZyhuYW1lLmxlbmd0aCArIDEpKTtcbiAgICAgICAgICAgICAgICBicmVhaztcbiAgICAgICAgICAgIH1cbiAgICAgICAgfVxuICAgIH1cbiAgICByZXR1cm4gY29va2llVmFsdWU7XG59XG5cbi8qKlxuICogQ2hlY2sgaWYgSFRUUCBtZXRob2QgcmVxdWlyZXMgQ1NSRi5cbiAqIEBwYXJhbSBtZXRob2RcbiAqIEByZXR1cm5zIHtib29sZWFufVxuICovXG5leHBvcnQgZnVuY3Rpb24gY3NyZlNhZmVNZXRob2QobWV0aG9kKSB7XG4gICAgLy8gdGhlc2UgSFRUUCBtZXRob2RzIGRvIG5vdCByZXF1aXJlIENTUkYgcHJvdGVjdGlvblxuICAgIHJldHVybiAoL14oR0VUfEhFQUR8T1BUSU9OU3xUUkFDRSkkLy50ZXN0KG1ldGhvZCkpO1xufSIsIi8qKlxuICogQGZpbGVcbiAqIEluaXQgdGhlIFNCIHdlYnNpdGUuXG4gKiBnbG9iYWxJbml0IC0gUnVucyBvbiBhbGwgcGFnZXMuXG4gKiBVc2VyQXV0aGVkSW5pdCAtIFJ1bnMgb24gYXV0aGVkIHBhZ2VzLlxuICogdXNlckFub25Jbml0IC0gUnVucyBvbiBhbm9uIHBhZ2VzLlxuICogVE9ETzogVGhlIGluZGl2aWR1YWwgaW5pdCBmdW5jdGlvbnMgY291bGQgYmUgdHVybmVkIGludG8gYXJyYXlzIG9yIG9iamVjdHMgYW5kIHRoZW5cbiAqIGxvb3BlZCBvdmVyLlxuICovXG52YXIgaGVscGVycyA9IHJlcXVpcmUoJy4vaGVscGVycycpO1xuXG4vKipcbiAqIFNjb3BlIC0gR2xvYmFsXG4gKiBBamF4IFNldHVwXG4gKiAtLSBBdXRvbWF0aWNhbGx5IGFkZCBDU1JGIGNvb2tpZSB2YWx1ZSB0byBhbGwgYWpheCByZXF1ZXN0cy5cbiAqL1xuZnVuY3Rpb24gYWpheFNldHVwKCkge1xuICAgICQuYWpheFNldHVwKHtcbiAgICAgICAgYmVmb3JlU2VuZDogZnVuY3Rpb24gKHhociwgc2V0dGluZ3MpIHtcbiAgICAgICAgICAgIGlmICghaGVscGVycy5jc3JmU2FmZU1ldGhvZChzZXR0aW5ncy50eXBlKSAmJiAhdGhpcy5jcm9zc0RvbWFpbikge1xuICAgICAgICAgICAgICAgIHhoci5zZXRSZXF1ZXN0SGVhZGVyKFwiWC1DU1JGVG9rZW5cIiwgaGVscGVycy5nZXRDb29raWUoJ2NzcmZ0b2tlbicpKTtcbiAgICAgICAgICAgIH1cbiAgICAgICAgfVxuICAgIH0pO1xufVxuXG4vKipcbiAqICBTY29wZSAtIFVzZXIgQXV0aGVkXG4gKiAgQWRkcyBhbiBldmVudCBoYW5kbGVyIHRvIHBhZ2UgdW5sb2FkIHRoYXQgYWpheCBwb3N0cyBhbGwgdGhlIHVzZXIncyBhY3Rpb25zIHRoYXQgb2NjdXJlZCBkdXJpbmcgdGhlIHBhZ2UuXG4gKiAgVE9ETzogU3RvcCBkb2luZyB0aGlzLlxuICogIE5vdCBvbmx5IGFyZSBub24tYXN5bmMgYWpheCBjYWxscyBkZXByZWNhdGVkIGl0IGhvbGRzIHRoZSBwYWdlIGxvYWQgdXAgZm9yIHRoZSB1c2VyLlxuICogIFRoZXkgY2FuJ3QgZXZlbiBzdGFydCBsb2FkaW5nIHRoZSBuZXh0IHBhZ2UgdW50aWwgdGhpcyBpcyBjb21wbGV0ZWQuXG4gKi9cbmZ1bmN0aW9uIGNvbGxlY3RBdXRoZWRBY3Rpb25zKCkge1xuICAgICQoZG9jdW1lbnQpLnJlYWR5KGZ1bmN0aW9uICgpIHtcbiAgICAgICAgXCJ1c2Ugc3RyaWN0XCI7XG4gICAgICAgIHdpbmRvdy5vbmJlZm9yZXVubG9hZCA9IGZ1bmN0aW9uICgpIHtcbiAgICAgICAgICAgIHZhciBvYmplY3RMaXN0ID0gW107XG4gICAgICAgICAgICAkKFwiLmpzLXBhZ2Utb2JqZWN0XCIpLmVhY2goZnVuY3Rpb24gKCkge1xuICAgICAgICAgICAgICAgIG9iamVjdExpc3QucHVzaCgkKHRoaXMpLmRhdGEoJ29iamVjdF91dWlkJykpO1xuICAgICAgICAgICAgfSk7XG4gICAgICAgICAgICBpZiAob2JqZWN0TGlzdC5sZW5ndGgpIHtcbiAgICAgICAgICAgICAgICAkLmFqYXgoe1xuICAgICAgICAgICAgICAgICAgICB4aHJGaWVsZHM6IHt3aXRoQ3JlZGVudGlhbHM6IHRydWV9LFxuICAgICAgICAgICAgICAgICAgICB0eXBlOiBcIlBPU1RcIixcbiAgICAgICAgICAgICAgICAgICAgYXN5bmM6IGZhbHNlLFxuICAgICAgICAgICAgICAgICAgICB1cmw6IFwiL2RvY3N0b3JlL3VwZGF0ZV9uZW9fYXBpL1wiLFxuICAgICAgICAgICAgICAgICAgICBkYXRhOiBKU09OLnN0cmluZ2lmeSh7XG4gICAgICAgICAgICAgICAgICAgICAgICAnb2JqZWN0X3V1aWRzJzogb2JqZWN0TGlzdFxuICAgICAgICAgICAgICAgICAgICB9KSxcbiAgICAgICAgICAgICAgICAgICAgY29udGVudFR5cGU6IFwiYXBwbGljYXRpb24vanNvbjsgY2hhcnNldD11dGYtOFwiLFxuICAgICAgICAgICAgICAgICAgICBkYXRhVHlwZTogXCJqc29uXCIsXG4gICAgICAgICAgICAgICAgICAgIGVycm9yOiBmdW5jdGlvbiAoWE1MSHR0cFJlcXVlc3QpIHtcbiAgICAgICAgICAgICAgICAgICAgICAgIGlmIChYTUxIdHRwUmVxdWVzdC5zdGF0dXMgPT09IDUwMCkge1xuICAgICAgICAgICAgICAgICAgICAgICAgICAgICQoXCIjc2VydmVyX2Vycm9yXCIpLnNob3coKTtcbiAgICAgICAgICAgICAgICAgICAgICAgIH1cbiAgICAgICAgICAgICAgICAgICAgfVxuICAgICAgICAgICAgICAgIH0pO1xuICAgICAgICAgICAgfVxuICAgICAgICB9O1xuICAgIH0pO1xufVxuXG5cblxuLyoqXG4gKiBUaGlzIGZ1bmN0aW9uIGlzIGNhbGxlZCBpbiBzYWdlYnJldy5qcyBtYWluIGZpbGUuXG4gKiBFYWNoIGluaXQgdGFzayBzaG91bGQgYmUgZGVmaW5lZCBpbiBpdCdzIG93biBmdW5jdGlvbiBmb3Igd2hhdGV2ZXIgcmVhc29uLlxuICogLS0gQmV0dGVyIGNvZGUgcmVhZGFiaWxpdHk/XG4gKi9cbmV4cG9ydCBmdW5jdGlvbiBnbG9iYWxJbml0KCkge1xuICAgIGNvbnNvbGUubG9nKFwiR2xvYmFsIEluaXQgU3RhcnRcIik7XG4gICAgYWpheFNldHVwKCk7XG4gICAgY29uc29sZS5sb2coXCJHbG9iYWwgSW5pdCBTdG9wXCIpO1xufVxuXG4vKipcbiAqIEF1dGggSW5pdC5cbiAqL1xuZXhwb3J0IGZ1bmN0aW9uIHVzZXJBdXRoZWRJbml0KCkge1xuICAgIGNvbnNvbGUubG9nKFwidXNlckF1dGhlZEluaXQgU3RhcnRcIik7XG4gICAgY29sbGVjdEF1dGhlZEFjdGlvbnMoKTtcbiAgICBjb25zb2xlLmxvZyhcInVzZXJBdXRoZWRJbml0IFN0b3BcIik7XG59XG5cbi8qKlxuICogQW5vbiBJbml0LlxuICovXG5leHBvcnQgZnVuY3Rpb24gdXNlckFub25Jbml0KCkge1xuICAgIGNvbnNvbGUubG9nKFwidXNlckFub25Jbml0IFN0YXJ0XCIpO1xuICAgIGNvbnNvbGUubG9nKFwidXNlckFub25Jbml0IFN0b3BcIik7XG59XG5cblxuXG5cbiIsIi8qKlxuICogQGZpbGVcbiAqIFVzZWQgb24gZXZlcnkgcGFnZSB3aXRoIGFuIGFub24gdXNlci5cbiAqL1xuXG52YXIgdXNlckFub25Jbml0ID0gcmVxdWlyZSgnLi9jb21wb25lbnRzL2luaXQnKS51c2VyQW5vbkluaXQ7XG52YXIgbG9naW5mb3JtID0gcmVxdWlyZSgnLi9jb21wb25lbnRzL2F1dGhlZC9uYXZiYXInKS5pbml0TG9naW5Gb3JtO1xuXG4vL0luaXQgdmFyaW91cyB0aGluZ3MgZm9yIGFub24gdXNlci5cbnVzZXJBbm9uSW5pdCgpO1xubG9naW5mb3JtKCk7XG5cblxuIl19
