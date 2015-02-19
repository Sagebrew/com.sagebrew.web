$(document).ready(function(){
    $("#singupForm").bootstrapValidator({
        feedbackIcons: {
            valid: 'glyphicon glyphicon-ok',
            validating: 'glyphicon glyphicon-refresh'
        },
        live: 'enabled',
        submitButtons: 'button.submit_signup',
        err: "tooltip",
        fields: {
            first_name: {
                group: 'fname',
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
                group: 'lname',
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
                group: 'email_class',
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
                group: 'p1',
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
                group: 'p2',
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
                group: 'bday',
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
    })
});