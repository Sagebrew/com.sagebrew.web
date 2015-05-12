/*global $, jQuery*/
$(document).ready(function () {
    "use strict";
    // Retrieves all the notifications for a given user and gathers how
    // many have been seen or unseen.
    $.ajax({
        xhrFields: {withCredentials: true},
        type: "GET",
        url: "/v1/me/notifications/render/",
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (data) {
            $('#notification_wrapper').append(data.results.html);
            if (data.results.unseen > 0) {
                $('#js-notification_notifier_wrapper').append('<span class="navbar-new sb_notifier" id="js-sb_notifications_notifier">' + data.results.unseen + '</span>');
            }
        },
        error: function (XMLHttpRequest) {
            errorDisplay(XMLHttpRequest);
        }
    });
    // Shows the notifications when the notification icon is clicked
    $(".show_notifications-action").click(function () {
        $("#notification_div").fadeToggle();
        if ($('#js-notification_notifier_wrapper').children().length > 0) {
            $.ajax({
                xhrFields: {withCredentials: true},
                type: "GET",
                url: "/v1/me/notifications/?seen=true",
                contentType: "application/json; charset=utf-8",
                dataType: "json",
                success: function () {
                    $('#js-sb_notifications_notifier').remove();
                },
                error: function (XMLHttpRequest) {
                    errorDisplay(XMLHttpRequest);
                }
            });
        }
    });
});
