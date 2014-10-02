$( document ).ready(function() {
    var password_match = false;
    $(".password2").on("keyup", function() {
        var password = $('.password').val();
        var password2 = $('.password2').val();
        if (password.length<6) {}
        else if ((password === password2) && !password_match){
            password_match = true
        }
        else {
            password_match = false
        }
    });
	$("a.submit_signup").click(function(event){
        if ($('.f_name').val()===''){
            alert('Please enter a first name')
        }
        else if ($('.l_name').val()===''){
            alert('Please enter a last name')
        }
        else if ($('.email').val()===''){
            alert('Please enter an email address')
        }
        else if (!password_match) {
            alert('Passwords must match!')
        }
        else {
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
                    window.location.href = "https://192.168.56.101/" +
                        "registration/signup/confirm/"
                }
            });
        }
	});
});

