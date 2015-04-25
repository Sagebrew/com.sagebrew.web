/*global $, jQuery, ajax_security, getUrlParameter*/
$(document).ready(function () {
    "use strict";
    var submitArea = $("#submit_login");
    function loginFxn() {
        submitArea.attr("disabled", "disabled");
        var next = "";
        try {
            next = getUrlParameter('next');
        } catch (err) {
            next = "";
        }
        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                ajax_security(xhr, settings);
            }
        });
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "POST",
            url: "/registration/login/api/",
            data: JSON.stringify({
                'email': $('.email').val(),
                'password': $('.password').val()
            }),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (data) {
                if (data.detail === 'success' && next !== undefined) {
                    window.location.href = next;
                } else if (data.detail === 'success') {
                    window.location.href = data.url;
                }
            },
            error: function (XMLHttpRequest) {
                alert(XMLHttpRequest.responseJSON.detail);
                submitArea.removeAttr("disabled");
            }
        });
    }
    submitArea.on('click', function () {
        loginFxn();
    });

    $("#password_input").keyup(function (e) {
        if (e.which === 10 || e.which === 13) {
            loginFxn();
        }
    });
    $("#email_input").keyup(function (e) {
        if (e.which === 10 || e.which === 13) {
            loginFxn();
        }
    });
});