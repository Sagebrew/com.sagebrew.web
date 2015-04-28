$( document ).ready(function() {
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            ajaxSecurity(xhr, settings)
        }
    });
    $.ajax({
        xhrFields: {withCredentials: true},
        type: "GET",
        url: "/privilege/create/privilege/",
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function(data){
            $("#choice_wrapper").append(data['html']);
            enable_post_functionality();
        },
        error: function(XMLHttpRequest, textStatus, errorThrown) {
                if(XMLHttpRequest.status === 500){
                    $("#server_error").show();
                }
            }
    });
});