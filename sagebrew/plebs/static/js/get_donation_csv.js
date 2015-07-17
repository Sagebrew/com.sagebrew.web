/*global $, jQuery, ajaxSecurity*/
$(document).ready(function () {
    $.ajax({
        xhrFields: {withCredentials: true},
        type: "GET",
        url: "/v1/campaigns/" + "tyler_wiersing" + "/donation_data/",
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (data) {
            console.log(data);
        },
        error: function (XMLHttpRequest) {
            if (XMLHttpRequest.status === 500) {
                $("#server_error").show();
            }
        }
    });
});