/*global $, jQuery, ajaxSecurity, getUrlParameter, errorDisplay*/
$(document).ready(function () {
    var submitButton = $("#submit_signup");
    function signupFxn() {
        submitButton.attr("disabled", "disabled");
        event.preventDefault();
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
                if (data.detail === 'success') {
                    window.location.href = "/registration/signup/confirm/";
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
    submitButton.on('click', function () {
        signupFxn();
    });
    $('#f_name').keyup(function (e) {
        if (e.which === 10 || e.which === 13) {
            signupFxn();
        }
    });
    $('#l_name').keyup(function (e) {
        if (e.which === 10 || e.which === 13) {
            signupFxn();
        }
    });
    $('#email').keyup(function (e) {
        if (e.which === 10 || e.which === 13) {
            signupFxn();
        }
    });
    $('#password').keyup(function (e) {
        if (e.which === 10 || e.which === 13) {
            signupFxn();
        }
    });
    $('#password2').keyup(function (e) {
        if (e.which === 10 || e.which === 13) {
            signupFxn();
        }
    });
    $('#birthday').keyup(function (e) {
        if (e.which === 10 || e.which === 13) {
            signupFxn();
        }
    });
});

