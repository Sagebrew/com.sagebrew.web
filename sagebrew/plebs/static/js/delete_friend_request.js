/*global $, ajaxSecurity*/
/**
 * NO LONGER USED (for real this time)
 */
$(document).ready(function () {
    "use strict";
    $(".js-delete-friend-request").click(function (event) {
        event.preventDefault();
        var deleteAction = $(".js-delete-friend-request"),
            objectUUID = $(this).data('uuid');
        deleteAction.attr("disabled", "disabled");

        $.ajax({
            xhrFields: {withCredentials: true},
            type: "DELETE",
            url: "/v1/me/sent_friend_requests/" + objectUUID + "/",
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function () {
                $(".js-delete-friend-request").hide();
                var friendAction = $(".js-send-friend-request");
                friendAction.show();
                friendAction.removeAttr("disabled");
            },
            error: function (XMLHttpRequest) {
                if (XMLHttpRequest.status === 500) {
                    $("#server_error").show();
                }
            }
        });
    });
});
