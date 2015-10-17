/*global $, ajaxSecurity*/
/**
 * NO LONGER USED (For real this time)
 */
$(document).ready(function () {
    "use strict";
    $("button.js-send-friend-request").click(function (event) {
        event.preventDefault();
        var sendRequest = $("button.js-send-friend-request");
        sendRequest.attr("disabled", "disabled");

        $.ajax({
            xhrFields: {withCredentials: true},
            type: "POST",
            url: "/relationships/create_friend_request/",
            data: JSON.stringify({
                'from_username': $(this).data('from_username'),
                'to_username': $(this).data('to_username')
            }),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (data) {
                if (data.action === true) {
                    sendRequest.hide();
                    var deleteFriend = $(".js-delete-friend-request");
                    deleteFriend.data('uuid', data.friend_request_id);
                    deleteFriend.removeAttr("disabled");
                    deleteFriend.show();
                }
            },
            error: function (XMLHttpRequest) {
                if (XMLHttpRequest.status === 500) {
                    sendRequest.removeAttr("disabled");
                    $("#server_error").show();
                }
            }
        });
    });
    $(".js-hover-overlay-activate").mouseenter(function () {
        var $this = $(this),
            overlay = $this.parent().parent().find(".sb-overlay");
        overlay.height($this.height());
        overlay.fadeIn('fast');
    });
    $(".sb-overlay").mouseleave(function () {
        $(this).fadeOut('fast');
        $(".sb-profile-not-friend-element-image").removeClass("active");
    });
});
