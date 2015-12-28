/**
 * @file
 * Validators that can be reused on multiple interfaces (signup, settings, etc)
 */

/**
 * Add a validator to a account form. This manages all the fields we acquire at
 * signup.
 * @param formVal
 */
export function accountValidator(formVal) {
    formVal.formValidation({
        framework: 'bootstrap',
        /*
        Don't use icons anywhere else but if we want to add this.
        icon: {
            valid: 'fa fa-check',
            invalid: 'fa fa-times',
            validating: 'fa fa-refresh'
        },
        */
        fields: {
            firstName: {
                selector: '#first-name',
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
            lastName: {
                selector: '#last-name',
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
                selector: '#email',
                validators: {
                    notEmpty: {
                        message: "Email is required"
                    },
                    stringLength: {
                        max: 200,
                        message: "Email must not exceed 200 characters"
                    },
                    emailAddress: {
                        message: 'The value is not a valid email address'
                    }
                }
            },
            password1: {
                selector: '#password',
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
                selector: '#password2',
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
                selector: '#birthday',
                validators: {
                    date: {
                        format: 'MM/DD/YYYY',
                        message: 'The value is not a valid date'
                    },
                    notEmpty: {
                        message: "Birthday is required"
                    }
                }
            }
        }
    });
}

/**
 * Form validator for address information. This manages all of the fields we
 * associate with a given address for a user.
 * @param addressVal
 */
export function addressValidator(addressVal) {
    addressVal.formValidation({
        framework: 'bootstrap',
        /*
        Don't use icons anywhere else but if we want to add this.
        icon: {
            valid: 'fa fa-check',
            invalid: 'fa fa-times',
            validating: 'fa fa-refresh'
        },
        */
        fields: {
            street: {
                selector: '#street',
                validators: {
                    notEmpty: {
                        message: "Address is required"
                    }
                }
            },
            streetAdditional: {
                selector: '#street-additional',
                validators: {
                    stringLength: {
                        max: 128,
                        message: "Additional street info must be shorter than 128 chars"
                    }
                }
            },
            city: {
                selector: '#city',
                validators: {
                    notEmpty: {
                        message: "City is required"
                    }
                }
            },
            state: {
                selector: '#state',
                validators: {
                    notEmpty: {
                        message: "State is required"
                    }
                }
            },
            postalCode: {
                selector: '#postal-code',
                validators: {
                    notEmpty: {
                        message: "Zip Code is required"
                    }
                }
            }
        }
    });
}