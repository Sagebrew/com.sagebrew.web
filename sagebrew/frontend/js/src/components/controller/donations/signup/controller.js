/*global google, Intercom*/
var helpers = require('common/helpers'),
    settings = require('settings').settings;

export const meta = {
    controller: "donations/signup",
    match_method: "path",
    check: [
       "^missions\/[A-Za-z0-9.@_%+-]{36}\/[A-Za-z0-9.@_%+-]{1,140}\/donate\/name"
    ]
};


/**
 * Init
 */
export function init() {

}

/**
 * Load
 */
export function load() {
    var latitudeKey = "addressLatitude",
        longitudeKey = "addressLongitude",
        countryKey = "addressCountry",
        congressionalKey = "addressCongressionalDistrict",
        validKey = "addressValid",
        originalKey = "addressOriginal",
        $app = $(".app-sb"),
        accountForm = document.getElementById('account-info');
    $("#account-info").formValidation({
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
            first_name: {
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
            last_name: {
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

    $app.on('change', '#account-info', function () {
        var formData = helpers.getSuccessFormData(accountForm);
        if (Object.keys(formData).length == accountForm.length - 1) {
            // Subtract one because we don't submit password 2
            // We have all valid fields for account info according to formValidation!
            // TODO either set some value off in storage that says all these fields are ready
            // to go or move this check to when the button gets clicked/when the user enters
            // the last pieces of info. Probably don't want to tie to "last piece of info" because
            // that could be any field on the page...
        }
    });
    var liveaddress = $.LiveAddress({
        key: settings.api.liveaddress,
        addresses: [
            {
                street: "#street",
                street2: "#street-additional",
                city: "#city",
                state: "#state",
                zipcode: "#postal-code"
            }
        ]
    });
    liveaddress.activate();
    liveaddress.on("AddressWasValid", function(event, data, previousHandler){
        if (data.response.raw[0].metadata.congressional_district === "AL") {
            localStorage.setItem(congressionalKey, 1);
        } else {
            localStorage.setItem(congressionalKey, data.response.raw[0].metadata.congressional_district);
        }
        localStorage.setItem(validKey, "valid");
        localStorage.setItem(latitudeKey, data.response.raw[0].metadata.latitude);
        localStorage.setItem(longitudeKey, data.response.raw[0].metadata.longitude);
        localStorage.setItem(countryKey, data.response.raw[0].metadata.county_name);
        previousHandler(event, data);
    });
    liveaddress.on("AddressWasAmbiguous", function(event, data, previousHandler){
        localStorage.setItem(validKey, "ambiguous");
        previousHandler(event, data);
    });
    liveaddress.on("AddressWasInvalid", function(event, data, previousHandler){
        localStorage.setItem(validKey, "invalid");
        previousHandler(event, data);
    });
    liveaddress.on("OriginalInputSelected", function(event, data, previousHandler){
        var valid = localStorage.getItem(validKey);
        if (valid === "invalid") {
            localStorage.setItem(originalKey, true);
        }
        previousHandler(event, data);
    });
    $('#birthday').keyup(function (e) {
        helpers.birthdayInputManager(this, e);
    });
}

/**
 * Post Load
 */
export function postload() {
    //
    // Intercom Tracking
}
