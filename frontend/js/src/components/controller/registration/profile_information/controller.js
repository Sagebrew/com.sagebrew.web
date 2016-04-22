var helpers = require('common/helpers'),
    addresses = require('common/addresses');

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
        continueBtn = document.getElementById('js-continue-btn'),
        addressForm = document.getElementById('address');
    addresses.setupAddress(validateAddressCallback);
    $app
        .on('keyup', 'input', function () {
            continueBtn.disabled = !helpers.verifyContinue([addressForm]);
        })
        .on('click', '#js-continue-btn', function (event) {
            event.preventDefault();
            document.getElementById('sb-greyout-page').classList.remove('sb_hidden');
            addresses.submitAddress(addressForm, submitAddressCallback);
        });
}

/**
 * Post Load
 */
export function postload() {
    //
    // Intercom Tracking
}


function validateAddressCallback() {
    var continueBtn = document.getElementById('js-continue-btn'),
        addressForm = document.getElementById('address');

    continueBtn.disabled = !helpers.verifyContinue([addressForm]);
}

function submitAddressCallback() {
    window.location.href = "/registration/interests/";
}