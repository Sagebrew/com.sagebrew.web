/*global $*/
$(document).ready(function () {
    $.ajax({
        xhrFields: {withCredentials: true},
        type: "GET",
        url: "/v1/profiles/" + $("#reputation_total").data('username') + "/reputation/",
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (data) {
            var reputationTotal = $("#reputation_total");
            reputationTotal.append('<p id="js-change-data-container">' + data.reputation + '</p>');
        },
        error: function (XMLHttpRequest) {
            if (XMLHttpRequest.status === 500) {
                $("#server_error").show();
            }
        }
    });
});
