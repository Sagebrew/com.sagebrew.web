$( document ).ready(function() {
    var username = $(".show_notifications-action").data("username");
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
                ajax_security(xhr, settings)
            }
    });
    $.ajax({
        xhrFields: {withCredentials: true},
        type: "GET",
        url: "/v1/profiles/" + username + "/notifications/?html=true",
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (data) {
            var notification_div = $('#notification_wrapper');
            notification_div.append(data);
        },
        error: function(XMLHttpRequest, textStatus, errorThrown) {
            if(XMLHttpRequest.status === 500){
                $("#server_error").show();
            }
        }
    });
});
