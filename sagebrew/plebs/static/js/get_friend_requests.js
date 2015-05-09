$(document).ready(function () {
    var username = $(".show_friend_request-action").data("username");
    $.ajax({
        xhrFields: {withCredentials: true},
        type: "GET",
        url: "/v1/profiles/" + username + "/friend_requests/?html=true",
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (data) {
            var container = $("#friend_requests");
            container.empty();
            container.append(data);
            respond_friend_request();
        },
        error: function(XMLHttpRequest, textStatus, errorThrown) {
            if(XMLHttpRequest.status === 500){
                $("#server_error").show();
            }
        }
    });
});