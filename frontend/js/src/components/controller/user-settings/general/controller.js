var requests = require('api').request,
    helpers = require('common/helpers'),
    settings = require('settings').settings,
    validators = require('common/validators');

export const meta = {
    controller: "user-settings/general",
    match_method: "path",
    check: [
       "^user/settings$"
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
    // TODO need to see if we can reuse some of the code from donation signup
    // Very similiar especially when it comes to address.
    var latitudeKey = "addressLatitude",
        longitudeKey = "addressLongitude",
        countryKey = "addressCountry",
        congressionalKey = "addressCongressionalDistrict",
        validKey = "addressValid",
        originalKey = "addressOriginal",
        $app = $(".app-sb"),
        addressID = document.getElementById('address-id').dataset.id,
        accountForm = document.getElementById('account-info'),
        addressForm = document.getElementById('address'),
        passwordForm = document.getElementById('password-form'),
        addressValidationForm = $("#address"),
        passwordValidationForm = $('#password-form'),
        continueBtn = document.getElementById('js-continue-btn'),
        passwordBtn = document.getElementById('js-new-password');
    validators.updateAccountValidator($("#account-info"));
    validators.addressValidator(addressValidationForm);
    validators.passwordValidator(passwordValidationForm);
    passwordValidationForm
        .on('keyup', 'input', function () {
            passwordBtn.disabled = !helpers.verifyContinue([passwordForm]);
        });
    addressValidationForm
        .on('keyup', 'input', function () {
            continueBtn.disabled = !helpers.verifyContinue([addressForm]);
        });
    $app
        .on('keypress', '#street', function() {
            var postalCode = document.getElementById('postal-code');
            postalCode.value = "";
            var parentPostalCode = helpers.findAncestor(postalCode, 'form-group');
            parentPostalCode.classList.remove('has-success');

        })
        .on('click', '#js-continue-btn', function () {
            var addressData = helpers.getSuccessFormData(addressForm);

            // Add the additional address fields we get dynamically from smarty
            // streets
            var verify = localStorage.getItem(validKey),
                validated;
            validated = verify === "valid";
            addressData.validated = validated;
            addressData.latitude = localStorage.getItem(latitudeKey);
            addressData.longitude = localStorage.getItem(longitudeKey);
            addressData.country = localStorage.getItem(countryKey);
            addressData.congressional_district = localStorage.getItem(congressionalKey);
            requests.put({url: "/v1/addresses/" + addressID + "/", data: JSON.stringify(addressData)})
                .done(function () {
                    window.location.reload();
                });
        })
        .on('click', '#submit_settings', function (event) {
            event.preventDefault();
            document.getElementById('sb-greyout-page').classList.remove('sb_hidden');
            var accountData = helpers.getSuccessFormData(accountForm);

            // accountData.date_of_birth = moment(accountData.date_of_birth, "MM/DD/YYYY").format();
            requests.patch({url: "/v1/profiles/" + settings.user.username + "/", data: JSON.stringify(accountData)})
                .done(function () {
                    window.location.reload();
                });
        })
        .on('click', '#js-new-password', function (event) {
            event.preventDefault();
            document.getElementById('sb-greyout-page').classList.remove('sb_hidden');
            var passwordData = helpers.getSuccessFormData(passwordForm);
            requests.patch({url: "/v1/profiles/" + settings.user.username + "/", data: JSON.stringify(passwordData)})
                .done(function () {
                    window.location.reload();
                });
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
        // Revalidate the form so that we get has-success classess added to all
        // the valid fields. This way we can use verifyContinue properly
        addressValidationForm.formValidation('revalidateField', 'street');
        addressValidationForm.formValidation('revalidateField', 'streetAdditional');
        addressValidationForm.formValidation('revalidateField', 'city');
        addressValidationForm.formValidation('revalidateField', 'state');
        addressValidationForm.formValidation('revalidateField', 'postalCode');
        // If the street-additional field is blank then replace it with an empty
        // space so that we don't have green placeholder text in the field.
        // TODO we may want to spend some more time on rectifying this with css
        // rather than this hack (change the placeholder text back to grey within
        // has-success class.
        if(document.getElementById('street-additional').value === ""){
            document.getElementById('street-additional').value = " ";
        }
        continueBtn.disabled = !helpers.verifyContinue([accountForm, addressForm]);
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