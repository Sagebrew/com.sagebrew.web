var requests = require('api').request,
    helpers = require('common/helpers'),
    settings = require('settings').settings,
    validators = require('common/validators');

export function setupAddress(validateCallback) {
    var addressValidationForm = $("#address");
    validators.addressValidator(addressValidationForm);
    validateAddress(addressValidationForm, validateCallback);
    $(".app-sb")
        .on('keypress', '#street', function() {
            var postalCode = document.getElementById('postal-code');
            postalCode.value = "";
            var parentPostalCode = helpers.findAncestor(postalCode, 'form-group');
            parentPostalCode.classList.remove('has-success');
        }).on('keyup', '#postal-code', function () {
            addressValidationForm.formValidation('revalidateField', 'street');
            addressValidationForm.formValidation('revalidateField', 'streetAdditional');
            addressValidationForm.formValidation('revalidateField', 'city');
            addressValidationForm.formValidation('revalidateField', 'state');
        });
}

function validateAddress(addressValidationForm, callbackFunction) {
    var latitudeKey = "addressLatitude",
        longitudeKey = "addressLongitude",
        countryKey = "addressCountry",
        congressionalKey = "addressCongressionalDistrict",
        originalKey = "addressOriginal",
        validKey = "addressValid";
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
        callbackFunction();
        
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
}


export function submitAddress(addressForm, callbackFunction) {
    var latitudeKey = "addressLatitude",
        longitudeKey = "addressLongitude",
        countryKey = "addressCountry",
        congressionalKey = "addressCongressionalDistrict",
        validKey = "addressValid",
        greyPage = document.getElementById('sb-greyout-page'),
        addressData = helpers.getSuccessFormData(addressForm),
        verify = localStorage.getItem(validKey),
        validated;
    greyPage.classList.remove('sb_hidden');
    validated = verify === "valid";
    addressData.validated = validated;
    addressData.latitude = localStorage.getItem(latitudeKey);
    addressData.longitude = localStorage.getItem(longitudeKey);
    addressData.country = localStorage.getItem(countryKey);
    addressData.congressional_district = localStorage.getItem(congressionalKey);
    requests.post({url: "/v1/addresses/", data: JSON.stringify(addressData)})
        .done(function (data) {
            greyPage.classList.add('sb_hidden');
            callbackFunction(data);
        });
}