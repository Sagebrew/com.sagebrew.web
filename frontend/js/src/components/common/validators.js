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


export function updateAccountValidator(formVal) {
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
                    stringLength: {
                        max: 30,
                        message: "First Name must not exceed 30 characters"
                    }
                }
            },
            lastName: {
                selector: '#last-name',
                validators: {
                    stringLength: {
                        max: 30,
                        message: "Last Name must not exceed 30 characters"
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
                    },
                    stringLength: {
                        max: 128,
                        message: "Address info must be shorter than 128 chars"
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
                    },
                    stringLength: {
                        max: 2,
                        message: "Additional street info must be shorter than 128 chars"
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
                        message: "Zip Code must be shorter than 128 chars"
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


export function questManageValidator(manageForm) {
    manageForm.formValidation({
        framework: 'bootstrap',
        live: 'enabled',
        fields: {
            about: {
                selector: '#about',
                validators: {
                    stringLength: {
                        max: 128,
                        message: 'About section must be less than 128 characters'
                    }
                }
            }
        }
    });
}


export function missionManageValidator(manageForm) {
    manageForm.formValidation({
        framework: 'bootstrap',
        live: 'enabled',
        fields: {
            about: {
                selector: '#about',
                validators: {
                    stringLength: {
                        max: 255,
                        message: 'About section must be less than 255 characters'
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
                        message: 'Title must be between %s and %s'
                    }
                }
            }
        }
    });
}