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
                    }
                }
            },
            password2: {
                selector: '#password2',
                validators: {
                    notEmpty: {
                        message: "Password 2 is required"
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


export function updateAccountValidator(formVal) {
    formVal.formValidation({
        framework: 'bootstrap',
        fields: {
            firstName: {
                selector: '#first-name',
                validators: {
                    stringLength: {
                        max: 30,
                        message: "First Name must not exceed 30 characters"
                    },
                    notEmpty: {
                        message: "First Name is required"
                    }
                }
            },
            lastName: {
                selector: '#last-name',
                validators: {
                    stringLength: {
                        max: 30,
                        message: "Last Name must not exceed 30 characters"
                    },
                    notEmpty: {
                        message: "Last Name is required"
                    }
                }
            },
            email: {
                selector: '#email',
                validators: {
                    stringLength: {
                        max: 200,
                        message: "Email must not exceed 200 characters"
                    },
                    emailAddress: {
                        message: 'The value is not a valid email address'
                    },
                    notEmpty: {
                        message: "Email is required"
                    }
                }
            },
            birthday: {
                selector: '#birthday',
                validators: {
                    date: {
                        format: 'MM/DD/YYYY',
                        message: 'The value is not a valid date'
                    }
                }
            }
        }
    });
}

export function passwordValidator(passwordVal) {
    passwordVal.formValidation({
        framework: 'bootstrap',
        fields: {
            oldPassword: {
                selector: '#password',
                validators: {
                    notEmpty: {
                        message: "Please provide your old password"
                    }
                }
            },
            password1: {
                selector: '#new-password',
                validators: {
                    notEmpty: {
                        message: "Password is required"
                    },
                    stringLength: {
                        min: 8,
                        max: 128,
                        message: "Passwords must be between 8 and 128 characters long"
                    }
                }
            },
            password2: {
                selector: '#password2',
                validators: {
                    notEmpty: {
                        message: "Password 2 is required"
                    },
                    identical: {
                        field: 'password1',
                        message: 'Passwords must be the same'
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
        fields: {
            street: {
                selector: '#street',
                validators: {
                    notEmpty: {
                        message: "Address is required"
                    },
                    stringLength: {
                        max: 128,
                        message: "Address info must be shorter than 128 characters"
                    }
                }
            },
            streetAdditional: {
                selector: '#street-additional',
                validators: {
                    stringLength: {
                        max: 128,
                        message: "Additional street info must be shorter than 128 characters"
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
                    },
                    stringLength: {
                        max: 2,
                        message: "State field must be shorter than 2 characters"
                    }
                }
            },
            postalCode: {
                selector: '#postal-code',
                validators: {
                    notEmpty: {
                        message: "Zip Code is required"
                    },
                    stringLength: {
                        max: 15,
                        message: "Zip Code must be shorter than 15 characters"
                    }
                }
            }
        }
    });
}

export function editUpdateValidator(updateVal) {
    updateVal.formValidation({
        framework: 'bootstrap',
        live: 'enabled',
        fields: {
            title: {
                selector: '#title_input',
                validators: {
                    notEmpty: {
                        message: "Title is required"
                    },
                    stringLength: {
                        min: 5,
                        max: 140,
                        message: "Title must be between 5 and 140 characters long"
                    }
                }
            },
            content: {
                selector: '#update_content_input',
                validators: {
                    notEmpty: {
                        message: "Content is required"
                    }
                }
            }
        }
    });
}


export function solutionValidator (solutionForm) {
    solutionForm.formValidation({
        framework: 'bootstrap',
        live: 'enabled',
        fields: {
            content: {
                selector: 'js-solution-markdown',
                validators: {
                    notEmpty: {
                        message: "Content is required"
                    },
                    stringLength: {
                        min: 15,
                        message: "Solutions must be at least 15 characters long"
                    }
                }
            }
        }
    });
}


export function missionManageValidator(manageForm, aboutLengthLimit) {
    manageForm.formValidation({
        framework: 'bootstrap',
        live: 'enabled',
        fields: {
            title: {
                selector: '#title',
                validators: {
                    stringLength: {
                        max: 240,
                        message: ' '
                    },
                    notEmpty: {
                        message: 'You must have a title'
                    }
                }
            },
            about: {
                selector: '#about',
                validators: {
                    stringLength: {
                        max: aboutLengthLimit,
                        message: ' '
                    }
                }
            },
            website: {
                selector: "#website",
                validators: {
                    callback: {
                        callback: function (value) {
                            if ($.trim(value).indexOf("http://") === 0 || $.trim(value).indexOf("https://") === 0 || $.trim(value) === "") {
                                return true;
                            } else {
                                return {
                                    valid: false,
                                    message: 'Please enter a valid fully qualified url including "http://" or "https://"'
                                };
                            }
                        }
                    }
                }
            },
            facebook: {
                selector: "#facebook-social-address",
                validators: {
                    callback: {
                        callback: function (value) {
                            if ($.trim(value).indexOf("https://www.facebook.com/") === 0 || $.trim(value).indexOf("http://www.facebook.com/") === 0 || $.trim(value).indexOf("www.facebook.com/") === 0 || $.trim(value) === "") {
                                return true;
                            } else {
                                return {
                                    valid: false,
                                    message: 'Please enter a valid fully qualified Facebook url'
                                };
                            }
                        }
                    }
                }
            },
            twitter: {
                selector: "#twitter-social-address",
                validators: {
                    callback: {
                        callback: function (value) {
                            if ($.trim(value).indexOf("https://twitter.com/") === 0 || $.trim(value).indexOf("https://www.twitter.com/") === 0 || $.trim(value).indexOf("www.twitter.com/") === 0 || $.trim(value) === "") {
                                return true;
                            } else {
                                return {
                                    valid: false,
                                    message: 'Please enter a valid fully qualified Twitter url'
                                };
                            }
                        }
                    }
                }
            },
            linkedin: {
                selector: "#linkedin-social-address",
                validators: {
                    callback: {
                        callback: function (value) {
                            if ($.trim(value).indexOf("https://www.linkedin.com/") === 0 || $.trim(value).indexOf("http://www.linkedin.com/") === 0 || $.trim(value).indexOf("www.linkedin.com/") === 0 || $.trim(value) === "") {
                                return true;
                            } else {
                                return {
                                    valid: false,
                                    message: 'Please enter a valid fully qualified LinkedIn url'
                                };
                            }
                        }
                    }
                }
            },
            youtube: {
                selector: "#youtube-social-address",
                validators: {
                    callback: {
                        callback: function (value) {
                            if ($.trim(value).indexOf("https://www.youtube.com/") === 0 || $.trim(value).indexOf("www.youtube.com/") === 0 || $.trim(value).indexOf("https://youtu.be/") === 0 || $.trim(value).indexOf("www.youtube.com/") === 0 || $.trim(value).indexOf("http://youtu.be/") === 0 || $.trim(value).indexOf("www.youtu.be/") === 0 || $.trim(value) === ""){
                                return true;
                            } else {
                                return {
                                    valid: false,
                                    message: 'Please enter a valid fully qualified Youtube url'
                                };
                            }
                        }
                    }
                }
            }
        }
    });
}

export function updateValidator(updateForm) {
    updateForm.formValidation({
        framework: 'bootstrap',
        live: 'enabled',
        fields: {
            title: {
                selector: '#js-update-title',
                validators: {
                    stringLength: {
                        max: 128,
                        min: 5,
                        message: 'Title must be between 5 and 128 characters long'
                    }
                }
            }
        }
    });
}

export function campaignFinanceValidator(formVal) {
    formVal.formValidation({
        framework: 'bootstrap',
        fields: {
            employerName: {
                selector: '#employer-name',
                validators: {
                    stringLength: {
                        max: 240,
                        message: "Employer name may not exceed 240 characters"
                    }
                }
            },
            occupationName: {
                selector: '#occupation-name',
                validators: {
                    stringLength: {
                        max: 240,
                        message: "Occupation name must not exceed 240 characters"
                    }
                }
            },
            campaignFinanceForm: {
                selector: '.campaign-finance-form',
                validators: {
                    callback: {
                        message: '',
                        callback: function(value, validator) {
                            var retired = document.getElementById('retired-or-not-employed'),
                                isEmpty = true,
                                // Get the list of fields
                                $fields = validator.getFieldElements('campaignFinanceForm');
                            // Check if both Employer name and Job title are filled out
                            if($fields.eq(0).val() !== '' && $fields.eq(1).val() !== '' &&
                                    $fields.eq(0).val() !== null && $fields.eq(1).val() !== null) {
                                isEmpty = false;
                            }
                            if(retired.checked !== false) {
                                isEmpty = false;
                            }

                            // Check if Employer Name, Job Title, and Unemployed are all checked
                            if(($fields.eq(0).val().length > 0 || $fields.eq(1).val().length > 0) && retired.checked === true) {
                                return {
                                    valid: false,
                                    message: "Please only indicate your Employment " +
                                    "Information or that you are Retired or not employed"
                                };
                            }
                            if (!isEmpty) {
                                // Update the status of callback validator for all fields
                                validator.updateStatus('campaignFinanceForm', validator.STATUS_VALID, 'callback');
                                return true;
                            }
                            return {
                                valid: false,
                                message: "Please indicate your Employer Name and Job " +
                                "Title or that you are Retired or not employed"
                            };
                        }
                    }
                }
            }
        }
    });
}


export function bankAccountValidator(bankAccountVal) {
    bankAccountVal.formValidation({
        framework: 'bootstrap',
        fields: {
            accountType: {
                selector: '#account-type',
                validators: {
                    business: {
                        enabled: true,
                        message: "Setup account for organization or business"
                    },
                    individual: {
                        enabled: false,
                        message: "Setup account as yourself"
                    }
                }
            },
            socialSecurityNumber: {
                selector: '#ssn',
                validators: {
                    notEmpty: {
                        message: "This value is require"
                    },
                    stringLength: {
                        max: 24,
                        message: "This value cannot be longer than 24 characters"
                    }
                }
            },
            bankAccountOwnerName: {
                selector: '#account-owner',
                validators: {
                    notEmpty: {
                        message: "This value is require"
                    },
                    stringLength: {
                        max: 240,
                        message: "This value cannot be longer than 240 characters"
                    }
                }
            },
            einOfAccountOwner: {
                selector: '#ein',
                validators: {
                    notEmpty: {
                        message: "This value is required"
                    },
                    ein: {
                        message: 'The value is not valid EIN'
                    }
                }
            },
            routingNumber: {
                selector: '#routing-number',
                validators: {
                    notEmpty: {
                        message: "This value is required"
                    },
                    stringLength: {
                        max: 56,
                        message: "This value cannot be longer than 56 characters"
                    }
                }
            },
            bankAccountNumber: {
                selector: '#account-number',
                validators: {
                    notEmpty: {
                        message: "This value is required"
                    },
                    stringLength: {
                        max: 240,
                        message: "This value cannot be longer than 240 characters"
                    }
                }
            }
        }
    })
        .find('[name="stripe_account_type"]')
            .on('change', function() {
                var type = $(this).val();
                switch (type) {
                    case 'individual':
                        bankAccountVal
                            .formValidation('enableFieldValidators', 'bankAccountOwnerName', false, 'notEmpty')
                            .formValidation('enableFieldValidators', 'bankAccountOwnerName', false, 'stringLength')
                            .formValidation('enableFieldValidators', 'einOfAccountOwner', false, 'notEmpty')
                            .formValidation('enableFieldValidators', 'einOfAccountOwner', false, 'stringLength');
                        break;

                    case 'business':
                        bankAccountVal
                            .formValidation('enableFieldValidators', 'bankAccountOwnerName', true, 'notEmpty')
                            .formValidation('enableFieldValidators', 'bankAccountOwnerName', true, 'stringLength')
                            .formValidation('enableFieldValidators', 'einOfAccountOwner', true, 'notEmpty')
                            .formValidation('enableFieldValidators', 'einOfAccountOwner', true, 'stringLength');
                        bankAccountVal.data('formValidation').validate();
                        break;
                }
            })
            .end();
}