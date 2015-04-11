$(document).ready(function(){
    $("#settings_form").bootstrapValidator({
        framework: 'bootstrap',
        feedbackIcons: {
            valid: 'glyphicon glyphicon-ok',
            validating: 'glyphicon glyphicon-refresh'
        },
        live: 'enabled',
        submitButtons: '#submit_settings',
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
            old_password: {
                group: 'password1',
                validators: {
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
            new_password: {
                group: 'password2',
                validators: {
                    stringLength: {
                        min: 8,
                        max: 128,
                        message: "Passwords must be between 8 and 128 characters long"
                    },
                    identical: {
                        field: 'new_password_confirm',
                        message: 'Passwords must be the same'
                    }
                }
            },
            new_password_confirm: {
                group: 'password3',
                validators: {
                    stringLength: {
                        min: 8,
                        max: 128,
                        message: "Passwords must be between 8 and 128 characters long"
                    },
                    identical: {
                        field: 'new_password',
                        message: 'Passwords must be the same'
                    }
                }
            }
        }
    })
});