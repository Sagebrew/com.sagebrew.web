var addresses = require('common/addresses');

export const meta = {
    controller: "registration/profile_information",
    match_method: "path",
    check: [
        "^registration/profile_information$"
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
    var $app = $(".app-sb"),
        addressForm = document.getElementById('address');
    var addressValidationForm = addresses.setupAddress(validateAddressCallback);
    $app
        .on('click', '#js-continue-btn', function (event) {
            event.preventDefault();
            completeAddress(addressValidationForm, addressForm);
            return false;
        }).on('keypress', '#address input', function(event) {
            if (event.which === 13 || event.which === 10) {
                completeAddress(addressValidationForm, addressForm);
                return false; // handles event.preventDefault(), event.stopPropagation() and returnValue for IE8 and earlier
            }
        });
}

/**
 * Post Load
 */
export function postload() {
    //
    // Intercom Tracking
}


function completeAddress(addressValidationForm, addressForm) {
    "use strict";
    addressValidationForm.data('formValidation').validate();
    if(addressValidationForm.data('formValidation').isValid() === true) {
        document.getElementById('sb-greyout-page').classList.remove('sb_hidden');
        addresses.submitAddress(addressForm, submitAddressCallback);
    }
}


function validateAddressCallback() {
}

function submitAddressCallback() {
    window.location.href = "/registration/interests/";
}