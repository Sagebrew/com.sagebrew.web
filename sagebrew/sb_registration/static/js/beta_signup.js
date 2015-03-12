$( document ).ready(function() {
	$("button#beta_email_submit").click(function(event){
        $("button#beta_email_submit").attr('disabled', 'disabled');
        event.preventDefault();
        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                ajax_security(xhr, settings)
            }
        });
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "POST",
            url: "/registration/beta/signup/",
            data: JSON.stringify({
                'email': $("#beta_email_input").val()
            }),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (data) {
                $("#signup_wrapper").empty();
                $("#successMessage").show();
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                if(XMLHttpRequest.status === 409) {
                    $("#signup_wrapper").empty();
                    $("#user_exists").show();
                } else if(XMLHttpRequest.status === 500){
                    $("#signup_wrapper").empty();
                    $("#server_error").show();
                }
            }
        });
	});
});