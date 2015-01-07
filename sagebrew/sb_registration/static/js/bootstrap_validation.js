$(document).ready(function(){
    $("#singupForm").bootstrapValidator({
        feedbackIcons: {
            valid: 'glyphicon glyphicon-ok',
            invalid: 'glyphicon glyphicon-remove',
            validating: 'glyphicon glyphicon-refresh'
        },
        live: 'enabled',
        submitButtons: 'button.submit_signup',
        fields: {
            first_name: {
                group: '.col-sm-4',
                validators: {
                    notEmpty: {
                        message: "First Name is Required"
                    },
                    stringLength: {
                        max: 200,
                        message: "First Name must not exceed 200 characters"
                    }
                }
            },
            last_name: {
                group: '.col-sm-4',
                validators: {
                    notEmpty: {
                        message: "Last Name is Required"
                    },
                    stringLength: {
                        max: 200,
                        message: "Last Name must not exceed 200 characters"
                    }
                }
            },
            email: {
                group: '.col-sm-8',
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
                group: '.col-sm-8',
                validators: {
                    notEmpty: {
                        message: "Password is required"
                    },
                    stringLength: {
                        max: 150,
                        message: "Password must not exceed 150 characters"
                    },
                    identical: {
                        field: 'password2',
                        message: 'Passwords must be the same'
                    }
                }
            },
            password2: {
                group: '.col-sm-8',
                validators: {
                    notEmpty: {
                        message: "Password 2 is required"
                    },
                    stringLength: {
                        max: 200,
                        message: "Email must not exceed 200 characters"
                    },
                    identical: {
                        field: 'password1',
                        message: 'Passwords must be the same'
                    }
                }
            },
            birthday: {
                group: '.col-sm-8',
                validators: {
                    notEmpty: {
                        message: "Birthdate is required"
                    }
                }
            }
        }
    })
});