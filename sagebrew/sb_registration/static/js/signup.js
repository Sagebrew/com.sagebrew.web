/*global $, jQuery, ajaxSecurity, getUrlParameter, errorDisplay*/
$(document).ready(function () {
    var submitButton = $("#submit_signup");
    function signupFxn() {
        submitButton.attr("disabled", "disabled");
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "POST",
            url: "/registration/signup/",
            data: JSON.stringify({
                'first_name': $('#f_name').val(),
                'last_name': $('#l_name').val(),
                'email': $('#email').val(),
                'password': $('#password').val(),
                'password2': $('#password2').val(),
                'birthday': $('#birthday').val()
            }),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (data) {
                console.log(data);
                if (data.detail === 'success') {
                    window.location.href = "/registration/signup/confirm/";
                } else if (data.detail === 'existing success') {
                    window.location.href = "/registration/profile_info/";
                } else if (data.detail === 'redirect') {
                    window.location.href = data.url;
                } else {
                    $("#submit_signup").removeAttr("disabled");
                }
            },
            error: function (XMLHttpRequest) {
                $("#submit_signup").removeAttr("disabled");
                errorDisplay(XMLHttpRequest);
            }
        });
    }
    submitButton.on('click', function (event) {
        event.preventDefault();
        signupFxn();
    });
    $('#f_name').keypress(function (e) {
        if (e.which === 10 || e.which === 13) {
            e.preventDefault();
            signupFxn();
        }
    });
    $('#l_name').keypress(function (e) {
        if (e.which === 10 || e.which === 13) {
            e.preventDefault();
            signupFxn();
        }
    });
    $('#email').keypress(function (e) {
        if (e.which === 10 || e.which === 13) {
            e.preventDefault();
            signupFxn();
        }
    });
    $('#password').keypress(function (e) {
        if (e.which === 10 || e.which === 13) {
            e.preventDefault();
            signupFxn();
        }
    });
    $('#password2').keypress(function (e) {
        if (e.which === 10 || e.which === 13) {
            e.preventDefault();
            signupFxn();
        }
    });
    $('#birthday').keypress(function (e) {
        if (e.which === 10 || e.which === 13) {
            e.preventDefault();
            signupFxn();
        }
    });
});

