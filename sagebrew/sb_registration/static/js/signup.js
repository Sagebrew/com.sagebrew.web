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
	$("a.submit_signup").click(function(event){
        if ($('.f_name').val() === ''){
            alert('Please enter a first name')
        }
        else if ($('.l_name').val()===''){
            alert('Please enter a last name')
        }
        else if ($('.email').val()===''){
            alert('Please enter an email address')
        }
        else if (password_too_small){
            alert('Passwords must be at least 6 characters long')
        }
        else if (password_too_large){
            alert('Passwords must be no larger than 56 characters long')
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

