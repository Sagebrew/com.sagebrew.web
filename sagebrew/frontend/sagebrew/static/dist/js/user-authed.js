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
//# sourceMappingURL=data:application/json;charset:utf-8;base64,eyJ2ZXJzaW9uIjozLCJzb3VyY2VzIjpbIm5vZGVfbW9kdWxlcy9icm93c2VyaWZ5L25vZGVfbW9kdWxlcy9icm93c2VyLXBhY2svX3ByZWx1ZGUuanMiLCIvVXNlcnMvbXdpc25lci9Qcm9qZWN0cy9zYWdlYnJldy9jb20uc2FnZWJyZXcud2ViL3NhZ2VicmV3L2Zyb250ZW5kL2pzL3NyYy9jb21wb25lbnRzL2F1dGhlZC9uYXZiYXIuanMiLCIvVXNlcnMvbXdpc25lci9Qcm9qZWN0cy9zYWdlYnJldy9jb20uc2FnZWJyZXcud2ViL3NhZ2VicmV3L2Zyb250ZW5kL2pzL3NyYy9jb21wb25lbnRzL2hlbHBlcnMuanMiLCIvVXNlcnMvbXdpc25lci9Qcm9qZWN0cy9zYWdlYnJldy9jb20uc2FnZWJyZXcud2ViL3NhZ2VicmV3L2Zyb250ZW5kL2pzL3NyYy9jb21wb25lbnRzL2luaXQuanMiLCIvVXNlcnMvbXdpc25lci9Qcm9qZWN0cy9zYWdlYnJldy9jb20uc2FnZWJyZXcud2ViL3NhZ2VicmV3L2Zyb250ZW5kL2pzL3NyYy91c2VyLWF1dGhlZC5qcyJdLCJuYW1lcyI6W10sIm1hcHBpbmdzIjoiQUFBQTs7Ozs7Ozs7Ozs7O0FDS0EsSUFBSSxRQUFRLEdBQUcsT0FBTyxDQUFDLFVBQVUsQ0FBQyxDQUFDOzs7Ozs7QUFNbkMsU0FBUyxNQUFNLEdBQUc7QUFDZCxLQUFDLENBQUMsUUFBUSxDQUFDLENBQUMsS0FBSyxDQUFDLFlBQVc7Ozs7OztBQU16QixnQkFBUSxDQUFDLE9BQU8sQ0FBQyxHQUFHLENBQUMsRUFBQyxHQUFHLEVBQUUsOEJBQThCLEVBQUMsQ0FBQyxDQUN0RCxJQUFJLENBQUMsVUFBUyxJQUFJLEVBQUM7QUFDaEIsYUFBQyxDQUFDLHVCQUF1QixDQUFDLENBQUMsTUFBTSxDQUFDLElBQUksQ0FBQyxPQUFPLENBQUMsSUFBSSxDQUFDLENBQUM7QUFDckQsZ0JBQUksSUFBSSxDQUFDLE9BQU8sQ0FBQyxNQUFNLEdBQUcsQ0FBQyxFQUFFO0FBQ3pCLGlCQUFDLENBQUMsbUNBQW1DLENBQUMs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R0FBRztBQUM3Qix3QkFBb0IsRUFBRSxDQUFDO0NBQzFCOzs7Ozs7QUFLTSxTQUFTLFlBQVksR0FBRyxFQUU5Qjs7Ozs7Ozs7OztBQ2pGRCxJQUFJLGNBQWMsR0FBRyxPQUFPLENBQUMsbUJBQW1CLENBQUMsQ0FBQyxjQUFjLENBQUM7QUFDakUsSUFBSSxNQUFNLEdBQUcsT0FBTyxDQUFDLDRCQUE0QixDQUFDLENBQUMsVUFBVSxDQUFDOzs7QUFHOUQsY0FBYyxFQUFFLENBQUM7QUFDakIsTUFBTSxFQUFFLENBQUMiLCJmaWxlIjoiZ2VuZXJhdGVkLmpzIiwic291cmNlUm9vdCI6IiIsInNvdXJjZXNDb250ZW50IjpbIihmdW5jdGlvbiBlKHQsbixyKXtmdW5jdGlvbiBzKG8sdSl7aWYoIW5bb10pe2lmKCF0W29dKXt2YXIgYT10eXBlb2YgcmVxdWlyZT09XCJmdW5jdGlvblwiJiZyZXF1aXJlO2lmKCF1JiZhKXJldHVybiBhKG8sITApO2lmKGkpcmV0dXJuIGkobywhMCk7dmFyIGY9bmV3IEVycm9yKFwiQ2Fubm90IGZpbmQgbW9kdWxlICdcIitvK1wiJ1wiKTt0aHJvdyBmLmNvZGU9XCJNT0RVTEVfTk9UX0ZPVU5EXCIsZn12YXIgbD1uW29dPXtleHBvcnRzOnt9fTt0W29dWzBdLmNhbGwobC5leHBvcnRzLGZ1bmN0aW9uKGUpe3ZhciBuPXRbb11bMV1bZV07cmV0dXJuIHMobj9uOmUpfSxsLGwuZXhwb3J0cyxlLHQsbixyKX1yZXR1cm4gbltvXS5leHBvcnRzfXZhciBpPXR5cGVvZiByZXF1aXJlPT1cImZ1bmN0aW9uXCImJnJlcXVpcmU7Zm9yKHZhciBvPTA7bzxyLmxlbmd0aDtvKyspcyhyW29dKTtyZXR1cm4gc30pIiwiLyoqXG4gKiBAZmlsZVxuICogQWxsIHRoZSBmdW5jdGlvbmFsaXR5IGZvciB0aGUgbmF2YmFyLlxuICogVE9ETzogUmVvcmdhbml6ZS5cbiAqL1xudmFyIHNhZ2VicmV3ID0gcmVxdWlyZSgnc2FnZWJyZXcnKTtcblxuLyoqXG4gKiAgU2NvcGUgLSBVc2VyIEF1dGhlZFxuICogIEFsbCB0aGluZ3MgcmVsYXRpbmcgdG8gdGhlIG5hdmJhci5cbiAqL1xuZnVuY3Rpb24gbmF2YmFyKCkge1xuICAgICQoZG9jdW1lbnQpLnJlYWR5KGZ1bmN0aW9uKCkge1xuICAgICAgICAvL1xuICAgICAgICAvLyBOb3RpZmljYXRpb25zXG4gICAgICAgIC8vIFJldHJpZXZlcyBhbGwgdGhlIG5vdGlmaWNhdGlvbnMgZm9yIGEgZ2l2ZW4gdXNlciBhbmQgZ2F0aGVycyBob3dcbiAgICAgICAgLy8gbWFueSBoYXZlIGJlZW4gc2VlbiBvciB1bnNlZW4uXG4gICAgICAgIC8vTm90aWZpY2F0aW9uIGNvdW50IGluIHNpZGViYXIuXG4gICAgICAgIHNhZ2VicmV3LnJlcXVlc3QuZ2V0KHt1cmw6IFwiL3YxL21lL25vdGlmaWNhdGlvbnMvcmVuZGVyL1wifSlcbiAgICAgICAgICAgIC50aGVuKGZ1bmN0aW9uKGRhdGEpe1xuICAgICAgICAgICAgICAgICQoJyNub3RpZmljYXRpb25fd3JhcHBlcicpLmFwcGVuZChkYXRhLnJlc3VsdHMuaHRtbCk7XG4gICAgICAgICAgICAgICAgaWYgKGRhdGEucmVzdWx0cy51bnNlZW4gPiAwKSB7XG4gICAgICAgICAgICAgICAgICAgICQoJyNqcy1ub3RpZmljYXRpb25fbm90aWZpZXJfd3JhcHBlcicpLmFwcGVuZCgnPHNwYW4gY2xhc3M9XCJuYXZiYXItbmV3IHNiX25vdGlmaWVyXCIgaWQ9XCJqcy1zYl9ub3RpZmljYXRpb25zX25vdGlmaWVyXCI+JyArIGRhdGEucmVzdWx0cy51bnNlZW4gKyAnPC9zcGFuPicpO1xuICAgICAgICAgICAgICAgIH1cbiAgICAgICAgfSk7XG5cbiAgICAgICAgLy8gU2hvd3MgdGhlIG5vdGlmaWNhdGlvbnMgd2hlbiB0aGUgbm90aWZpY2F0aW9uIGljb24gaXMgY2xpY2tlZFxuICAgICAgICAkKFwiLnNob3dfbm90aWZpY2F0aW9ucy1hY3Rpb25cIikuY2xpY2soZnVuY3Rpb24gKCkge1xuICAgICAgICAgICAgJChcIiNub3RpZmljYXRpb25fZGl2XCIpLmZhZGVUb2dnbGUoKTtcblxuICAgICAgICAgICAgaWYgKCQoJyNqcy1ub3RpZmljYXRpb25fbm90aWZpZXJfd3JhcHBlcicpLmNoaWxkcmVuKCkubGVuZ3RoID4gMCkge1xuICAgICAgICAgICAgICAgIHNhZ2VicmV3LnJlcXVlc3QuZ2V0KHt1cmw6ICBcIi92MS9tZS9ub3RpZmljYXRpb25zLz9zZWVuPXRydWVcIn0pXG4gICAgICAgICAgICAgICAgICAgIC50aGVuKGZ1bmN0aW9uKCkge1xuICAgICAgICAgICAgICAgICAgICAgICAgJCgnI2pzLXNiX25vdGlmaWNhdGlvbnNfbm90aWZpZXInKS5yZW1vdmUoKTtcbiAgICAgICAgICAgICAgICB9KTtcbiAgICAgICAgICAgIH1cblxuICAgICAgICB9KTtcblxuICAgICAgICAvL1xuICAgICAgICAvLyBSZXAgV2FzIFZpZXdlZD9cbiAgICAgICAgJChcIi5zaG93LXJlcHV0YXRpb24tYWN0aW9uXCIpLm9uKFwiY2xpY2tcIiwgZnVuY3Rpb24gKCkge1xuICAgICAgICAgICAgc2FnZWJyZXcucmVxdWVzdC5wdXQoe1xuICAgICAgICAgICAgICAgIHVybDogXCIvdjEvbWUvXCIsXG4gICAgICAgICAgICAgICAgZGF0YTogSlNPTi5zdHJpbmdpZnkoe1xuICAgICAgICAgICAgICAgICAgICBcInJlcHV0YXRpb25fdXBkYXRlX3NlZW5cIjogdHJ1ZVxuICAgICAgICAgICAgICAgIH0pXG4gICAgICAgICAgICB9KTtcbiAgICAgICAgfSk7XG5cbiAgICAgICAgLy9cbiAgICAgICAgLy8gU2hvdyBSZXBcbiAgICAgICAgc2FnZWJyZXcucmVxdWVzdC5nZXQoe3VybDogXCIvdjEvcHJvZmlsZXMvXCIgKyAkKFwiI3JlcHV0YXRpb25fdG90YWxcIikuZGF0YSgndXNlcm5hbWUnKSArIFwiL3JlcHV0YXRpb24vXCJ9KVxuICAgICAgICAgICAgLnRoZW4oZnVuY3Rpb24oZGF0YSkge1xuICAgICAgICAgICAgICAgICQoXCIjcmVwdXRhdGlvbl90b3RhbFwiKS5hcHBlbmQoXCI8cD5cIiArIGRhdGFbJ3JlcHV0YXRpb24nXSArIFwiPC9wPlwiKTtcbiAgICAgICAgfSk7XG5cblxuICAgICAgICAvL1xuICAgICAgICAvLyBTZWFyY2hcbiAgICAgICAgJChcIi5mdWxsX3NlYXJjaC1hY3Rpb25cIikuY2xpY2soZnVuY3Rpb24oZSkge1xuICAgICAgICAgICAgdmFyIHNlYXJjaF9wYXJhbSA9ICgkKCcjc2Jfc2VhcmNoX2lucHV0JykudmFsKCkpO1xuICAgICAgICAgICAgd2luZG93LmxvY2F0aW9uLmhyZWYgPSBcIi9zZWFyY2gvP3E9XCIgKyBzZWFyY2hfcGFyYW0gKyBcIiZwYWdlPTEmZmlsdGVyPWdlbmVyYWxcIjtcbiAgICAgICAgfSk7XG4gICAgICAgICQoXCIjc2Jfc2VhcmNoX2lucHV0XCIpLmtleXVwKGZ1bmN0aW9uKGUpIHtcbiAgICAgICAgICAgIGlmKGUud2hpY2ggPT09IDEwIHx8IGUud2hpY2ggPT09IDEzKSB7XG4gICAgICAgICAgICAgICAgdmFyIHNlYXJjaF9wYXJhbSA9ICgkKCcjc2Jfc2VhcmNoX2lucHV0JykudmFsKCkpO1xuICAgICAgICAgICAgICAgIHdpbmRvdy5sb2NhdGlvbi5ocmVmID0gXCIvc2VhcmNoLz9xPVwiICsgc2VhcmNoX3BhcmFtICsgXCImcGFnZT0xJmZpbHRlcj1nZW5lcmFsXCI7XG4gICAgICAgICAgICB9XG4gICAgICAgIH0pO1xuXG4gICAgICAgIC8vXG4gICAgICAgIC8vIEZyaWVuZHNcbiAgICAgICAgLy8gUmV0cmlldmVzIGFsbCB0aGUgZnJpZW5kIHJlcXVlc3RzIGZvciBhIGdpdmVuIHVzZXIgYW5kIGdhdGhlcnMgaG93XG4gICAgICAgIC8vIG1hbnkgaGF2ZSBiZWVuIHNlZW4gb3IgdW5zZWVuLlxuICAgICAgICBzYWdlYnJldy5yZXF1ZXN0LmdldCh7dXJsOiBcIi92MS9tZS9mcmllbmRfcmVxdWVzdHMvcmVuZGVyL1wifSlcbiAgICAgICAgICAgIC50aGVuKGZ1bmN0aW9uKGRhdGEpIHtcbiAgICAgICAgICAgICAgICAkKCcjZnJpZW5kX3JlcXVlc3Rfd3JhcHBlcicpLmFwcGVuZChkYXRhLnJlc3VsdHMuaHRtbCk7XG4gICAgICAgICAgICAgICAgaWYgKGRhdGEucmVzdWx0cy51bnNlZW4gPiAwKSB7XG4gICAgICAgICAgICAgICAgICAgICQoJyNqcy1mcmllbmRfcmVxdWVzdF9ub3RpZmllcl93cmFwcGVyJykuYXBwZW5kKCc8c3BhbiBjbGFzcz1cIm5hdmJhci1uZXcgc2Jfbm90aWZpZXJcIiBpZD1cImpzLXNiX2ZyaWVuZF9yZXF1ZXN0X25vdGlmaWVyXCI+JyArIGRhdGEucmVzdWx0cy51bnNlZW4gKyAnPC9zcGFuPicpO1xuICAgICAgICAgICAgICAgIH1cbiAgICAgICAgICAgIH0pO1xuXG4gICAgICAgIC8vIFNob3dzIHRoZSBmcmllbmQgcmVxdWVzdHMgd2hlbiB0aGUgZnJpZW5kIHJlcXVlc3QgaWNvbiBpcyBjbGlja2VkXG4gICAgICAgICQoXCIuc2hvd19mcmllbmRfcmVxdWVzdC1hY3Rpb25cIikuY2xpY2soZnVuY3Rpb24gKCkge1xuICAgICAgICAgICAgJChcIiNmcmllbmRfcmVxdWVzdF9kaXZcIikuZmFkZVRvZ2dsZSgpO1xuICAgICAgICAgICAgaWYgKCQoJyNqcy1zYl9mcmllbmRfcmVxdWVzdF9ub3RpZmllcicpLmxlbmd0aCA+IDApIHtcbiAgICAgICAgICAgICAgICBzYWdlYnJldy5yZXF1ZXN0LmdldCh7dXJsOiBcIi92MS9tZS9mcmllbmRfcmVxdWVzdHMvP3NlZW49dHJ1ZVwifSlcbiAgICAgICAgICAgICAgICAudGhlbihmdW5jdGlvbigpIHtcbiAgICAgICAgICAgICAgICAgICAgICQoJyNqcy1zYl9mcmllbmRfcmVxdWVzdF9ub3RpZmllcicpLnJlbW92ZSgpO1xuICAgICAgICAgICAgICAgIH0pO1xuICAgICAgICAgICAgfVxuXG4gICAgICAgICAgICAkKFwiLnJlc3BvbmRfZnJpZW5kX3JlcXVlc3QtYWNjZXB0LWFjdGlvblwiKS5jbGljayhmdW5jdGlvbiAoZXZlbnQpIHtcbiAgICAgICAgICAgICAgICBldmVudC5wcmV2ZW50RGVmYXVsdCgpO1xuICAgICAgICAgICAgICAgIHZhciByZXF1ZXN0SUQgPSAkKHRoaXMpLmRhdGEoJ3JlcXVlc3RfaWQnKTtcbiAgICAgICAgICAgICAgICBzYWdlYnJldy5yZXF1ZXN0LnBvc3Qoe1xuICAgICAgICAgICAgICAgICAgICB1cmw6IFwiL3YxL21lL2ZyaWVuZF9yZXF1ZXN0cy9cIiArIHJlcXVlc3RJRCArIFwiL2FjY2VwdC9cIixcbiAgICAgICAgICAgICAgICAgICAgZGF0YTogSlNPTi5zdHJpbmdpZnkoe1xuICAgICAgICAgICAgICAgICAgICAgICAgJ3JlcXVlc3RfaWQnOiByZXF1ZXN0SURcbiAgICAgICAgICAgICAgICAgICAgfSlcbiAgICAgICAgICAgICAgICB9KS50aGVuKGZ1bmN0aW9uKCkge1xuICAgICAgICAgICAgICAgICAgICAkKCcjZnJpZW5kX3JlcXVlc3RfJyArIHJlcXVlc3RJRCkucmVtb3ZlKCk7XG4gICAgICAgICAgICAgICAgfSk7XG4gICAgICAgICAgICB9KTtcblxuICAgICAgICAgICAgJChcIi5yZXNwb25kX2ZyaWVuZF9yZXF1ZXN0LWRlY2xpbmUtYWN0aW9uXCIpLmNsaWNrKGZ1bmN0aW9uIChldmVudCkge1xuICAgICAgICAgICAgICAgIGV2ZW50LnByZXZlbnREZWZhdWx0KCk7XG4gICAgICAgICAgICAgICAgdmFyIHJlcXVlc3RJRCA9ICQodGhpcykuZGF0YSgncmVxdWVzdF9pZCcpO1xuICAgICAgICAgICAgICAgIHNhZ2VicmV3LnJlcXVlc3QucG9zdCh7XG4gICAgICAgICAgICAgICAgICAgIHVybDogXCIvdjEvbWUvZnJpZW5kX3JlcXVlc3RzL1wiICsgcmVxdWVzdElEICsgXCIvZGVjbGluZS9cIixcbiAgICAgICAgICAgICAgICAgICAgZGF0YTogSlNPTi5zdHJpbmdpZnkoe1xuICAgICAgICAgICAgICAgICAgICAgICAgJ3JlcXVlc3RfaWQnOiByZXF1ZXN0SURcbiAgICAgICAgICAgICAgICAgICAgfSlcbiAgICAgICAgICAgICAgICB9KS50aGVuKGZ1bmN0aW9uKCkge1xuICAgICAgICAgICAgICAgICAgICAkKCcjZnJpZW5kX3JlcXVlc3RfJyArIHJlcXVlc3RJRCkucmVtb3ZlKCk7XG4gICAgICAgICAgICAgICAgfSk7XG4gICAgICAgICAgICB9KTtcblxuICAgICAgICAgICAgJChcIi5yZXNwb25kX2ZyaWVuZF9yZXF1ZXN0LWJsb2NrLWFjdGlvblwiKS5jbGljayhmdW5jdGlvbiAoZXZlbnQpIHtcbiAgICAgICAgICAgICAgICBldmVudC5wcmV2ZW50RGVmYXVsdCgpO1xuICAgICAgICAgICAgICAgIHZhciByZXF1ZXN0SUQgPSAkKHRoaXMpLmRhdGEoJ3JlcXVlc3RfaWQnKTtcbiAgICAgICAgICAgICAgICBzYWdlYnJldy5yZXF1ZXN0LnBvc3Qoe1xuICAgICAgICAgICAgICAgICAgICB1cmw6IFwiL3YxL21lL2ZyaWVuZF9yZXF1ZXN0cy9cIiArIHJlcXVlc3RJRCArIFwiL2Jsb2NrL1wiLFxuICAgICAgICAgICAgICAgICAgICBkYXRhOiBKU09OLnN0cmluZ2lmeSh7XG4gICAgICAgICAgICAgICAgICAgICAgICAncmVxdWVzdF9pZCc6IHJlcXVlc3RJRFxuICAgICAgICAgICAgICAgICAgICB9KVxuICAgICAgICAgICAgICAgIH0pLnRoZW4oZnVuY3Rpb24oKSB7XG4gICAgICAgICAgICAgICAgICAgICQoJyNmcmllbmRfcmVxdWVzdF8nICsgcmVxdWVzdElEKS5yZW1vdmUoKTtcbiAgICAgICAgICAgICAgICB9KTtcbiAgICAgICAgICAgIH0pO1xuXG4gICAgICAgIH0pO1xuICAgIH0pO1xufVxuXG5leHBvcnQgZnVuY3Rpb24gaW5pdE5hdmJhcigpIHtcbiAgICByZXR1cm4gbmF2YmFyKCk7XG59IiwiLyoqXG4gKiBAZmlsZVxuICogSGVscGVyIGZ1bmN0aW9ucyB0aGF0IGFyZW4ndCBnbG9iYWwuXG4gKi9cblxuLyoqXG4gKiBHZXQgY29va2llIGJhc2VkIGJ5IG5hbWUuXG4gKiBAcGFyYW0gbmFtZVxuICogQHJldHVybnMgeyp9XG4gKi9cbmV4cG9ydCBmdW5jdGlvbiBnZXRDb29raWUobmFtZSkge1xuICAgIHZhciBjb29raWVWYWx1ZSA9IG51bGw7XG4gICAgaWYgKGRvY3VtZW50LmNvb2tpZSAmJiBkb2N1bWVudC5jb29raWUgIT09IFwiXCIpIHtcbiAgICAgICAgdmFyIGNvb2tpZXMgPSBkb2N1bWVudC5jb29raWUuc3BsaXQoJzsnKTtcbiAgICAgICAgZm9yICh2YXIgaSA9IDA7IGkgPCBjb29raWVzLmxlbmd0aDsgaSArPSAxKSB7XG4gICAgICAgICAgICB2YXIgY29va2llID0gJC50cmltKGNvb2tpZXNbaV0pO1xuICAgICAgICAgICAgLy8gRG9lcyB0aGlzIGNvb2tpZSBzdHJpbmcgYmVnaW4gd2l0aCB0aGUgbmFtZSB3ZSB3YW50P1xuXG4gICAgICAgICAgICBpZiAoY29va2llLnN1YnN0cmluZygwLCBuYW1lLmxlbmd0aCArIDEpID09PSAobmFtZSArICc9JykpIHtcbiAgICAgICAgICAgICAgICBjb29raWVWYWx1ZSA9IGRlY29kZVVSSUNvbXBvbmVudChjb29raWUuc3Vic3RyaW5nKG5hbWUubGVuZ3RoICsgMSkpO1xuICAgICAgICAgICAgICAgIGJyZWFrO1xuICAgICAgICAgICAgfVxuICAgICAgICB9XG4gICAgfVxuICAgIHJldHVybiBjb29raWVWYWx1ZTtcbn1cblxuLyoqXG4gKiBDaGVjayBpZiBIVFRQIG1ldGhvZCByZXF1aXJlcyBDU1JGLlxuICogQHBhcmFtIG1ldGhvZFxuICogQHJldHVybnMge2Jvb2xlYW59XG4gKi9cbmV4cG9ydCBmdW5jdGlvbiBjc3JmU2FmZU1ldGhvZChtZXRob2QpIHtcbiAgICAvLyB0aGVzZSBIVFRQIG1ldGhvZHMgZG8gbm90IHJlcXVpcmUgQ1NSRiBwcm90ZWN0aW9uXG4gICAgcmV0dXJuICgvXihHRVR8SEVBRHxPUFRJT05TfFRSQUNFKSQvLnRlc3QobWV0aG9kKSk7XG59IiwiLyoqXG4gKiBAZmlsZVxuICogSW5pdCB0aGUgU0Igd2Vic2l0ZS5cbiAqIGdsb2JhbEluaXQgLSBSdW5zIG9uIGFsbCBwYWdlcy5cbiAqIFVzZXJBdXRoZWRJbml0IC0gUnVucyBvbiBhdXRoZWQgcGFnZXMuXG4gKiB1c2VyQW5vbkluaXQgLSBSdW5zIG9uIGFub24gcGFnZXMuXG4gKiBUT0RPOiBUaGUgaW5kaXZpZHVhbCBpbml0IGZ1bmN0aW9ucyBjb3VsZCBiZSB0dXJuZWQgaW50byBhcnJheXMgb3Igb2JqZWN0cyBhbmQgdGhlblxuICogbG9vcGVkIG92ZXIuXG4gKi9cbnZhciBoZWxwZXJzID0gcmVxdWlyZSgnLi9oZWxwZXJzJyk7XG5cbi8qKlxuICogU2NvcGUgLSBHbG9iYWxcbiAqIEFqYXggU2V0dXBcbiAqIC0tIEF1dG9tYXRpY2FsbHkgYWRkIENTUkYgY29va2llIHZhbHVlIHRvIGFsbCBhamF4IHJlcXVlc3RzLlxuICovXG5mdW5jdGlvbiBhamF4U2V0dXAoKSB7XG4gICAgJC5hamF4U2V0dXAoe1xuICAgICAgICBiZWZvcmVTZW5kOiBmdW5jdGlvbiAoeGhyLCBzZXR0aW5ncykge1xuICAgICAgICAgICAgaWYgKCFoZWxwZXJzLmNzcmZTYWZlTWV0aG9kKHNldHRpbmdzLnR5cGUpICYmICF0aGlzLmNyb3NzRG9tYWluKSB7XG4gICAgICAgICAgICAgICAgeGhyLnNldFJlcXVlc3RIZWFkZXIoXCJYLUNTUkZUb2tlblwiLCBoZWxwZXJzLmdldENvb2tpZSgnY3NyZnRva2VuJykpO1xuICAgICAgICAgICAgfVxuICAgICAgICB9XG4gICAgfSk7XG59XG5cbi8qKlxuICogIFNjb3BlIC0gVXNlciBBdXRoZWRcbiAqICBBZGRzIGFuIGV2ZW50IGhhbmRsZXIgdG8gcGFnZSB1bmxvYWQgdGhhdCBhamF4IHBvc3RzIGFsbCB0aGUgdXNlcidzIGFjdGlvbnMgdGhhdCBvY2N1cmVkIGR1cmluZyB0aGUgcGFnZS5cbiAqICBUT0RPOiBTdG9wIGRvaW5nIHRoaXMuXG4gKiAgTm90IG9ubHkgYXJlIG5vbi1hc3luYyBhamF4IGNhbGxzIGRlcHJlY2F0ZWQgaXQgaG9sZHMgdGhlIHBhZ2UgbG9hZCB1cCBmb3IgdGhlIHVzZXIuXG4gKiAgVGhleSBjYW4ndCBldmVuIHN0YXJ0IGxvYWRpbmcgdGhlIG5leHQgcGFnZSB1bnRpbCB0aGlzIGlzIGNvbXBsZXRlZC5cbiAqL1xuZnVuY3Rpb24gY29sbGVjdEF1dGhlZEFjdGlvbnMoKSB7XG4gICAgJChkb2N1bWVudCkucmVhZHkoZnVuY3Rpb24gKCkge1xuICAgICAgICBcInVzZSBzdHJpY3RcIjtcbiAgICAgICAgd2luZG93Lm9uYmVmb3JldW5sb2FkID0gZnVuY3Rpb24gKCkge1xuICAgICAgICAgICAgdmFyIG9iamVjdExpc3QgPSBbXTtcbiAgICAgICAgICAgICQoXCIuanMtcGFnZS1vYmplY3RcIikuZWFjaChmdW5jdGlvbiAoKSB7XG4gICAgICAgICAgICAgICAgb2JqZWN0TGlzdC5wdXNoKCQodGhpcykuZGF0YSgnb2JqZWN0X3V1aWQnKSk7XG4gICAgICAgICAgICB9KTtcbiAgICAgICAgICAgIGlmIChvYmplY3RMaXN0Lmxlbmd0aCkge1xuICAgICAgICAgICAgICAgICQuYWpheCh7XG4gICAgICAgICAgICAgICAgICAgIHhockZpZWxkczoge3dpdGhDcmVkZW50aWFsczogdHJ1ZX0sXG4gICAgICAgICAgICAgICAgICAgIHR5cGU6IFwiUE9TVFwiLFxuICAgICAgICAgICAgICAgICAgICBhc3luYzogZmFsc2UsXG4gICAgICAgICAgICAgICAgICAgIHVybDogXCIvZG9jc3RvcmUvdXBkYXRlX25lb19hcGkvXCIsXG4gICAgICAgICAgICAgICAgICAgIGRhdGE6IEpTT04uc3RyaW5naWZ5KHtcbiAgICAgICAgICAgICAgICAgICAgICAgICdvYmplY3RfdXVpZHMnOiBvYmplY3RMaXN0XG4gICAgICAgICAgICAgICAgICAgIH0pLFxuICAgICAgICAgICAgICAgICAgICBjb250ZW50VHlwZTogXCJhcHBsaWNhdGlvbi9qc29uOyBjaGFyc2V0PXV0Zi04XCIsXG4gICAgICAgICAgICAgICAgICAgIGRhdGFUeXBlOiBcImpzb25cIixcbiAgICAgICAgICAgICAgICAgICAgZXJyb3I6IGZ1bmN0aW9uIChYTUxIdHRwUmVxdWVzdCkge1xuICAgICAgICAgICAgICAgICAgICAgICAgaWYgKFhNTEh0dHBSZXF1ZXN0LnN0YXR1cyA9PT0gNTAwKSB7XG4gICAgICAgICAgICAgICAgICAgICAgICAgICAgJChcIiNzZXJ2ZXJfZXJyb3JcIikuc2hvdygpO1xuICAgICAgICAgICAgICAgICAgICAgICAgfVxuICAgICAgICAgICAgICAgICAgICB9XG4gICAgICAgICAgICAgICAgfSk7XG4gICAgICAgICAgICB9XG4gICAgICAgIH07XG4gICAgfSk7XG59XG5cblxuXG4vKipcbiAqIFRoaXMgZnVuY3Rpb24gaXMgY2FsbGVkIGluIHNhZ2VicmV3LmpzIG1haW4gZmlsZS5cbiAqIEVhY2ggaW5pdCB0YXNrIHNob3VsZCBiZSBkZWZpbmVkIGluIGl0J3Mgb3duIGZ1bmN0aW9uIGZvciB3aGF0ZXZlciByZWFzb24uXG4gKiAtLSBCZXR0ZXIgY29kZSByZWFkYWJpbGl0eT9cbiAqL1xuZXhwb3J0IGZ1bmN0aW9uIGdsb2JhbEluaXQoKSB7XG4gICAgYWpheFNldHVwKCk7XG59XG5cbi8qKlxuICogQXV0aCBJbml0LlxuICovXG5leHBvcnQgZnVuY3Rpb24gdXNlckF1dGhlZEluaXQoKSB7XG4gICAgY29sbGVjdEF1dGhlZEFjdGlvbnMoKTtcbn1cblxuLyoqXG4gKiBBbm9uIEluaXQuXG4gKi9cbmV4cG9ydCBmdW5jdGlvbiB1c2VyQW5vbkluaXQoKSB7XG5cbn1cblxuXG5cblxuIiwiLyoqXG4gKiBAZmlsZVxuICogVXNlZCBvbiBldmVyeSBwYWdlIHdpdGggYW4gYXV0aGVkIHVzZXIuXG4gKi9cblxudmFyIHVzZXJBdXRoZWRJbml0ID0gcmVxdWlyZSgnLi9jb21wb25lbnRzL2luaXQnKS51c2VyQXV0aGVkSW5pdDtcbnZhciBuYXZiYXIgPSByZXF1aXJlKCcuL2NvbXBvbmVudHMvYXV0aGVkL25hdmJhcicpLmluaXROYXZiYXI7XG5cbi8vIEluaXQgdmFyaW91cyB0aGluZ3MgZm9yIGF1dGhlZCB1c2VyLlxudXNlckF1dGhlZEluaXQoKTtcbm5hdmJhcigpOyJdfQ==
