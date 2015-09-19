/*global $*/
$(document).ready(function () {
    $(".show-reputation-action").on("click", function () {
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "PUT",
            url: "/v1/me/",
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            data: JSON.stringify({
                "reputation_update_seen": true
            }),
            success: function (data) {
            }
        });
    });
});