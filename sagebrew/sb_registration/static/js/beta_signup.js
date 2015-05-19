/*global $, jQuery, guid, Croppic, alert, errorDisplay*/
$(document).ready(function () {
    "use strict";
    function submitBeta() {
        $("button#beta_email_submit").attr('disabled', 'disabled');
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "POST",
            url: "/registration/beta/signup/",
            data: JSON.stringify({
                'email': $("#beta_email_input").val()
            }),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function () {
                $("#signup_wrapper").empty();
                $("#successMessage").show();
            },
            error: function (XMLHttpRequest) {
                errorDisplay(XMLHttpRequest);
                if (XMLHttpRequest.status === 409) {
                    $("#signup_wrapper").empty();
                    $("#user_exists").show();
                } else if (XMLHttpRequest.status === 500) {
                    $("#signup_wrapper").empty();
                }
            }
        });
    }
    $("button#beta_email_submit").click(function (event) {
        event.preventDefault();
        submitBeta();
    });
    $("#beta_email_input").keyup(function (e) {
        if (e.which === 10 || e.which === 13) {
            e.preventDefault();
            submitBeta();
        }
    });
});