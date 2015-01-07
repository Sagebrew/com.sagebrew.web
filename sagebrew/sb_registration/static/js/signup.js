$( document ).ready(function() {
	$("button.submit_signup").click(function(event){
        event.preventDefault();
        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                ajax_security(xhr, settings)
            }
        });
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "POST",
            url: "/registration/signup/",
            data: JSON.stringify({
                'first_name': $('.f_name').val(),
                'last_name': $('.l_name').val(),
                'email': $('.email').val(),
                'password': $('.password').val(),
                'password2': $('.password2').val()
            }),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (data) {
                if (data['detail'] === 'A user with this email already exists!'){
                    alert(data['detail'])
                }
                else if (data['detail'] === "If you are using a .gov email address please follow this link, or use a personal email address."){
                    alert(data['detail'])
                }
                else {
                    window.location.href = "/registration/signup/confirm/";
                }
            }
        });
	});
});

