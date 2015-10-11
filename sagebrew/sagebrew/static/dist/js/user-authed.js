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

},{"./helpers":2}],"user-authed":[function(require,module,exports){
/**
 * @file
 * Used on every page with an authed user.
 */

'use strict';

var userAuthedInit = require('./components/init').userAuthedInit;
var navbar = require('./components/authed/navbar').initNavbar;

// Init various things for authed user.
userAuthedInit();
navbar();

},{"./components/authed/navbar":1,"./components/init":3}]},{},["user-authed"])
//# sourceMappingURL=data:application/json;charset:utf-8;base64,eyJ2ZXJzaW9uIjozLCJzb3VyY2VzIjpbIm5vZGVfbW9kdWxlcy9icm93c2VyaWZ5L25vZGVfbW9kdWxlcy9icm93c2VyLXBhY2svX3ByZWx1ZGUuanMiLCIvVXNlcnMvbXdpc25lci9Qcm9qZWN0cy9zYWdlYnJldy9jb20uc2FnZWJyZXcud2ViL3NhZ2VicmV3L3NhZ2VicmV3L3N0YXRpYy9qcy9zcmMvY29tcG9uZW50cy9hdXRoZWQvbmF2YmFyLmpzIiwiL1VzZXJzL213aXNuZXIvUHJvamVjdHMvc2FnZWJyZXcvY29tLnNhZ2VicmV3LndlYi9zYWdlYnJldy9zYWdlYnJldy9zdGF0aWMvanMvc3JjL2NvbXBvbmVudHMvaGVscGVycy5qcyIsIi9Vc2Vycy9td2lzbmVyL1Byb2plY3RzL3NhZ2VicmV3L2NvbS5zYWdlYnJldy53ZWIvc2FnZWJyZXcvc2FnZWJyZXcvc3RhdGljL2pzL3NyYy9jb21wb25lbnRzL2luaXQuanMiLCIvVXNlcnMvbXdpc25lci9Qcm9qZWN0cy9zYWdlYnJldy9jb20uc2FnZWJyZXcud2ViL3NhZ2VicmV3L3NhZ2VicmV3L3N0YXRpYy9qcy9zcmMvdXNlci1hdXRoZWQuanMiXSwibmFtZXMiOltdLCJtYXBwaW5ncyI6IkFBQUE7Ozs7Ozs7Ozs7OztBQ0tBLElBQUksUUFBUSxHQUFHLE9BQU8sQ0FBQyxVQUFVLENBQUMsQ0FBQzs7Ozs7O0FBTW5DLFNBQVMsTUFBTSxHQUFHO0FBQ2QsS0FBQyxDQUFDLFFBQVEsQ0FBQyxDQUFDLEtBQUssQ0FBQyxZQUFXOzs7OztBQUt6QixlQUFPLENBQUMsR0FBRyxDQUFDLGNBQWMsQ0FBQyxDQUFDOztBQUU1QixnQkFBUSxDQUFDLFFBQVEsQ0FBQyxHQUFHLENBQUMsRUFBQyxHQUFHLEVBQUUsOEJBQThCLEVBQUMsQ0FBQyxDQUFDLElBQUksQ0FBQyxVQUFTLElBQUksRUFBQztBQUM1RSxhQUFDLENBQUMsdUJBQXVCLENBQUMsQ0FBQyxNQUFNLENBQUMsSUFBSSxDQUFDLE9BQU8sQ0FBQyxJQUFJLENBQUMsQ0FBQztBQUNyRCxnQkFBSSxJ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Q0FBQztBQUNwQyx3QkFBb0IsRUFBRSxDQUFDO0FBQ3ZCLFdBQU8sQ0FBQyxHQUFHLENBQUMscUJBQXFCLENBQUMsQ0FBQztDQUN0Qzs7Ozs7O0FBS00sU0FBUyxZQUFZLEdBQUc7QUFDM0IsV0FBTyxDQUFDLEdBQUcsQ0FBQyxvQkFBb0IsQ0FBQyxDQUFDO0FBQ2xDLFdBQU8sQ0FBQyxHQUFHLENBQUMsbUJBQW1CLENBQUMsQ0FBQztDQUNwQzs7Ozs7Ozs7OztBQ3RGRCxJQUFJLGNBQWMsR0FBRyxPQUFPLENBQUMsbUJBQW1CLENBQUMsQ0FBQyxjQUFjLENBQUM7QUFDakUsSUFBSSxNQUFNLEdBQUcsT0FBTyxDQUFDLDRCQUE0QixDQUFDLENBQUMsVUFBVSxDQUFDOzs7QUFHOUQsY0FBYyxFQUFFLENBQUM7QUFDakIsTUFBTSxFQUFFLENBQUMiLCJmaWxlIjoiZ2VuZXJhdGVkLmpzIiwic291cmNlUm9vdCI6IiIsInNvdXJjZXNDb250ZW50IjpbIihmdW5jdGlvbiBlKHQsbixyKXtmdW5jdGlvbiBzKG8sdSl7aWYoIW5bb10pe2lmKCF0W29dKXt2YXIgYT10eXBlb2YgcmVxdWlyZT09XCJmdW5jdGlvblwiJiZyZXF1aXJlO2lmKCF1JiZhKXJldHVybiBhKG8sITApO2lmKGkpcmV0dXJuIGkobywhMCk7dmFyIGY9bmV3IEVycm9yKFwiQ2Fubm90IGZpbmQgbW9kdWxlICdcIitvK1wiJ1wiKTt0aHJvdyBmLmNvZGU9XCJNT0RVTEVfTk9UX0ZPVU5EXCIsZn12YXIgbD1uW29dPXtleHBvcnRzOnt9fTt0W29dWzBdLmNhbGwobC5leHBvcnRzLGZ1bmN0aW9uKGUpe3ZhciBuPXRbb11bMV1bZV07cmV0dXJuIHMobj9uOmUpfSxsLGwuZXhwb3J0cyxlLHQsbixyKX1yZXR1cm4gbltvXS5leHBvcnRzfXZhciBpPXR5cGVvZiByZXF1aXJlPT1cImZ1bmN0aW9uXCImJnJlcXVpcmU7Zm9yKHZhciBvPTA7bzxyLmxlbmd0aDtvKyspcyhyW29dKTtyZXR1cm4gc30pIiwiLyoqXG4gKiBAZmlsZVxuICogQWxsIHRoZSBmdW5jdGlvbmFsaXR5IGZvciB0aGUgbmF2YmFyLlxuICogVE9ETzogUmVvcmdhbml6ZS5cbiAqL1xudmFyIHNhZ2VicmV3ID0gcmVxdWlyZSgnc2FnZWJyZXcnKTtcblxuLyoqXG4gKiAgU2NvcGUgLSBVc2VyIEF1dGhlZFxuICogIEFsbCB0aGluZ3MgcmVsYXRpbmcgdG8gdGhlIG5hdmJhci5cbiAqL1xuZnVuY3Rpb24gbmF2YmFyKCkge1xuICAgICQoZG9jdW1lbnQpLnJlYWR5KGZ1bmN0aW9uKCkge1xuICAgICAgICAvL1xuICAgICAgICAvLyBOb3RpZmljYXRpb25zXG4gICAgICAgIC8vIFJldHJpZXZlcyBhbGwgdGhlIG5vdGlmaWNhdGlvbnMgZm9yIGEgZ2l2ZW4gdXNlciBhbmQgZ2F0aGVycyBob3dcbiAgICAgICAgLy8gbWFueSBoYXZlIGJlZW4gc2VlbiBvciB1bnNlZW4uXG4gICAgICAgIGNvbnNvbGUubG9nKFwiTmF2YmFyIFN0YXJ0XCIpO1xuXG4gICAgICAgIHNhZ2VicmV3LnJlc291cmNlLmdldCh7dXJsOiBcIi92MS9tZS9ub3RpZmljYXRpb25zL3JlbmRlci9cIn0pLnRoZW4oZnVuY3Rpb24oZGF0YSl7XG4gICAgICAgICAgICAkKCcjbm90aWZpY2F0aW9uX3dyYXBwZXInKS5hcHBlbmQoZGF0YS5yZXN1bHRzLmh0bWwpO1xuICAgICAgICAgICAgaWYgKGRhdGEucmVzdWx0cy51bnNlZW4gPiAwKSB7XG4gICAgICAgICAgICAgICAgJCgnI2pzLW5vdGlmaWNhdGlvbl9ub3RpZmllcl93cmFwcGVyJykuYXBwZW5kKCc8c3BhbiBjbGFzcz1cIm5hdmJhci1uZXcgc2Jfbm90aWZpZXJcIiBpZD1cImpzLXNiX25vdGlmaWNhdGlvbnNfbm90aWZpZXJcIj4nICsgZGF0YS5yZXN1bHRzLnVuc2VlbiArICc8L3NwYW4+Jyk7XG4gICAgICAgICAgICB9XG4gICAgICAgIH0pO1xuXG4gICAgICAgIC8vIFNob3dzIHRoZSBub3RpZmljYXRpb25zIHdoZW4gdGhlIG5vdGlmaWNhdGlvbiBpY29uIGlzIGNsaWNrZWRcbiAgICAgICAgJChcIi5zaG93X25vdGlmaWNhdGlvbnMtYWN0aW9uXCIpLmNsaWNrKGZ1bmN0aW9uICgpIHtcbiAgICAgICAgICAgICQoXCIjbm90aWZpY2F0aW9uX2RpdlwiKS5mYWRlVG9nZ2xlKCk7XG4gICAgICAgICAgICBpZiAoJCgnI2pzLW5vdGlmaWNhdGlvbl9ub3RpZmllcl93cmFwcGVyJykuY2hpbGRyZW4oKS5sZW5ndGggPiAwKSB7XG4gICAgICAgICAgICAgICAgJC5hamF4KHtcbiAgICAgICAgICAgICAgICAgICAgeGhyRmllbGRzOiB7d2l0aENyZWRlbnRpYWxzOiB0cnVlfSxcbiAgICAgICAgICAgICAgICAgICAgdHlwZTogXCJHRVRcIixcbiAgICAgICAgICAgICAgICAgICAgdXJsOiBcIi92MS9tZS9ub3RpZmljYXRpb25zLz9zZWVuPXRydWVcIixcbiAgICAgICAgICAgICAgICAgICAgY29udGVudFR5cGU6IFwiYXBwbGljYXRpb24vanNvbjsgY2hhcnNldD11dGYtOFwiLFxuICAgICAgICAgICAgICAgICAgICBkYXRhVHlwZTogXCJqc29uXCIsXG4gICAgICAgICAgICAgICAgICAgIHN1Y2Nlc3M6IGZ1bmN0aW9uICgpIHtcbiAgICAgICAgICAgICAgICAgICAgICAgICQoJyNqcy1zYl9ub3RpZmljYXRpb25zX25vdGlmaWVyJykucmVtb3ZlKCk7XG4gICAgICAgICAgICAgICAgICAgIH0sXG4gICAgICAgICAgICAgICAgICAgIGVycm9yOiBmdW5jdGlvbiAoWE1MSHR0cFJlcXVlc3QpIHtcbiAgICAgICAgICAgICAgICAgICAgICAgIGVycm9yRGlzcGxheShYTUxIdHRwUmVxdWVzdCk7XG4gICAgICAgICAgICAgICAgICAgIH1cbiAgICAgICAgICAgICAgICB9KTtcbiAgICAgICAgICAgIH1cbiAgICAgICAgfSk7XG5cbiAgICAgICAgLy9cbiAgICAgICAgLy8gUmVwIFdhcyBWaWV3ZWQ/XG4gICAgICAgICQoXCIuc2hvdy1yZXB1dGF0aW9uLWFjdGlvblwiKS5vbihcImNsaWNrXCIsIGZ1bmN0aW9uICgpIHtcbiAgICAgICAgICAgICQuYWpheCh7XG4gICAgICAgICAgICAgICAgeGhyRmllbGRzOiB7d2l0aENyZWRlbnRpYWxzOiB0cnVlfSxcbiAgICAgICAgICAgICAgICB0eXBlOiBcIlBVVFwiLFxuICAgICAgICAgICAgICAgIHVybDogXCIvdjEvbWUvXCIsXG4gICAgICAgICAgICAgICAgY29udGVudFR5cGU6IFwiYXBwbGljYXRpb24vanNvbjsgY2hhcnNldD11dGYtOFwiLFxuICAgICAgICAgICAgICAgIGRhdGFUeXBlOiBcImpzb25cIixcbiAgICAgICAgICAgICAgICBkYXRhOiBKU09OLnN0cmluZ2lmeSh7XG4gICAgICAgICAgICAgICAgICAgIFwicmVwdXRhdGlvbl91cGRhdGVfc2VlblwiOiB0cnVlXG4gICAgICAgICAgICAgICAgfSlcbiAgICAgICAgICAgIH0pO1xuICAgICAgICB9KTtcblxuICAgICAgICAvL1xuICAgICAgICAvLyBTaG93IFJlcFxuICAgICAgICAkLmFqYXgoe1xuICAgICAgICAgICAgeGhyRmllbGRzOiB7d2l0aENyZWRlbnRpYWxzOiB0cnVlfSxcbiAgICAgICAgICAgIHR5cGU6IFwiR0VUXCIsXG4gICAgICAgICAgICB1cmw6IFwiL3YxL3Byb2ZpbGVzL1wiICsgJChcIiNyZXB1dGF0aW9uX3RvdGFsXCIpLmRhdGEoJ3VzZXJuYW1lJykgKyBcIi9yZXB1dGF0aW9uL1wiLFxuICAgICAgICAgICAgY29udGVudFR5cGU6IFwiYXBwbGljYXRpb24vanNvbjsgY2hhcnNldD11dGYtOFwiLFxuICAgICAgICAgICAgZGF0YVR5cGU6IFwianNvblwiLFxuICAgICAgICAgICAgc3VjY2VzczogZnVuY3Rpb24gKGRhdGEpIHtcbiAgICAgICAgICAgICAgICAkKFwiI3JlcHV0YXRpb25fdG90YWxcIikuYXBwZW5kKFwiPHA+XCIgKyBkYXRhW1wicmVwdXRhdGlvblwiXSArIFwiPC9wPlwiKTtcbiAgICAgICAgICAgIH0sXG4gICAgICAgICAgICBlcnJvcjogZnVuY3Rpb24oWE1MSHR0cFJlcXVlc3QsIHRleHRTdGF0dXMsIGVycm9yVGhyb3duKSB7XG4gICAgICAgICAgICAgICAgaWYoWE1MSHR0cFJlcXVlc3Quc3RhdHVzID09PSA1MDApe1xuICAgICAgICAgICAgICAgICAgICAkKFwiI3NlcnZlcl9lcnJvclwiKS5zaG93KCk7XG4gICAgICAgICAgICAgICAgfVxuICAgICAgICAgICAgfVxuICAgICAgICB9KTtcblxuICAgICAgICAvL1xuICAgICAgICAvLyBTZWFyY2hcbiAgICAgICAgJChcIi5mdWxsX3NlYXJjaC1hY3Rpb25cIikuY2xpY2soZnVuY3Rpb24oZSkge1xuICAgICAgICAgICAgdmFyIHNlYXJjaF9wYXJhbSA9ICgkKCcjc2Jfc2VhcmNoX2lucHV0JykudmFsKCkpO1xuICAgICAgICAgICAgd2luZG93LmxvY2F0aW9uLmhyZWYgPSBcIi9zZWFyY2gvP3E9XCIgKyBzZWFyY2hfcGFyYW0gKyBcIiZwYWdlPTEmZmlsdGVyPWdlbmVyYWxcIjtcbiAgICAgICAgfSk7XG4gICAgICAgICQoXCIjc2Jfc2VhcmNoX2lucHV0XCIpLmtleXVwKGZ1bmN0aW9uKGUpIHtcbiAgICAgICAgICAgIGlmKGUud2hpY2ggPT09IDEwIHx8IGUud2hpY2ggPT09IDEzKSB7XG4gICAgICAgICAgICAgICAgdmFyIHNlYXJjaF9wYXJhbSA9ICgkKCcjc2Jfc2VhcmNoX2lucHV0JykudmFsKCkpO1xuICAgICAgICAgICAgICAgIHdpbmRvdy5sb2NhdGlvbi5ocmVmID0gXCIvc2VhcmNoLz9xPVwiICsgc2VhcmNoX3BhcmFtICsgXCImcGFnZT0xJmZpbHRlcj1nZW5lcmFsXCI7XG4gICAgICAgICAgICB9XG4gICAgICAgIH0pO1xuXG4gICAgICAgIC8vXG4gICAgICAgIC8vXG5cbiAgICAgICAgLy9cbiAgICAgICAgLy8gRnJpZW5kc1xuICAgICAgICAvLyBSZXRyaWV2ZXMgYWxsIHRoZSBmcmllbmQgcmVxdWVzdHMgZm9yIGEgZ2l2ZW4gdXNlciBhbmQgZ2F0aGVycyBob3dcbiAgICAgICAgLy8gbWFueSBoYXZlIGJlZW4gc2VlbiBvciB1bnNlZW4uXG4gICAgICAgICQuYWpheCh7XG4gICAgICAgICAgICB4aHJGaWVsZHM6IHt3aXRoQ3JlZGVudGlhbHM6IHRydWV9LFxuICAgICAgICAgICAgdHlwZTogXCJHRVRcIixcbiAgICAgICAgICAgIHVybDogXCIvdjEvbWUvZnJpZW5kX3JlcXVlc3RzL3JlbmRlci9cIixcbiAgICAgICAgICAgIGNvbnRlbnRUeXBlOiBcImFwcGxpY2F0aW9uL2pzb247IGNoYXJzZXQ9dXRmLThcIixcbiAgICAgICAgICAgIGRhdGFUeXBlOiBcImpzb25cIixcbiAgICAgICAgICAgIHN1Y2Nlc3M6IGZ1bmN0aW9uIChkYXRhKSB7XG4gICAgICAgICAgICAgICAgJCgnI2ZyaWVuZF9yZXF1ZXN0X3dyYXBwZXInKS5hcHBlbmQoZGF0YS5yZXN1bHRzLmh0bWwpO1xuICAgICAgICAgICAgICAgIGlmIChkYXRhLnJlc3VsdHMudW5zZWVuID4gMCkge1xuICAgICAgICAgICAgICAgICAgICAkKCcjanMtZnJpZW5kX3JlcXVlc3Rfbm90aWZpZXJfd3JhcHBlcicpLmFwcGVuZCgnPHNwYW4gY2xhc3M9XCJuYXZiYXItbmV3IHNiX25vdGlmaWVyXCIgaWQ9XCJqcy1zYl9mcmllbmRfcmVxdWVzdF9ub3RpZmllclwiPicgKyBkYXRhLnJlc3VsdHMudW5zZWVuICsgJzwvc3Bhbj4nKTtcbiAgICAgICAgICAgICAgICB9XG4gICAgICAgICAgICB9LFxuICAgICAgICAgICAgZXJyb3I6IGZ1bmN0aW9uIChYTUxIdHRwUmVxdWVzdCkge1xuICAgICAgICAgICAgICAgIGlmIChYTUxIdHRwUmVxdWVzdC5zdGF0dXMgPT09IDUwMCkge1xuICAgICAgICAgICAgICAgICAgICAkKFwiI3NlcnZlcl9lcnJvclwiKS5zaG93KCk7XG4gICAgICAgICAgICAgICAgfVxuICAgICAgICAgICAgfVxuICAgICAgICB9KTtcblxuICAgICAgICAvLyBTaG93cyB0aGUgZnJpZW5kIHJlcXVlc3RzIHdoZW4gdGhlIGZyaWVuZCByZXF1ZXN0IGljb24gaXMgY2xpY2tlZFxuICAgICAgICAkKFwiLnNob3dfZnJpZW5kX3JlcXVlc3QtYWN0aW9uXCIpLmNsaWNrKGZ1bmN0aW9uICgpIHtcbiAgICAgICAgICAgICQoXCIjZnJpZW5kX3JlcXVlc3RfZGl2XCIpLmZhZGVUb2dnbGUoKTtcbiAgICAgICAgICAgIGlmICgkKCcjanMtc2JfZnJpZW5kX3JlcXVlc3Rfbm90aWZpZXInKS5sZW5ndGggPiAwKSB7XG4gICAgICAgICAgICAgICAgJC5hamF4KHtcbiAgICAgICAgICAgICAgICAgICAgeGhyRmllbGRzOiB7d2l0aENyZWRlbnRpYWxzOiB0cnVlfSxcbiAgICAgICAgICAgICAgICAgICAgdHlwZTogXCJHRVRcIixcbiAgICAgICAgICAgICAgICAgICAgdXJsOiBcIi92MS9tZS9mcmllbmRfcmVxdWVzdHMvP3NlZW49dHJ1ZVwiLFxuICAgICAgICAgICAgICAgICAgICBjb250ZW50VHlwZTogXCJhcHBsaWNhdGlvbi9qc29uOyBjaGFyc2V0PXV0Zi04XCIsXG4gICAgICAgICAgICAgICAgICAgIGRhdGFUeXBlOiBcImpzb25cIixcbiAgICAgICAgICAgICAgICAgICAgc3VjY2VzczogZnVuY3Rpb24gKCkge1xuICAgICAgICAgICAgICAgICAgICAgICAgJCgnI2pzLXNiX2ZyaWVuZF9yZXF1ZXN0X25vdGlmaWVyJykucmVtb3ZlKCk7XG4gICAgICAgICAgICAgICAgICAgIH0sXG4gICAgICAgICAgICAgICAgICAgIGVycm9yOiBmdW5jdGlvbiAoKSB7XG4gICAgICAgICAgICAgICAgICAgICAgICAkKFwiI3NlcnZlcl9lcnJvclwiKS5zaG93KCk7XG4gICAgICAgICAgICAgICAgICAgIH1cbiAgICAgICAgICAgICAgICB9KTtcbiAgICAgICAgICAgIH1cbiAgICAgICAgICAgICQoXCIucmVzcG9uZF9mcmllbmRfcmVxdWVzdC1hY2NlcHQtYWN0aW9uXCIpLmNsaWNrKGZ1bmN0aW9uIChldmVudCkge1xuICAgICAgICAgICAgICAgIGV2ZW50LnByZXZlbnREZWZhdWx0KCk7XG4gICAgICAgICAgICAgICAgdmFyIHJlcXVlc3RJRCA9ICQodGhpcykuZGF0YSgncmVxdWVzdF9pZCcpO1xuICAgICAgICAgICAgICAgICQuYWpheCh7XG4gICAgICAgICAgICAgICAgICAgIHhockZpZWxkczoge3dpdGhDcmVkZW50aWFsczogdHJ1ZX0sXG4gICAgICAgICAgICAgICAgICAgIHR5cGU6IFwiUE9TVFwiLFxuICAgICAgICAgICAgICAgICAgICB1cmw6IFwiL3YxL21lL2ZyaWVuZF9yZXF1ZXN0cy9cIiArIHJlcXVlc3RJRCArIFwiL2FjY2VwdC9cIixcbiAgICAgICAgICAgICAgICAgICAgZGF0YTogSlNPTi5zdHJpbmdpZnkoe1xuICAgICAgICAgICAgICAgICAgICAgICAgJ3JlcXVlc3RfaWQnOiByZXF1ZXN0SURcbiAgICAgICAgICAgICAgICAgICAgfSksXG4gICAgICAgICAgICAgICAgICAgIGNvbnRlbnRUeXBlOiBcImFwcGxpY2F0aW9uL2pzb247IGNoYXJzZXQ9dXRmLThcIixcbiAgICAgICAgICAgICAgICAgICAgZGF0YVR5cGU6IFwianNvblwiLFxuICAgICAgICAgICAgICAgICAgICBzdWNjZXNzOiBmdW5jdGlvbiAoKSB7XG4gICAgICAgICAgICAgICAgICAgICAgICAkKCcjZnJpZW5kX3JlcXVlc3RfJyArIHJlcXVlc3RJRCkucmVtb3ZlKCk7XG4gICAgICAgICAgICAgICAgICAgIH0sXG4gICAgICAgICAgICAgICAgICAgIGVycm9yOiBmdW5jdGlvbiAoWE1MSHR0cFJlcXVlc3QpIHtcbiAgICAgICAgICAgICAgICAgICAgICAgIGlmIChYTUxIdHRwUmVxdWVzdC5zdGF0dXMgPT09IDUwMCkge1xuICAgICAgICAgICAgICAgICAgICAgICAgICAgICQoXCIjc2VydmVyX2Vycm9yXCIpLnNob3coKTtcbiAgICAgICAgICAgICAgICAgICAgICAgIH1cbiAgICAgICAgICAgICAgICAgICAgfVxuICAgICAgICAgICAgICAgIH0pO1xuICAgICAgICAgICAgfSk7XG4gICAgICAgICAgICAkKFwiLnJlc3BvbmRfZnJpZW5kX3JlcXVlc3QtZGVjbGluZS1hY3Rpb25cIikuY2xpY2soZnVuY3Rpb24gKGV2ZW50KSB7XG4gICAgICAgICAgICAgICAgZXZlbnQucHJldmVudERlZmF1bHQoKTtcbiAgICAgICAgICAgICAgICB2YXIgcmVxdWVzdElEID0gJCh0aGlzKS5kYXRhKCdyZXF1ZXN0X2lkJyk7XG4gICAgICAgICAgICAgICAgJC5hamF4KHtcbiAgICAgICAgICAgICAgICAgICAgeGhyRmllbGRzOiB7d2l0aENyZWRlbnRpYWxzOiB0cnVlfSxcbiAgICAgICAgICAgICAgICAgICAgdHlwZTogXCJQT1NUXCIsXG4gICAgICAgICAgICAgICAgICAgIHVybDogXCIvdjEvbWUvZnJpZW5kX3JlcXVlc3RzL1wiICsgcmVxdWVzdElEICsgXCIvZGVjbGluZS9cIixcbiAgICAgICAgICAgICAgICAgICAgZGF0YTogSlNPTi5zdHJpbmdpZnkoe1xuICAgICAgICAgICAgICAgICAgICAgICAgJ3JlcXVlc3RfaWQnOiByZXF1ZXN0SURcbiAgICAgICAgICAgICAgICAgICAgfSksXG4gICAgICAgICAgICAgICAgICAgIGNvbnRlbnRUeXBlOiBcImFwcGxpY2F0aW9uL2pzb247IGNoYXJzZXQ9dXRmLThcIixcbiAgICAgICAgICAgICAgICAgICAgZGF0YVR5cGU6IFwianNvblwiLFxuICAgICAgICAgICAgICAgICAgICBzdWNjZXNzOiBmdW5jdGlvbiAoKSB7XG4gICAgICAgICAgICAgICAgICAgICAgICAkKCcjZnJpZW5kX3JlcXVlc3RfJyArIHJlcXVlc3RJRCkucmVtb3ZlKCk7XG4gICAgICAgICAgICAgICAgICAgIH0sXG4gICAgICAgICAgICAgICAgICAgIGVycm9yOiBmdW5jdGlvbiAoWE1MSHR0cFJlcXVlc3QpIHtcbiAgICAgICAgICAgICAgICAgICAgICAgIGlmIChYTUxIdHRwUmVxdWVzdC5zdGF0dXMgPT09IDUwMCkge1xuICAgICAgICAgICAgICAgICAgICAgICAgICAgICQoXCIjc2VydmVyX2Vycm9yXCIpLnNob3coKTtcbiAgICAgICAgICAgICAgICAgICAgICAgIH1cbiAgICAgICAgICAgICAgICAgICAgfVxuICAgICAgICAgICAgICAgIH0pO1xuICAgICAgICAgICAgfSk7XG4gICAgICAgICAgICAkKFwiLnJlc3BvbmRfZnJpZW5kX3JlcXVlc3QtYmxvY2stYWN0aW9uXCIpLmNsaWNrKGZ1bmN0aW9uIChldmVudCkge1xuICAgICAgICAgICAgICAgIGV2ZW50LnByZXZlbnREZWZhdWx0KCk7XG4gICAgICAgICAgICAgICAgdmFyIHJlcXVlc3RJRCA9ICQodGhpcykuZGF0YSgncmVxdWVzdF9pZCcpO1xuICAgICAgICAgICAgICAgICQuYWpheCh7XG4gICAgICAgICAgICAgICAgICAgIHhockZpZWxkczoge3dpdGhDcmVkZW50aWFsczogdHJ1ZX0sXG4gICAgICAgICAgICAgICAgICAgIHR5cGU6IFwiUE9TVFwiLFxuICAgICAgICAgICAgICAgICAgICB1cmw6IFwiL3YxL21lL2ZyaWVuZF9yZXF1ZXN0cy9cIiArIHJlcXVlc3RJRCArIFwiL2Jsb2NrL1wiLFxuICAgICAgICAgICAgICAgICAgICBkYXRhOiBKU09OLnN0cmluZ2lmeSh7XG4gICAgICAgICAgICAgICAgICAgICAgICAncmVxdWVzdF9pZCc6IHJlcXVlc3RJRFxuICAgICAgICAgICAgICAgICAgICB9KSxcbiAgICAgICAgICAgICAgICAgICAgY29udGVudFR5cGU6IFwiYXBwbGljYXRpb24vanNvbjsgY2hhcnNldD11dGYtOFwiLFxuICAgICAgICAgICAgICAgICAgICBkYXRhVHlwZTogXCJqc29uXCIsXG4gICAgICAgICAgICAgICAgICAgIHN1Y2Nlc3M6IGZ1bmN0aW9uICgpIHtcbiAgICAgICAgICAgICAgICAgICAgICAgICQoJyNmcmllbmRfcmVxdWVzdF8nICsgcmVxdWVzdElEKS5yZW1vdmUoKTtcbiAgICAgICAgICAgICAgICAgICAgfSxcbiAgICAgICAgICAgICAgICAgICAgZXJyb3I6IGZ1bmN0aW9uIChYTUxIdHRwUmVxdWVzdCkge1xuICAgICAgICAgICAgICAgICAgICAgICAgaWYgKFhNTEh0dHBSZXF1ZXN0LnN0YXR1cyA9PT0gNTAwKSB7XG4gICAgICAgICAgICAgICAgICAgICAgICAgICAgJChcIiNzZXJ2ZXJfZXJyb3JcIikuc2hvdygpO1xuICAgICAgICAgICAgICAgICAgICAgICAgfVxuICAgICAgICAgICAgICAgICAgICB9XG4gICAgICAgICAgICAgICAgfSk7XG4gICAgICAgICAgICB9KTtcbiAgICAgICAgfSk7XG4gICAgfSk7XG59XG5cbmV4cG9ydCBmdW5jdGlvbiBpbml0TmF2YmFyKCkge1xuICAgIHJldHVybiBuYXZiYXIoKTtcbn0iLCIvKipcbiAqIEBmaWxlXG4gKiBIZWxwZXIgZnVuY3Rpb25zIHRoYXQgYXJlbid0IGdsb2JhbC5cbiAqL1xuXG4vKipcbiAqIEdldCBjb29raWUgYmFzZWQgYnkgbmFtZS5cbiAqIEBwYXJhbSBuYW1lXG4gKiBAcmV0dXJucyB7Kn1cbiAqL1xuZXhwb3J0IGZ1bmN0aW9uIGdldENvb2tpZShuYW1lKSB7XG4gICAgdmFyIGNvb2tpZVZhbHVlID0gbnVsbDtcbiAgICBpZiAoZG9jdW1lbnQuY29va2llICYmIGRvY3VtZW50LmNvb2tpZSAhPT0gXCJcIikge1xuICAgICAgICB2YXIgY29va2llcyA9IGRvY3VtZW50LmNvb2tpZS5zcGxpdCgnOycpO1xuICAgICAgICBmb3IgKHZhciBpID0gMDsgaSA8IGNvb2tpZXMubGVuZ3RoOyBpICs9IDEpIHtcbiAgICAgICAgICAgIHZhciBjb29raWUgPSAkLnRyaW0oY29va2llc1tpXSk7XG4gICAgICAgICAgICAvLyBEb2VzIHRoaXMgY29va2llIHN0cmluZyBiZWdpbiB3aXRoIHRoZSBuYW1lIHdlIHdhbnQ/XG5cbiAgICAgICAgICAgIGlmIChjb29raWUuc3Vic3RyaW5nKDAsIG5hbWUubGVuZ3RoICsgMSkgPT09IChuYW1lICsgJz0nKSkge1xuICAgICAgICAgICAgICAgIGNvb2tpZVZhbHVlID0gZGVjb2RlVVJJQ29tcG9uZW50KGNvb2tpZS5zdWJzdHJpbmcobmFtZS5sZW5ndGggKyAxKSk7XG4gICAgICAgICAgICAgICAgYnJlYWs7XG4gICAgICAgICAgICB9XG4gICAgICAgIH1cbiAgICB9XG4gICAgcmV0dXJuIGNvb2tpZVZhbHVlO1xufVxuXG4vKipcbiAqIENoZWNrIGlmIEhUVFAgbWV0aG9kIHJlcXVpcmVzIENTUkYuXG4gKiBAcGFyYW0gbWV0aG9kXG4gKiBAcmV0dXJucyB7Ym9vbGVhbn1cbiAqL1xuZXhwb3J0IGZ1bmN0aW9uIGNzcmZTYWZlTWV0aG9kKG1ldGhvZCkge1xuICAgIC8vIHRoZXNlIEhUVFAgbWV0aG9kcyBkbyBub3QgcmVxdWlyZSBDU1JGIHByb3RlY3Rpb25cbiAgICByZXR1cm4gKC9eKEdFVHxIRUFEfE9QVElPTlN8VFJBQ0UpJC8udGVzdChtZXRob2QpKTtcbn0iLCIvKipcbiAqIEBmaWxlXG4gKiBJbml0IHRoZSBTQiB3ZWJzaXRlLlxuICogZ2xvYmFsSW5pdCAtIFJ1bnMgb24gYWxsIHBhZ2VzLlxuICogVXNlckF1dGhlZEluaXQgLSBSdW5zIG9uIGF1dGhlZCBwYWdlcy5cbiAqIHVzZXJBbm9uSW5pdCAtIFJ1bnMgb24gYW5vbiBwYWdlcy5cbiAqIFRPRE86IFRoZSBpbmRpdmlkdWFsIGluaXQgZnVuY3Rpb25zIGNvdWxkIGJlIHR1cm5lZCBpbnRvIGFycmF5cyBvciBvYmplY3RzIGFuZCB0aGVuXG4gKiBsb29wZWQgb3Zlci5cbiAqL1xudmFyIGhlbHBlcnMgPSByZXF1aXJlKCcuL2hlbHBlcnMnKTtcblxuLyoqXG4gKiBTY29wZSAtIEdsb2JhbFxuICogQWpheCBTZXR1cFxuICogLS0gQXV0b21hdGljYWxseSBhZGQgQ1NSRiBjb29raWUgdmFsdWUgdG8gYWxsIGFqYXggcmVxdWVzdHMuXG4gKi9cbmZ1bmN0aW9uIGFqYXhTZXR1cCgpIHtcbiAgICAkLmFqYXhTZXR1cCh7XG4gICAgICAgIGJlZm9yZVNlbmQ6IGZ1bmN0aW9uICh4aHIsIHNldHRpbmdzKSB7XG4gICAgICAgICAgICBpZiAoIWhlbHBlcnMuY3NyZlNhZmVNZXRob2Qoc2V0dGluZ3MudHlwZSkgJiYgIXRoaXMuY3Jvc3NEb21haW4pIHtcbiAgICAgICAgICAgICAgICB4aHIuc2V0UmVxdWVzdEhlYWRlcihcIlgtQ1NSRlRva2VuXCIsIGhlbHBlcnMuZ2V0Q29va2llKCdjc3JmdG9rZW4nKSk7XG4gICAgICAgICAgICB9XG4gICAgICAgIH1cbiAgICB9KTtcbn1cblxuLyoqXG4gKiAgU2NvcGUgLSBVc2VyIEF1dGhlZFxuICogIEFkZHMgYW4gZXZlbnQgaGFuZGxlciB0byBwYWdlIHVubG9hZCB0aGF0IGFqYXggcG9zdHMgYWxsIHRoZSB1c2VyJ3MgYWN0aW9ucyB0aGF0IG9jY3VyZWQgZHVyaW5nIHRoZSBwYWdlLlxuICogIFRPRE86IFN0b3AgZG9pbmcgdGhpcy5cbiAqICBOb3Qgb25seSBhcmUgbm9uLWFzeW5jIGFqYXggY2FsbHMgZGVwcmVjYXRlZCBpdCBob2xkcyB0aGUgcGFnZSBsb2FkIHVwIGZvciB0aGUgdXNlci5cbiAqICBUaGV5IGNhbid0IGV2ZW4gc3RhcnQgbG9hZGluZyB0aGUgbmV4dCBwYWdlIHVudGlsIHRoaXMgaXMgY29tcGxldGVkLlxuICovXG5mdW5jdGlvbiBjb2xsZWN0QXV0aGVkQWN0aW9ucygpIHtcbiAgICAkKGRvY3VtZW50KS5yZWFkeShmdW5jdGlvbiAoKSB7XG4gICAgICAgIFwidXNlIHN0cmljdFwiO1xuICAgICAgICB3aW5kb3cub25iZWZvcmV1bmxvYWQgPSBmdW5jdGlvbiAoKSB7XG4gICAgICAgICAgICB2YXIgb2JqZWN0TGlzdCA9IFtdO1xuICAgICAgICAgICAgJChcIi5qcy1wYWdlLW9iamVjdFwiKS5lYWNoKGZ1bmN0aW9uICgpIHtcbiAgICAgICAgICAgICAgICBvYmplY3RMaXN0LnB1c2goJCh0aGlzKS5kYXRhKCdvYmplY3RfdXVpZCcpKTtcbiAgICAgICAgICAgIH0pO1xuICAgICAgICAgICAgaWYgKG9iamVjdExpc3QubGVuZ3RoKSB7XG4gICAgICAgICAgICAgICAgJC5hamF4KHtcbiAgICAgICAgICAgICAgICAgICAgeGhyRmllbGRzOiB7d2l0aENyZWRlbnRpYWxzOiB0cnVlfSxcbiAgICAgICAgICAgICAgICAgICAgdHlwZTogXCJQT1NUXCIsXG4gICAgICAgICAgICAgICAgICAgIGFzeW5jOiBmYWxzZSxcbiAgICAgICAgICAgICAgICAgICAgdXJsOiBcIi9kb2NzdG9yZS91cGRhdGVfbmVvX2FwaS9cIixcbiAgICAgICAgICAgICAgICAgICAgZGF0YTogSlNPTi5zdHJpbmdpZnkoe1xuICAgICAgICAgICAgICAgICAgICAgICAgJ29iamVjdF91dWlkcyc6IG9iamVjdExpc3RcbiAgICAgICAgICAgICAgICAgICAgfSksXG4gICAgICAgICAgICAgICAgICAgIGNvbnRlbnRUeXBlOiBcImFwcGxpY2F0aW9uL2pzb247IGNoYXJzZXQ9dXRmLThcIixcbiAgICAgICAgICAgICAgICAgICAgZGF0YVR5cGU6IFwianNvblwiLFxuICAgICAgICAgICAgICAgICAgICBlcnJvcjogZnVuY3Rpb24gKFhNTEh0dHBSZXF1ZXN0KSB7XG4gICAgICAgICAgICAgICAgICAgICAgICBpZiAoWE1MSHR0cFJlcXVlc3Quc3RhdHVzID09PSA1MDApIHtcbiAgICAgICAgICAgICAgICAgICAgICAgICAgICAkKFwiI3NlcnZlcl9lcnJvclwiKS5zaG93KCk7XG4gICAgICAgICAgICAgICAgICAgICAgICB9XG4gICAgICAgICAgICAgICAgICAgIH1cbiAgICAgICAgICAgICAgICB9KTtcbiAgICAgICAgICAgIH1cbiAgICAgICAgfTtcbiAgICB9KTtcbn1cblxuXG5cbi8qKlxuICogVGhpcyBmdW5jdGlvbiBpcyBjYWxsZWQgaW4gc2FnZWJyZXcuanMgbWFpbiBmaWxlLlxuICogRWFjaCBpbml0IHRhc2sgc2hvdWxkIGJlIGRlZmluZWQgaW4gaXQncyBvd24gZnVuY3Rpb24gZm9yIHdoYXRldmVyIHJlYXNvbi5cbiAqIC0tIEJldHRlciBjb2RlIHJlYWRhYmlsaXR5P1xuICovXG5leHBvcnQgZnVuY3Rpb24gZ2xvYmFsSW5pdCgpIHtcbiAgICBjb25zb2xlLmxvZyhcIkdsb2JhbCBJbml0IFN0YXJ0XCIpO1xuICAgIGFqYXhTZXR1cCgpO1xuICAgIGNvbnNvbGUubG9nKFwiR2xvYmFsIEluaXQgU3RvcFwiKTtcbn1cblxuLyoqXG4gKiBBdXRoIEluaXQuXG4gKi9cbmV4cG9ydCBmdW5jdGlvbiB1c2VyQXV0aGVkSW5pdCgpIHtcbiAgICBjb25zb2xlLmxvZyhcInVzZXJBdXRoZWRJbml0IFN0YXJ0XCIpO1xuICAgIGNvbGxlY3RBdXRoZWRBY3Rpb25zKCk7XG4gICAgY29uc29sZS5sb2coXCJ1c2VyQXV0aGVkSW5pdCBTdG9wXCIpO1xufVxuXG4vKipcbiAqIEFub24gSW5pdC5cbiAqL1xuZXhwb3J0IGZ1bmN0aW9uIHVzZXJBbm9uSW5pdCgpIHtcbiAgICBjb25zb2xlLmxvZyhcInVzZXJBbm9uSW5pdCBTdGFydFwiKTtcbiAgICBjb25zb2xlLmxvZyhcInVzZXJBbm9uSW5pdCBTdG9wXCIpO1xufVxuXG5cblxuXG4iLCIvKipcbiAqIEBmaWxlXG4gKiBVc2VkIG9uIGV2ZXJ5IHBhZ2Ugd2l0aCBhbiBhdXRoZWQgdXNlci5cbiAqL1xuXG52YXIgdXNlckF1dGhlZEluaXQgPSByZXF1aXJlKCcuL2NvbXBvbmVudHMvaW5pdCcpLnVzZXJBdXRoZWRJbml0O1xudmFyIG5hdmJhciA9IHJlcXVpcmUoJy4vY29tcG9uZW50cy9hdXRoZWQvbmF2YmFyJykuaW5pdE5hdmJhcjtcblxuLy8gSW5pdCB2YXJpb3VzIHRoaW5ncyBmb3IgYXV0aGVkIHVzZXIuXG51c2VyQXV0aGVkSW5pdCgpO1xubmF2YmFyKCk7Il19
