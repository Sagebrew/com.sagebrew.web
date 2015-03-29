$(document).ready(function(){
    var username = $("#user_info").data("page_user_username");
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            ajax_security(xhr, settings)
        }
    });
    $.ajax({
        xhrFields: {withCredentials: true},
        type: "GET",
        url: "/v1/profiles/" + username + "/public_officials/?html=true",
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function(data) {
            $("#senator_wrapper").append(data['sen_html']);
            $("#house_rep_wrapper").append(data['rep_html']);
        },
        error: function(XMLHttpRequest, textStatus, errorThrown) {
            if(XMLHttpRequest.status === 500){
                $("#server_error").show();
            }
        }
    });
});