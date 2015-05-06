$(document).ready(function(){
    var username = $("#user_info").data("page_user_username");

    $.ajax({
        xhrFields: {withCredentials: true},
        type: "GET",
        url: "/v1/profiles/" + username + "/senators/?html=true",
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function(data) {
            $("#senator_wrapper").append(data);
            $("#house_rep_wrapper").append(data['rep_html']);
            $.ajax({
                xhrFields: {withCredentials: true},
                type: "GET",
                url: "/v1/profiles/" + username + "/house_rep/?html=true",
                contentType: "application/json; charset=utf-8",
                dataType: "json",
                success: function(data) {
                    $("#house_rep_wrapper").append(data);
                },
                error: function(XMLHttpRequest, textStatus, errorThrown) {
                    if(XMLHttpRequest.status === 500){
                        $("#server_error").show();
                    }
                }
            });
        },
        error: function(XMLHttpRequest, textStatus, errorThrown) {
            if(XMLHttpRequest.status === 500){
                $("#server_error").show();
            }
        }
    });
});