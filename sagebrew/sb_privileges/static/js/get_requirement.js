$( document ).ready(function() {
    $(".get_requirement_form").click(function (event) {
        event.preventDefault();
        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                ajax_security(xhr, settings)
            }
        });
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "GET",
            url: "/privilege/create/requirement/",
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function(data){
                $("#requirement_form_wrapper").append(data['html']);
                enable_post_functionality();
                $(".get_requirement_form").attr('disabled', 'disabled');
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                if(XMLHttpRequest.status === 500){
                    $("#server_error").show();
                }
            }
        });
    });
});