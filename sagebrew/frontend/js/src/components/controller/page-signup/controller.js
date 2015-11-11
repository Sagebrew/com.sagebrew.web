/* global wistiaJQuery */
/**
 * @file
 * Signup Page... This is actually the homepage for anon users.
 */
var request = require('api').request;

function signupFormValidation() {
       $("#signupForm").formValidation({
        framework: 'bootstrap',
        icon: {
            valid: 'glyphicon glyphicon-ok',
            validating: 'glyphicon glyphicon-refresh'
        },
        live: 'enabled',
        button: {
            selector: '#submit_signup'
        },
        fields: {
            first_name: {
                row: 'fname',
                validators: {
                    notEmpty: {
                        message: "First Name is Required"
                    },
                    stringLength: {
                        max: 30,
                        message: "First Name must not exceed 30 characters"
                    }
                }
            },
            last_name: {
                row: 'lname',
                validators: {
                    notEmpty: {
                        message: "Last Name is Required"
                    },
                    stringLength: {
                        max: 30,
                        message: "Last Name must not exceed 30 characters"
                    }
                }
            },
            email: {
                row: 'email_class',
                validators: {
                    notEmpty: {
                        message: "Email is required"
                    },
                    stringLength: {
                        max: 200,
                        message: "Email must not exceed 200 characters"
                    }
                }
            },
            password1: {
                row: 'p1',
                validators: {
                    notEmpty: {
                        message: "Password is required"
                    },
                    stringLength: {
                        min: 8,
                        max: 128,
                        message: "Passwords must be between 8 and 128 characters long"
                    },
                    identical: {
                        field: 'password2',
                        message: 'Passwords must be the same'
                    }
                }
            },
            password2: {
                row: 'p2',
                validators: {
                    notEmpty: {
                        message: "Password 2 is required"
                    },
                    stringLength: {
                        min: 8,
                        max: 128,
                        message: "Passwords must be between 8 and 128 characters long"
                    },
                    identical: {
                        field: 'password1',
                        message: 'Passwords must be the same'
                    }
                }
            },
            birthday: {
                row: 'bday',
                validators: {
                    date: {
                        format: 'MM/DD/YYYY',
                        message: 'The value is not a valid date'
                    },
                    notEmpty: {
                        message: "Birthdate is required"
                    }
                }
            }
        }
    });
}

function submitSignup() {
    var submitButton = $("#submit_signup");
    submitButton.attr("disabled", "disabled");
    request.post({
        url: "/registration/signup/",
        data: JSON.stringify({
            'first_name': $('#f_name').val(),
            'last_name': $('#l_name').val(),
            'email': $('#email').val(),
            'password': $('#password').val(),
            'password2': $('#password2').val(),
            'birthday': $('#birthday').val()
        })})
        .done(function(data) {
            if (data.detail === 'success') {
                window.location.href = "/registration/signup/confirm/";
            } else if (data.detail === 'existing success') {
                window.location.href = "/registration/profile_information/";
            } else if (data.detail === 'redirect') {
                window.location.href = data.url;
            } else {
                $("#submit_signup").removeAttr("disabled");
            }
        })
        .fail(function() {
            $("#submit_signup").removeAttr("disabled");
        });
}

/**
 * Init.
 */
export function init() {

}

/**
 * Load
 */
export function load() {

    //
    // Form Validation
    signupFormValidation();

    //
    // Actual signup form.
    $("#submit_signup").on('click', function (event) {
        event.preventDefault();
        submitSignup();
    });

    $('#signupForm input').keypress(function (e) {
        if (e.which === 10 || e.which === 13) {
            e.preventDefault();
            submitSignup();
        }
    });

    //
    // Background Video
    var vid = document.getElementById("bgvid");
    function vidFade() {
        vid.classList.add("stopfade");
    }

    vid.addEventListener('ended', function () {
        // only functional if "loop" is removed
        vid.pause();
        // to capture IE10
        vidFade();
    });
    wistiaJQuery(document).bind("wistia-popover", function(event, iframe) {
        vid.pause();
        iframe.wistiaApi.time(0).play();
    });
    wistiaJQuery(document).bind("wistia-popover-close", function() {
        vid.play();
    });

    //
    //Birthday input in signup form.
    $('#birthday').keyup(function (e) {
        var temp;
        if (e.keyCode !== 193 && e.keyCode !== 111) {
            if (e.keyCode !== 8) {
                if ($(this).val().length === 2) {
                    $(this).val($(this).val() + "/");
                } else if ($(this).val().length === 5) {
                    $(this).val($(this).val() + "/");
                }
            } else {
                temp = $(this).val();
                if ($(this).val().length === 5) {
                    $(this).val(temp.substring(0, 4));
                } else if ($(this).val().length === 2) {
                    $(this).val(temp.substring(0, 1));
                }
            }
        } else {
            temp = $(this).val();
            var tam = $(this).val().length;
            $(this).val(temp.substring(0, tam-1));
        }
    });
}