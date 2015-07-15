/*global $, jQuery, ajaxSecurity*/
$(document).ready(function () {
    var campaign_id = $("#js-campaign_id").data('object_uuid'),
        username = $("#js-campaign_id").data('username');
    $.ajax({
        xhrFields: {withCredentials: true},
        type: "GET",
        url: "/v1/profiles/" + username + "/friends/?html=true",
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (data) {
            if (data.count === 0){
                $("#friend_wrapper").append("<div><h3>Please use search to find your friends :)</h3></div>");
            }
            $.each(data.results, function (i, l) {
                $("#friend_wrapper").append(l);
            });
            $("#next_url").data('url', data.next);
        },
        error: function (XMLHttpRequest) {
            if (XMLHttpRequest.status === 500) {
                $("#server_error").show();
            }
        }
    });
});