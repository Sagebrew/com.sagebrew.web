/*global $, jQuery, ajaxSecurity*/
$(document).ready(function () {
    var campaign_id = $("#js-campaign_id").data('object_uuid'),
        username = $("#js-campaign_id").data('username');
    $.ajax({
        xhrFields: {withCredentials: true},
        type: "GET",
        url: "/v1/campaigns/" + campaign_id + "/possible_helpers/?html=true",
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