$(document).ready(function () {
    event.preventDefault();
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            ajax_security(xhr, settings)
        }
    });
    $.ajax({
        xhrFields: {withCredentials: true},
        type: "GET",
        url: "/v1/profiles/" + $("#reputation_total").data('username') + "/reputation/",
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (data) {
            $("#reputation_total").append("<p>" + data["reputation"] + "</p>");
        },
        error: function(XMLHttpRequest, textStatus, errorThrown) {
        if(XMLHttpRequest.status === 500){
            $("#server_error").show();
        }
    }
    });
});
