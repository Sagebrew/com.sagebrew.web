/*global $, jQuery, ajaxSecurity*/
$(document).ready(function () {
    "use strict";
    $(".delete_friend_request-action").click(function (event) {
        event.preventDefault();
        var deleteAction = $(".delete_friend_request-action"),
            objectUUID = $(this).data('uuid');
        deleteAction.attr("disabled", "disabled");

        $.ajax({
            xhrFields: {withCredentials: true},
            type: "DELETE",
            url: "/v1/friend_requests/" + objectUUID + "/",
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function () {
                $(".delete_friend_request-action").hide();
                var friendAction = $(".send_friend_request-action");
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
