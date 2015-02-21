$( document ).ready(function() {
	$("button#beta_email_submit").click(function(event){
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
                $(".email_class").empty();
                $("#successMessage").show();
            }
        });
	});
});