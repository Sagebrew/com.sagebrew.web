$( document ).ready(function() {
    // TODO This fails after the first attempt and doesn't reset
    // Should reset it in failure or come up with better process
    var password_match = false;
    var password_too_large = false;
    var password_too_small = false;
    $(".password2").on("keyup", function() {
        var password = $('.password').val();
        var password2 = $('.password2').val();
        if (password.length > 5) {
            if(password.length < 57) {
                password_match = password === password2;
            } else {
                password_too_large = true;
            }
        } else {
            password_too_small = true;
        }
    });
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
                else {
                    window.location.href = "/registration/signup/confirm/";
                }
            }
        });
	});
});

