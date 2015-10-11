require=(function e(t,n,r){function s(o,u){if(!n[o]){if(!t[o]){var a=typeof require=="function"&&require;if(!u&&a)return a(o,!0);if(i)return i(o,!0);var f=new Error("Cannot find module '"+o+"'");throw f.code="MODULE_NOT_FOUND",f}var l=n[o]={exports:{}};t[o][0].call(l.exports,function(e){var n=t[o][1][e];return s(n?n:e)},l,l.exports,e,t,n,r)}return n[o].exports}var i=typeof require=="function"&&require;for(var o=0;o<r.length;o++)s(r[o]);return s})({1:[function(require,module,exports){
/**
 * @file
 * All the functionality for the navbar.
 * TODO: Reorganize.
 */

/**
 *  Scope - User Authed
 *  All things relating to the navbar.
 */
"use strict";

Object.defineProperty(exports, "__esModule", {
    value: true
});
exports.initNavbar = initNavbar;
function navbar() {
    $(document).ready(function () {
        //
        // Notifications
        // Retrieves all the notifications for a given user and gathers how
        // many have been seen or unseen.
        $.ajax({
            xhrFields: { withCredentials: true },
            type: "GET",
            url: "/v1/me/notifications/render/",
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function success(data) {
                $('#notification_wrapper').append(data.results.html);
                if (data.results.unseen > 0) {
                    $('#js-notification_notifier_wrapper').append('<span class="navbar-new sb_notifier" id="js-sb_notifications_notifier">' + data.results.unseen + '</span>');
                }
            },
            error: function error(XMLHttpRequest) {
                errorDisplay(XMLHttpRequest);
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
//# sourceMappingURL=data:application/json;charset:utf-8;base64,eyJ2ZXJzaW9uIjozLCJzb3VyY2VzIjpbIm5vZGVfbW9kdWxlcy9icm93c2VyaWZ5L25vZGVfbW9kdWxlcy9icm93c2VyLXBhY2svX3ByZWx1ZGUuanMiLCIvVXNlcnMvbXdpc25lci9Qcm9qZWN0cy9zYWdlYnJldy9jb20uc2FnZWJyZXcud2ViL3NhZ2VicmV3L3NhZ2VicmV3L3N0YXRpYy9qcy9zcmMvY29tcG9uZW50cy9hdXRoZWQvbmF2YmFyLmpzIiwiL1VzZXJzL213aXNuZXIvUHJvamVjdHMvc2FnZWJyZXcvY29tLnNhZ2VicmV3LndlYi9zYWdlYnJldy9zYWdlYnJldy9zdGF0aWMvanMvc3JjL2NvbXBvbmVudHMvaGVscGVycy5qcyIsIi9Vc2Vycy9td2lzbmVyL1Byb2plY3RzL3NhZ2VicmV3L2NvbS5zYWdlYnJldy53ZWIvc2FnZWJyZXcvc2FnZWJyZXcvc3RhdGljL2pzL3NyYy9jb21wb25lbnRzL2luaXQuanMiLCIvVXNlcnMvbXdpc25lci9Qcm9qZWN0cy9zYWdlYnJldy9jb20uc2FnZWJyZXcud2ViL3NhZ2VicmV3L3NhZ2VicmV3L3N0YXRpYy9qcy9zcmMvdXNlci1hdXRoZWQuanMiXSwibmFtZXMiOltdLCJtYXBwaW5ncyI6IkFBQUE7Ozs7Ozs7Ozs7Ozs7Ozs7O0FDV0EsU0FBUyxNQUFNLEdBQUc7QUFDZCxLQUFDLENBQUMsUUFBUSxDQUFDLENBQUMsS0FBSyxDQUFDLFlBQVc7Ozs7O0FBS3pCLFNBQUMsQ0FBQyxJQUFJLENBQUM7QUFDSCxxQkFBUyxFQUFFLEVBQUMsZUFBZSxFQUFFLElBQUksRUFBQztBQUNsQyxnQkFBSSxFQUFFLEtBQUs7QUFDWCxlQUFHLEVBQUUsOEJBQThCO0FBQ25DLHVCQUFXLEVBQUUsaUNBQWlDO0FBQzlDLG9CQUFRLEVBQUUsTUFBTTtBQUNoQixtQkFBTyxFQUFFLGlCQUFVLElBQUksRUFBRTtBQUNyQixpQkFBQyxDQUFDLHVCQUF1QixDQUFDLENBQUMsTUFBTSxDQUFDLElBQUksQ0FBQyxPQUFPLENBQUMsSUFBSSxDQUFDLENBQUM7QUFDckQsb0JB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Q0FBQyxDQUFDO0NBQ25DOzs7Ozs7QUFLTSxTQUFTLGNBQWMsR0FBRztBQUM3QixXQUFPLENBQUMsR0FBRyxDQUFDLHNCQUFzQixDQUFDLENBQUM7QUFDcEMsd0JBQW9CLEVBQUUsQ0FBQztBQUN2QixXQUFPLENBQUMsR0FBRyxDQUFDLHFCQUFxQixDQUFDLENBQUM7Q0FDdEM7Ozs7OztBQUtNLFNBQVMsWUFBWSxHQUFHO0FBQzNCLFdBQU8sQ0FBQyxHQUFHLENBQUMsb0JBQW9CLENBQUMsQ0FBQztBQUNsQyxXQUFPLENBQUMsR0FBRyxDQUFDLG1CQUFtQixDQUFDLENBQUM7Q0FDcEM7Ozs7Ozs7Ozs7QUN0RkQsSUFBSSxjQUFjLEdBQUcsT0FBTyxDQUFDLG1CQUFtQixDQUFDLENBQUMsY0FBYyxDQUFDO0FBQ2pFLElBQUksTUFBTSxHQUFHLE9BQU8sQ0FBQyw0QkFBNEIsQ0FBQyxDQUFDLFVBQVUsQ0FBQzs7O0FBRzlELGNBQWMsRUFBRSxDQUFDO0FBQ2pCLE1BQU0sRUFBRSxDQUFDIiwiZmlsZSI6ImdlbmVyYXRlZC5qcyIsInNvdXJjZVJvb3QiOiIiLCJzb3VyY2VzQ29udGVudCI6WyIoZnVuY3Rpb24gZSh0LG4scil7ZnVuY3Rpb24gcyhvLHUpe2lmKCFuW29dKXtpZighdFtvXSl7dmFyIGE9dHlwZW9mIHJlcXVpcmU9PVwiZnVuY3Rpb25cIiYmcmVxdWlyZTtpZighdSYmYSlyZXR1cm4gYShvLCEwKTtpZihpKXJldHVybiBpKG8sITApO3ZhciBmPW5ldyBFcnJvcihcIkNhbm5vdCBmaW5kIG1vZHVsZSAnXCIrbytcIidcIik7dGhyb3cgZi5jb2RlPVwiTU9EVUxFX05PVF9GT1VORFwiLGZ9dmFyIGw9bltvXT17ZXhwb3J0czp7fX07dFtvXVswXS5jYWxsKGwuZXhwb3J0cyxmdW5jdGlvbihlKXt2YXIgbj10W29dWzFdW2VdO3JldHVybiBzKG4/bjplKX0sbCxsLmV4cG9ydHMsZSx0LG4scil9cmV0dXJuIG5bb10uZXhwb3J0c312YXIgaT10eXBlb2YgcmVxdWlyZT09XCJmdW5jdGlvblwiJiZyZXF1aXJlO2Zvcih2YXIgbz0wO288ci5sZW5ndGg7bysrKXMocltvXSk7cmV0dXJuIHN9KSIsIi8qKlxuICogQGZpbGVcbiAqIEFsbCB0aGUgZnVuY3Rpb25hbGl0eSBmb3IgdGhlIG5hdmJhci5cbiAqIFRPRE86IFJlb3JnYW5pemUuXG4gKi9cblxuXG4vKipcbiAqICBTY29wZSAtIFVzZXIgQXV0aGVkXG4gKiAgQWxsIHRoaW5ncyByZWxhdGluZyB0byB0aGUgbmF2YmFyLlxuICovXG5mdW5jdGlvbiBuYXZiYXIoKSB7XG4gICAgJChkb2N1bWVudCkucmVhZHkoZnVuY3Rpb24oKSB7XG4gICAgICAgIC8vXG4gICAgICAgIC8vIE5vdGlmaWNhdGlvbnNcbiAgICAgICAgLy8gUmV0cmlldmVzIGFsbCB0aGUgbm90aWZpY2F0aW9ucyBmb3IgYSBnaXZlbiB1c2VyIGFuZCBnYXRoZXJzIGhvd1xuICAgICAgICAvLyBtYW55IGhhdmUgYmVlbiBzZWVuIG9yIHVuc2Vlbi5cbiAgICAgICAgJC5hamF4KHtcbiAgICAgICAgICAgIHhockZpZWxkczoge3dpdGhDcmVkZW50aWFsczogdHJ1ZX0sXG4gICAgICAgICAgICB0eXBlOiBcIkdFVFwiLFxuICAgICAgICAgICAgdXJsOiBcIi92MS9tZS9ub3RpZmljYXRpb25zL3JlbmRlci9cIixcbiAgICAgICAgICAgIGNvbnRlbnRUeXBlOiBcImFwcGxpY2F0aW9uL2pzb247IGNoYXJzZXQ9dXRmLThcIixcbiAgICAgICAgICAgIGRhdGFUeXBlOiBcImpzb25cIixcbiAgICAgICAgICAgIHN1Y2Nlc3M6IGZ1bmN0aW9uIChkYXRhKSB7XG4gICAgICAgICAgICAgICAgJCgnI25vdGlmaWNhdGlvbl93cmFwcGVyJykuYXBwZW5kKGRhdGEucmVzdWx0cy5odG1sKTtcbiAgICAgICAgICAgICAgICBpZiAoZGF0YS5yZXN1bHRzLnVuc2VlbiA+IDApIHtcbiAgICAgICAgICAgICAgICAgICAgJCgnI2pzLW5vdGlmaWNhdGlvbl9ub3RpZmllcl93cmFwcGVyJykuYXBwZW5kKCc8c3BhbiBjbGFzcz1cIm5hdmJhci1uZXcgc2Jfbm90aWZpZXJcIiBpZD1cImpzLXNiX25vdGlmaWNhdGlvbnNfbm90aWZpZXJcIj4nICsgZGF0YS5yZXN1bHRzLnVuc2VlbiArICc8L3NwYW4+Jyk7XG4gICAgICAgICAgICAgICAgfVxuICAgICAgICAgICAgfSxcbiAgICAgICAgICAgIGVycm9yOiBmdW5jdGlvbiAoWE1MSHR0cFJlcXVlc3QpIHtcbiAgICAgICAgICAgICAgICBlcnJvckRpc3BsYXkoWE1MSHR0cFJlcXVlc3QpO1xuICAgICAgICAgICAgfVxuICAgICAgICB9KTtcblxuICAgICAgICAvLyBTaG93cyB0aGUgbm90aWZpY2F0aW9ucyB3aGVuIHRoZSBub3RpZmljYXRpb24gaWNvbiBpcyBjbGlja2VkXG4gICAgICAgICQoXCIuc2hvd19ub3RpZmljYXRpb25zLWFjdGlvblwiKS5jbGljayhmdW5jdGlvbiAoKSB7XG4gICAgICAgICAgICAkKFwiI25vdGlmaWNhdGlvbl9kaXZcIikuZmFkZVRvZ2dsZSgpO1xuICAgICAgICAgICAgaWYgKCQoJyNqcy1ub3RpZmljYXRpb25fbm90aWZpZXJfd3JhcHBlcicpLmNoaWxkcmVuKCkubGVuZ3RoID4gMCkge1xuICAgICAgICAgICAgICAgICQuYWpheCh7XG4gICAgICAgICAgICAgICAgICAgIHhockZpZWxkczoge3dpdGhDcmVkZW50aWFsczogdHJ1ZX0sXG4gICAgICAgICAgICAgICAgICAgIHR5cGU6IFwiR0VUXCIsXG4gICAgICAgICAgICAgICAgICAgIHVybDogXCIvdjEvbWUvbm90aWZpY2F0aW9ucy8/c2Vlbj10cnVlXCIsXG4gICAgICAgICAgICAgICAgICAgIGNvbnRlbnRUeXBlOiBcImFwcGxpY2F0aW9uL2pzb247IGNoYXJzZXQ9dXRmLThcIixcbiAgICAgICAgICAgICAgICAgICAgZGF0YVR5cGU6IFwianNvblwiLFxuICAgICAgICAgICAgICAgICAgICBzdWNjZXNzOiBmdW5jdGlvbiAoKSB7XG4gICAgICAgICAgICAgICAgICAgICAgICAkKCcjanMtc2Jfbm90aWZpY2F0aW9uc19ub3RpZmllcicpLnJlbW92ZSgpO1xuICAgICAgICAgICAgICAgICAgICB9LFxuICAgICAgICAgICAgICAgICAgICBlcnJvcjogZnVuY3Rpb24gKFhNTEh0dHBSZXF1ZXN0KSB7XG4gICAgICAgICAgICAgICAgICAgICAgICBlcnJvckRpc3BsYXkoWE1MSHR0cFJlcXVlc3QpO1xuICAgICAgICAgICAgICAgICAgICB9XG4gICAgICAgICAgICAgICAgfSk7XG4gICAgICAgICAgICB9XG4gICAgICAgIH0pO1xuXG4gICAgICAgIC8vXG4gICAgICAgIC8vIFJlcCBXYXMgVmlld2VkP1xuICAgICAgICAkKFwiLnNob3ctcmVwdXRhdGlvbi1hY3Rpb25cIikub24oXCJjbGlja1wiLCBmdW5jdGlvbiAoKSB7XG4gICAgICAgICAgICAkLmFqYXgoe1xuICAgICAgICAgICAgICAgIHhockZpZWxkczoge3dpdGhDcmVkZW50aWFsczogdHJ1ZX0sXG4gICAgICAgICAgICAgICAgdHlwZTogXCJQVVRcIixcbiAgICAgICAgICAgICAgICB1cmw6IFwiL3YxL21lL1wiLFxuICAgICAgICAgICAgICAgIGNvbnRlbnRUeXBlOiBcImFwcGxpY2F0aW9uL2pzb247IGNoYXJzZXQ9dXRmLThcIixcbiAgICAgICAgICAgICAgICBkYXRhVHlwZTogXCJqc29uXCIsXG4gICAgICAgICAgICAgICAgZGF0YTogSlNPTi5zdHJpbmdpZnkoe1xuICAgICAgICAgICAgICAgICAgICBcInJlcHV0YXRpb25fdXBkYXRlX3NlZW5cIjogdHJ1ZVxuICAgICAgICAgICAgICAgIH0pXG4gICAgICAgICAgICB9KTtcbiAgICAgICAgfSk7XG5cbiAgICAgICAgLy9cbiAgICAgICAgLy8gU2hvdyBSZXBcbiAgICAgICAgJC5hamF4KHtcbiAgICAgICAgICAgIHhockZpZWxkczoge3dpdGhDcmVkZW50aWFsczogdHJ1ZX0sXG4gICAgICAgICAgICB0eXBlOiBcIkdFVFwiLFxuICAgICAgICAgICAgdXJsOiBcIi92MS9wcm9maWxlcy9cIiArICQoXCIjcmVwdXRhdGlvbl90b3RhbFwiKS5kYXRhKCd1c2VybmFtZScpICsgXCIvcmVwdXRhdGlvbi9cIixcbiAgICAgICAgICAgIGNvbnRlbnRUeXBlOiBcImFwcGxpY2F0aW9uL2pzb247IGNoYXJzZXQ9dXRmLThcIixcbiAgICAgICAgICAgIGRhdGFUeXBlOiBcImpzb25cIixcbiAgICAgICAgICAgIHN1Y2Nlc3M6IGZ1bmN0aW9uIChkYXRhKSB7XG4gICAgICAgICAgICAgICAgJChcIiNyZXB1dGF0aW9uX3RvdGFsXCIpLmFwcGVuZChcIjxwPlwiICsgZGF0YVtcInJlcHV0YXRpb25cIl0gKyBcIjwvcD5cIik7XG4gICAgICAgICAgICB9LFxuICAgICAgICAgICAgZXJyb3I6IGZ1bmN0aW9uKFhNTEh0dHBSZXF1ZXN0LCB0ZXh0U3RhdHVzLCBlcnJvclRocm93bikge1xuICAgICAgICAgICAgICAgIGlmKFhNTEh0dHBSZXF1ZXN0LnN0YXR1cyA9PT0gNTAwKXtcbiAgICAgICAgICAgICAgICAgICAgJChcIiNzZXJ2ZXJfZXJyb3JcIikuc2hvdygpO1xuICAgICAgICAgICAgICAgIH1cbiAgICAgICAgICAgIH1cbiAgICAgICAgfSk7XG5cbiAgICAgICAgLy9cbiAgICAgICAgLy8gU2VhcmNoXG4gICAgICAgICQoXCIuZnVsbF9zZWFyY2gtYWN0aW9uXCIpLmNsaWNrKGZ1bmN0aW9uKGUpIHtcbiAgICAgICAgICAgIHZhciBzZWFyY2hfcGFyYW0gPSAoJCgnI3NiX3NlYXJjaF9pbnB1dCcpLnZhbCgpKTtcbiAgICAgICAgICAgIHdpbmRvdy5sb2NhdGlvbi5ocmVmID0gXCIvc2VhcmNoLz9xPVwiICsgc2VhcmNoX3BhcmFtICsgXCImcGFnZT0xJmZpbHRlcj1nZW5lcmFsXCI7XG4gICAgICAgIH0pO1xuICAgICAgICAkKFwiI3NiX3NlYXJjaF9pbnB1dFwiKS5rZXl1cChmdW5jdGlvbihlKSB7XG4gICAgICAgICAgICBpZihlLndoaWNoID09PSAxMCB8fCBlLndoaWNoID09PSAxMykge1xuICAgICAgICAgICAgICAgIHZhciBzZWFyY2hfcGFyYW0gPSAoJCgnI3NiX3NlYXJjaF9pbnB1dCcpLnZhbCgpKTtcbiAgICAgICAgICAgICAgICB3aW5kb3cubG9jYXRpb24uaHJlZiA9IFwiL3NlYXJjaC8/cT1cIiArIHNlYXJjaF9wYXJhbSArIFwiJnBhZ2U9MSZmaWx0ZXI9Z2VuZXJhbFwiO1xuICAgICAgICAgICAgfVxuICAgICAgICB9KTtcblxuICAgICAgICAvL1xuICAgICAgICAvL1xuXG4gICAgICAgIC8vXG4gICAgICAgIC8vIEZyaWVuZHNcbiAgICAgICAgLy8gUmV0cmlldmVzIGFsbCB0aGUgZnJpZW5kIHJlcXVlc3RzIGZvciBhIGdpdmVuIHVzZXIgYW5kIGdhdGhlcnMgaG93XG4gICAgICAgIC8vIG1hbnkgaGF2ZSBiZWVuIHNlZW4gb3IgdW5zZWVuLlxuICAgICAgICAkLmFqYXgoe1xuICAgICAgICAgICAgeGhyRmllbGRzOiB7d2l0aENyZWRlbnRpYWxzOiB0cnVlfSxcbiAgICAgICAgICAgIHR5cGU6IFwiR0VUXCIsXG4gICAgICAgICAgICB1cmw6IFwiL3YxL21lL2ZyaWVuZF9yZXF1ZXN0cy9yZW5kZXIvXCIsXG4gICAgICAgICAgICBjb250ZW50VHlwZTogXCJhcHBsaWNhdGlvbi9qc29uOyBjaGFyc2V0PXV0Zi04XCIsXG4gICAgICAgICAgICBkYXRhVHlwZTogXCJqc29uXCIsXG4gICAgICAgICAgICBzdWNjZXNzOiBmdW5jdGlvbiAoZGF0YSkge1xuICAgICAgICAgICAgICAgICQoJyNmcmllbmRfcmVxdWVzdF93cmFwcGVyJykuYXBwZW5kKGRhdGEucmVzdWx0cy5odG1sKTtcbiAgICAgICAgICAgICAgICBpZiAoZGF0YS5yZXN1bHRzLnVuc2VlbiA+IDApIHtcbiAgICAgICAgICAgICAgICAgICAgJCgnI2pzLWZyaWVuZF9yZXF1ZXN0X25vdGlmaWVyX3dyYXBwZXInKS5hcHBlbmQoJzxzcGFuIGNsYXNzPVwibmF2YmFyLW5ldyBzYl9ub3RpZmllclwiIGlkPVwianMtc2JfZnJpZW5kX3JlcXVlc3Rfbm90aWZpZXJcIj4nICsgZGF0YS5yZXN1bHRzLnVuc2VlbiArICc8L3NwYW4+Jyk7XG4gICAgICAgICAgICAgICAgfVxuICAgICAgICAgICAgfSxcbiAgICAgICAgICAgIGVycm9yOiBmdW5jdGlvbiAoWE1MSHR0cFJlcXVlc3QpIHtcbiAgICAgICAgICAgICAgICBpZiAoWE1MSHR0cFJlcXVlc3Quc3RhdHVzID09PSA1MDApIHtcbiAgICAgICAgICAgICAgICAgICAgJChcIiNzZXJ2ZXJfZXJyb3JcIikuc2hvdygpO1xuICAgICAgICAgICAgICAgIH1cbiAgICAgICAgICAgIH1cbiAgICAgICAgfSk7XG5cbiAgICAgICAgLy8gU2hvd3MgdGhlIGZyaWVuZCByZXF1ZXN0cyB3aGVuIHRoZSBmcmllbmQgcmVxdWVzdCBpY29uIGlzIGNsaWNrZWRcbiAgICAgICAgJChcIi5zaG93X2ZyaWVuZF9yZXF1ZXN0LWFjdGlvblwiKS5jbGljayhmdW5jdGlvbiAoKSB7XG4gICAgICAgICAgICAkKFwiI2ZyaWVuZF9yZXF1ZXN0X2RpdlwiKS5mYWRlVG9nZ2xlKCk7XG4gICAgICAgICAgICBpZiAoJCgnI2pzLXNiX2ZyaWVuZF9yZXF1ZXN0X25vdGlmaWVyJykubGVuZ3RoID4gMCkge1xuICAgICAgICAgICAgICAgICQuYWpheCh7XG4gICAgICAgICAgICAgICAgICAgIHhockZpZWxkczoge3dpdGhDcmVkZW50aWFsczogdHJ1ZX0sXG4gICAgICAgICAgICAgICAgICAgIHR5cGU6IFwiR0VUXCIsXG4gICAgICAgICAgICAgICAgICAgIHVybDogXCIvdjEvbWUvZnJpZW5kX3JlcXVlc3RzLz9zZWVuPXRydWVcIixcbiAgICAgICAgICAgICAgICAgICAgY29udGVudFR5cGU6IFwiYXBwbGljYXRpb24vanNvbjsgY2hhcnNldD11dGYtOFwiLFxuICAgICAgICAgICAgICAgICAgICBkYXRhVHlwZTogXCJqc29uXCIsXG4gICAgICAgICAgICAgICAgICAgIHN1Y2Nlc3M6IGZ1bmN0aW9uICgpIHtcbiAgICAgICAgICAgICAgICAgICAgICAgICQoJyNqcy1zYl9mcmllbmRfcmVxdWVzdF9ub3RpZmllcicpLnJlbW92ZSgpO1xuICAgICAgICAgICAgICAgICAgICB9LFxuICAgICAgICAgICAgICAgICAgICBlcnJvcjogZnVuY3Rpb24gKCkge1xuICAgICAgICAgICAgICAgICAgICAgICAgJChcIiNzZXJ2ZXJfZXJyb3JcIikuc2hvdygpO1xuICAgICAgICAgICAgICAgICAgICB9XG4gICAgICAgICAgICAgICAgfSk7XG4gICAgICAgICAgICB9XG4gICAgICAgICAgICAkKFwiLnJlc3BvbmRfZnJpZW5kX3JlcXVlc3QtYWNjZXB0LWFjdGlvblwiKS5jbGljayhmdW5jdGlvbiAoZXZlbnQpIHtcbiAgICAgICAgICAgICAgICBldmVudC5wcmV2ZW50RGVmYXVsdCgpO1xuICAgICAgICAgICAgICAgIHZhciByZXF1ZXN0SUQgPSAkKHRoaXMpLmRhdGEoJ3JlcXVlc3RfaWQnKTtcbiAgICAgICAgICAgICAgICAkLmFqYXgoe1xuICAgICAgICAgICAgICAgICAgICB4aHJGaWVsZHM6IHt3aXRoQ3JlZGVudGlhbHM6IHRydWV9LFxuICAgICAgICAgICAgICAgICAgICB0eXBlOiBcIlBPU1RcIixcbiAgICAgICAgICAgICAgICAgICAgdXJsOiBcIi92MS9tZS9mcmllbmRfcmVxdWVzdHMvXCIgKyByZXF1ZXN0SUQgKyBcIi9hY2NlcHQvXCIsXG4gICAgICAgICAgICAgICAgICAgIGRhdGE6IEpTT04uc3RyaW5naWZ5KHtcbiAgICAgICAgICAgICAgICAgICAgICAgICdyZXF1ZXN0X2lkJzogcmVxdWVzdElEXG4gICAgICAgICAgICAgICAgICAgIH0pLFxuICAgICAgICAgICAgICAgICAgICBjb250ZW50VHlwZTogXCJhcHBsaWNhdGlvbi9qc29uOyBjaGFyc2V0PXV0Zi04XCIsXG4gICAgICAgICAgICAgICAgICAgIGRhdGFUeXBlOiBcImpzb25cIixcbiAgICAgICAgICAgICAgICAgICAgc3VjY2VzczogZnVuY3Rpb24gKCkge1xuICAgICAgICAgICAgICAgICAgICAgICAgJCgnI2ZyaWVuZF9yZXF1ZXN0XycgKyByZXF1ZXN0SUQpLnJlbW92ZSgpO1xuICAgICAgICAgICAgICAgICAgICB9LFxuICAgICAgICAgICAgICAgICAgICBlcnJvcjogZnVuY3Rpb24gKFhNTEh0dHBSZXF1ZXN0KSB7XG4gICAgICAgICAgICAgICAgICAgICAgICBpZiAoWE1MSHR0cFJlcXVlc3Quc3RhdHVzID09PSA1MDApIHtcbiAgICAgICAgICAgICAgICAgICAgICAgICAgICAkKFwiI3NlcnZlcl9lcnJvclwiKS5zaG93KCk7XG4gICAgICAgICAgICAgICAgICAgICAgICB9XG4gICAgICAgICAgICAgICAgICAgIH1cbiAgICAgICAgICAgICAgICB9KTtcbiAgICAgICAgICAgIH0pO1xuICAgICAgICAgICAgJChcIi5yZXNwb25kX2ZyaWVuZF9yZXF1ZXN0LWRlY2xpbmUtYWN0aW9uXCIpLmNsaWNrKGZ1bmN0aW9uIChldmVudCkge1xuICAgICAgICAgICAgICAgIGV2ZW50LnByZXZlbnREZWZhdWx0KCk7XG4gICAgICAgICAgICAgICAgdmFyIHJlcXVlc3RJRCA9ICQodGhpcykuZGF0YSgncmVxdWVzdF9pZCcpO1xuICAgICAgICAgICAgICAgICQuYWpheCh7XG4gICAgICAgICAgICAgICAgICAgIHhockZpZWxkczoge3dpdGhDcmVkZW50aWFsczogdHJ1ZX0sXG4gICAgICAgICAgICAgICAgICAgIHR5cGU6IFwiUE9TVFwiLFxuICAgICAgICAgICAgICAgICAgICB1cmw6IFwiL3YxL21lL2ZyaWVuZF9yZXF1ZXN0cy9cIiArIHJlcXVlc3RJRCArIFwiL2RlY2xpbmUvXCIsXG4gICAgICAgICAgICAgICAgICAgIGRhdGE6IEpTT04uc3RyaW5naWZ5KHtcbiAgICAgICAgICAgICAgICAgICAgICAgICdyZXF1ZXN0X2lkJzogcmVxdWVzdElEXG4gICAgICAgICAgICAgICAgICAgIH0pLFxuICAgICAgICAgICAgICAgICAgICBjb250ZW50VHlwZTogXCJhcHBsaWNhdGlvbi9qc29uOyBjaGFyc2V0PXV0Zi04XCIsXG4gICAgICAgICAgICAgICAgICAgIGRhdGFUeXBlOiBcImpzb25cIixcbiAgICAgICAgICAgICAgICAgICAgc3VjY2VzczogZnVuY3Rpb24gKCkge1xuICAgICAgICAgICAgICAgICAgICAgICAgJCgnI2ZyaWVuZF9yZXF1ZXN0XycgKyByZXF1ZXN0SUQpLnJlbW92ZSgpO1xuICAgICAgICAgICAgICAgICAgICB9LFxuICAgICAgICAgICAgICAgICAgICBlcnJvcjogZnVuY3Rpb24gKFhNTEh0dHBSZXF1ZXN0KSB7XG4gICAgICAgICAgICAgICAgICAgICAgICBpZiAoWE1MSHR0cFJlcXVlc3Quc3RhdHVzID09PSA1MDApIHtcbiAgICAgICAgICAgICAgICAgICAgICAgICAgICAkKFwiI3NlcnZlcl9lcnJvclwiKS5zaG93KCk7XG4gICAgICAgICAgICAgICAgICAgICAgICB9XG4gICAgICAgICAgICAgICAgICAgIH1cbiAgICAgICAgICAgICAgICB9KTtcbiAgICAgICAgICAgIH0pO1xuICAgICAgICAgICAgJChcIi5yZXNwb25kX2ZyaWVuZF9yZXF1ZXN0LWJsb2NrLWFjdGlvblwiKS5jbGljayhmdW5jdGlvbiAoZXZlbnQpIHtcbiAgICAgICAgICAgICAgICBldmVudC5wcmV2ZW50RGVmYXVsdCgpO1xuICAgICAgICAgICAgICAgIHZhciByZXF1ZXN0SUQgPSAkKHRoaXMpLmRhdGEoJ3JlcXVlc3RfaWQnKTtcbiAgICAgICAgICAgICAgICAkLmFqYXgoe1xuICAgICAgICAgICAgICAgICAgICB4aHJGaWVsZHM6IHt3aXRoQ3JlZGVudGlhbHM6IHRydWV9LFxuICAgICAgICAgICAgICAgICAgICB0eXBlOiBcIlBPU1RcIixcbiAgICAgICAgICAgICAgICAgICAgdXJsOiBcIi92MS9tZS9mcmllbmRfcmVxdWVzdHMvXCIgKyByZXF1ZXN0SUQgKyBcIi9ibG9jay9cIixcbiAgICAgICAgICAgICAgICAgICAgZGF0YTogSlNPTi5zdHJpbmdpZnkoe1xuICAgICAgICAgICAgICAgICAgICAgICAgJ3JlcXVlc3RfaWQnOiByZXF1ZXN0SURcbiAgICAgICAgICAgICAgICAgICAgfSksXG4gICAgICAgICAgICAgICAgICAgIGNvbnRlbnRUeXBlOiBcImFwcGxpY2F0aW9uL2pzb247IGNoYXJzZXQ9dXRmLThcIixcbiAgICAgICAgICAgICAgICAgICAgZGF0YVR5cGU6IFwianNvblwiLFxuICAgICAgICAgICAgICAgICAgICBzdWNjZXNzOiBmdW5jdGlvbiAoKSB7XG4gICAgICAgICAgICAgICAgICAgICAgICAkKCcjZnJpZW5kX3JlcXVlc3RfJyArIHJlcXVlc3RJRCkucmVtb3ZlKCk7XG4gICAgICAgICAgICAgICAgICAgIH0sXG4gICAgICAgICAgICAgICAgICAgIGVycm9yOiBmdW5jdGlvbiAoWE1MSHR0cFJlcXVlc3QpIHtcbiAgICAgICAgICAgICAgICAgICAgICAgIGlmIChYTUxIdHRwUmVxdWVzdC5zdGF0dXMgPT09IDUwMCkge1xuICAgICAgICAgICAgICAgICAgICAgICAgICAgICQoXCIjc2VydmVyX2Vycm9yXCIpLnNob3coKTtcbiAgICAgICAgICAgICAgICAgICAgICAgIH1cbiAgICAgICAgICAgICAgICAgICAgfVxuICAgICAgICAgICAgICAgIH0pO1xuICAgICAgICAgICAgfSk7XG4gICAgICAgIH0pO1xuICAgIH0pO1xufVxuXG5leHBvcnQgZnVuY3Rpb24gaW5pdE5hdmJhcigpIHtcbiAgICByZXR1cm4gbmF2YmFyKCk7XG59IiwiLyoqXG4gKiBAZmlsZVxuICogSGVscGVyIGZ1bmN0aW9ucyB0aGF0IGFyZW4ndCBnbG9iYWwuXG4gKi9cblxuLyoqXG4gKiBHZXQgY29va2llIGJhc2VkIGJ5IG5hbWUuXG4gKiBAcGFyYW0gbmFtZVxuICogQHJldHVybnMgeyp9XG4gKi9cbmV4cG9ydCBmdW5jdGlvbiBnZXRDb29raWUobmFtZSkge1xuICAgIHZhciBjb29raWVWYWx1ZSA9IG51bGw7XG4gICAgaWYgKGRvY3VtZW50LmNvb2tpZSAmJiBkb2N1bWVudC5jb29raWUgIT09IFwiXCIpIHtcbiAgICAgICAgdmFyIGNvb2tpZXMgPSBkb2N1bWVudC5jb29raWUuc3BsaXQoJzsnKTtcbiAgICAgICAgZm9yICh2YXIgaSA9IDA7IGkgPCBjb29raWVzLmxlbmd0aDsgaSArPSAxKSB7XG4gICAgICAgICAgICB2YXIgY29va2llID0gJC50cmltKGNvb2tpZXNbaV0pO1xuICAgICAgICAgICAgLy8gRG9lcyB0aGlzIGNvb2tpZSBzdHJpbmcgYmVnaW4gd2l0aCB0aGUgbmFtZSB3ZSB3YW50P1xuXG4gICAgICAgICAgICBpZiAoY29va2llLnN1YnN0cmluZygwLCBuYW1lLmxlbmd0aCArIDEpID09PSAobmFtZSArICc9JykpIHtcbiAgICAgICAgICAgICAgICBjb29raWVWYWx1ZSA9IGRlY29kZVVSSUNvbXBvbmVudChjb29raWUuc3Vic3RyaW5nKG5hbWUubGVuZ3RoICsgMSkpO1xuICAgICAgICAgICAgICAgIGJyZWFrO1xuICAgICAgICAgICAgfVxuICAgICAgICB9XG4gICAgfVxuICAgIHJldHVybiBjb29raWVWYWx1ZTtcbn1cblxuLyoqXG4gKiBDaGVjayBpZiBIVFRQIG1ldGhvZCByZXF1aXJlcyBDU1JGLlxuICogQHBhcmFtIG1ldGhvZFxuICogQHJldHVybnMge2Jvb2xlYW59XG4gKi9cbmV4cG9ydCBmdW5jdGlvbiBjc3JmU2FmZU1ldGhvZChtZXRob2QpIHtcbiAgICAvLyB0aGVzZSBIVFRQIG1ldGhvZHMgZG8gbm90IHJlcXVpcmUgQ1NSRiBwcm90ZWN0aW9uXG4gICAgcmV0dXJuICgvXihHRVR8SEVBRHxPUFRJT05TfFRSQUNFKSQvLnRlc3QobWV0aG9kKSk7XG59IiwiLyoqXG4gKiBAZmlsZVxuICogSW5pdCB0aGUgU0Igd2Vic2l0ZS5cbiAqIGdsb2JhbEluaXQgLSBSdW5zIG9uIGFsbCBwYWdlcy5cbiAqIFVzZXJBdXRoZWRJbml0IC0gUnVucyBvbiBhdXRoZWQgcGFnZXMuXG4gKiB1c2VyQW5vbkluaXQgLSBSdW5zIG9uIGFub24gcGFnZXMuXG4gKiBUT0RPOiBUaGUgaW5kaXZpZHVhbCBpbml0IGZ1bmN0aW9ucyBjb3VsZCBiZSB0dXJuZWQgaW50byBhcnJheXMgb3Igb2JqZWN0cyBhbmQgdGhlblxuICogbG9vcGVkIG92ZXIuXG4gKi9cbnZhciBoZWxwZXJzID0gcmVxdWlyZSgnLi9oZWxwZXJzJyk7XG5cbi8qKlxuICogU2NvcGUgLSBHbG9iYWxcbiAqIEFqYXggU2V0dXBcbiAqIC0tIEF1dG9tYXRpY2FsbHkgYWRkIENTUkYgY29va2llIHZhbHVlIHRvIGFsbCBhamF4IHJlcXVlc3RzLlxuICovXG5mdW5jdGlvbiBhamF4U2V0dXAoKSB7XG4gICAgJC5hamF4U2V0dXAoe1xuICAgICAgICBiZWZvcmVTZW5kOiBmdW5jdGlvbiAoeGhyLCBzZXR0aW5ncykge1xuICAgICAgICAgICAgaWYgKCFoZWxwZXJzLmNzcmZTYWZlTWV0aG9kKHNldHRpbmdzLnR5cGUpICYmICF0aGlzLmNyb3NzRG9tYWluKSB7XG4gICAgICAgICAgICAgICAgeGhyLnNldFJlcXVlc3RIZWFkZXIoXCJYLUNTUkZUb2tlblwiLCBoZWxwZXJzLmdldENvb2tpZSgnY3NyZnRva2VuJykpO1xuICAgICAgICAgICAgfVxuICAgICAgICB9XG4gICAgfSk7XG59XG5cbi8qKlxuICogIFNjb3BlIC0gVXNlciBBdXRoZWRcbiAqICBBZGRzIGFuIGV2ZW50IGhhbmRsZXIgdG8gcGFnZSB1bmxvYWQgdGhhdCBhamF4IHBvc3RzIGFsbCB0aGUgdXNlcidzIGFjdGlvbnMgdGhhdCBvY2N1cmVkIGR1cmluZyB0aGUgcGFnZS5cbiAqICBUT0RPOiBTdG9wIGRvaW5nIHRoaXMuXG4gKiAgTm90IG9ubHkgYXJlIG5vbi1hc3luYyBhamF4IGNhbGxzIGRlcHJlY2F0ZWQgaXQgaG9sZHMgdGhlIHBhZ2UgbG9hZCB1cCBmb3IgdGhlIHVzZXIuXG4gKiAgVGhleSBjYW4ndCBldmVuIHN0YXJ0IGxvYWRpbmcgdGhlIG5leHQgcGFnZSB1bnRpbCB0aGlzIGlzIGNvbXBsZXRlZC5cbiAqL1xuZnVuY3Rpb24gY29sbGVjdEF1dGhlZEFjdGlvbnMoKSB7XG4gICAgJChkb2N1bWVudCkucmVhZHkoZnVuY3Rpb24gKCkge1xuICAgICAgICBcInVzZSBzdHJpY3RcIjtcbiAgICAgICAgd2luZG93Lm9uYmVmb3JldW5sb2FkID0gZnVuY3Rpb24gKCkge1xuICAgICAgICAgICAgdmFyIG9iamVjdExpc3QgPSBbXTtcbiAgICAgICAgICAgICQoXCIuanMtcGFnZS1vYmplY3RcIikuZWFjaChmdW5jdGlvbiAoKSB7XG4gICAgICAgICAgICAgICAgb2JqZWN0TGlzdC5wdXNoKCQodGhpcykuZGF0YSgnb2JqZWN0X3V1aWQnKSk7XG4gICAgICAgICAgICB9KTtcbiAgICAgICAgICAgIGlmIChvYmplY3RMaXN0Lmxlbmd0aCkge1xuICAgICAgICAgICAgICAgICQuYWpheCh7XG4gICAgICAgICAgICAgICAgICAgIHhockZpZWxkczoge3dpdGhDcmVkZW50aWFsczogdHJ1ZX0sXG4gICAgICAgICAgICAgICAgICAgIHR5cGU6IFwiUE9TVFwiLFxuICAgICAgICAgICAgICAgICAgICBhc3luYzogZmFsc2UsXG4gICAgICAgICAgICAgICAgICAgIHVybDogXCIvZG9jc3RvcmUvdXBkYXRlX25lb19hcGkvXCIsXG4gICAgICAgICAgICAgICAgICAgIGRhdGE6IEpTT04uc3RyaW5naWZ5KHtcbiAgICAgICAgICAgICAgICAgICAgICAgICdvYmplY3RfdXVpZHMnOiBvYmplY3RMaXN0XG4gICAgICAgICAgICAgICAgICAgIH0pLFxuICAgICAgICAgICAgICAgICAgICBjb250ZW50VHlwZTogXCJhcHBsaWNhdGlvbi9qc29uOyBjaGFyc2V0PXV0Zi04XCIsXG4gICAgICAgICAgICAgICAgICAgIGRhdGFUeXBlOiBcImpzb25cIixcbiAgICAgICAgICAgICAgICAgICAgZXJyb3I6IGZ1bmN0aW9uIChYTUxIdHRwUmVxdWVzdCkge1xuICAgICAgICAgICAgICAgICAgICAgICAgaWYgKFhNTEh0dHBSZXF1ZXN0LnN0YXR1cyA9PT0gNTAwKSB7XG4gICAgICAgICAgICAgICAgICAgICAgICAgICAgJChcIiNzZXJ2ZXJfZXJyb3JcIikuc2hvdygpO1xuICAgICAgICAgICAgICAgICAgICAgICAgfVxuICAgICAgICAgICAgICAgICAgICB9XG4gICAgICAgICAgICAgICAgfSk7XG4gICAgICAgICAgICB9XG4gICAgICAgIH07XG4gICAgfSk7XG59XG5cblxuXG4vKipcbiAqIFRoaXMgZnVuY3Rpb24gaXMgY2FsbGVkIGluIHNhZ2VicmV3LmpzIG1haW4gZmlsZS5cbiAqIEVhY2ggaW5pdCB0YXNrIHNob3VsZCBiZSBkZWZpbmVkIGluIGl0J3Mgb3duIGZ1bmN0aW9uIGZvciB3aGF0ZXZlciByZWFzb24uXG4gKiAtLSBCZXR0ZXIgY29kZSByZWFkYWJpbGl0eT9cbiAqL1xuZXhwb3J0IGZ1bmN0aW9uIGdsb2JhbEluaXQoKSB7XG4gICAgY29uc29sZS5sb2coXCJHbG9iYWwgSW5pdCBTdGFydFwiKTtcbiAgICBhamF4U2V0dXAoKTtcbiAgICBjb25zb2xlLmxvZyhcIkdsb2JhbCBJbml0IFN0b3BcIik7XG59XG5cbi8qKlxuICogQXV0aCBJbml0LlxuICovXG5leHBvcnQgZnVuY3Rpb24gdXNlckF1dGhlZEluaXQoKSB7XG4gICAgY29uc29sZS5sb2coXCJ1c2VyQXV0aGVkSW5pdCBTdGFydFwiKTtcbiAgICBjb2xsZWN0QXV0aGVkQWN0aW9ucygpO1xuICAgIGNvbnNvbGUubG9nKFwidXNlckF1dGhlZEluaXQgU3RvcFwiKTtcbn1cblxuLyoqXG4gKiBBbm9uIEluaXQuXG4gKi9cbmV4cG9ydCBmdW5jdGlvbiB1c2VyQW5vbkluaXQoKSB7XG4gICAgY29uc29sZS5sb2coXCJ1c2VyQW5vbkluaXQgU3RhcnRcIik7XG4gICAgY29uc29sZS5sb2coXCJ1c2VyQW5vbkluaXQgU3RvcFwiKTtcbn1cblxuXG5cblxuIiwiLyoqXG4gKiBAZmlsZVxuICogVXNlZCBvbiBldmVyeSBwYWdlIHdpdGggYW4gYXV0aGVkIHVzZXIuXG4gKi9cblxudmFyIHVzZXJBdXRoZWRJbml0ID0gcmVxdWlyZSgnLi9jb21wb25lbnRzL2luaXQnKS51c2VyQXV0aGVkSW5pdDtcbnZhciBuYXZiYXIgPSByZXF1aXJlKCcuL2NvbXBvbmVudHMvYXV0aGVkL25hdmJhcicpLmluaXROYXZiYXI7XG5cbi8vIEluaXQgdmFyaW91cyB0aGluZ3MgZm9yIGF1dGhlZCB1c2VyLlxudXNlckF1dGhlZEluaXQoKTtcbm5hdmJhcigpOyJdfQ==
