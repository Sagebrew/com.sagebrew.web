var requests = require('api').request,
    helpers = require('common/helpers'),
    settings = require('settings').settings,
    validators = require('common/validators'),
    moment = require('moment');

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
        occupationKey = "occupationKey",
        employerKey = "employerKey",
        $app = $(".app-sb"),
        donateToID = helpers.args(1),
        missionSlug = helpers.args(2),
        donationType = helpers.args(0),
        accountForm = document.getElementById('account-info'),
        addressForm = document.getElementById('address'),
        addressValidationForm = $("#address"),
        continueBtn = document.getElementById('js-continue-btn');
    $(':checkbox').radiocheck();
    validators.accountValidator($("#account-info"));
    validators.addressValidator(addressValidationForm);
    $app
        .on('change', 'input', function () {
            continueBtn.disabled = !helpers.verifyContinue([accountForm, addressForm]);
        })
        .on('click', '#js-continue-btn', function (event) {
            event.preventDefault();
            document.getElementById('sb-greyout-page').classList.remove('sb_hidden');
            var accountData = helpers.getSuccessFormData(accountForm);
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

            // If employment and occupation info is available add it to the account info
            accountData.employer_name = localStorage.getItem(employerKey);
            accountData.occupation_name = localStorage.getItem(occupationKey);

            // The backend doesn't care about the user's password matching so
            // delete the second password input we use to help ensure the user
            // doesn't put int a password they don't mean to.
            delete accountData["password2"];
            accountData.date_of_birth = moment(accountData.date_of_birth, "MM/DD/YYYY").format();
            requests.post({url: "/v1/profiles/", data: JSON.stringify(accountData)})
                .done(function () {
                    requests.post({url: "/v1/addresses/", data: JSON.stringify(addressData)})
                        .done(function () {
                            window.location.href = "/missions/" + donateToID + "/" +
                                missionSlug + "/donate/payment/";
                        })
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