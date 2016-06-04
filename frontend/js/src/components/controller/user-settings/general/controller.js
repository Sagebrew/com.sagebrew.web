var requests = require('api').request,
    helpers = require('common/helpers'),
    settings = require('settings').settings,
    addresses = require('common/addresses'),
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
    var $app = $(".app-sb"),
        accountForm = document.getElementById('account-info'),
        addressForm = document.getElementById('address'),
        passwordForm = document.getElementById('password-form'),
        passwordValidationForm = $('#password-form'),
        passwordBtn = document.getElementById('js-new-password'),
        accountValidationForm = $("#account-info");
    addresses.setupAddress(validateAddressCallback);
    /*
        $imageProfileForm = $("#js-image-upload-form"),
        $previewProfileContainer = $('#js-image-preview'),
        $saveProfilePicButton = $("#js-submit-profile-picture"),
        $imageWallpaperForm = $("#js-image-wallpaper-upload-form"),
        $previewWallpaperContainer = $('#js-wallpaper-image-preview'),
        $saveWallpaperPicButton = $("#js-submit-wallpaper-picture");
    helpers.setupImageUpload($app, $imageProfileForm, $previewProfileContainer, $saveProfilePicButton, 500, 500);
    helpers.setupImageUpload($app, $imageWallpaperForm, $previewWallpaperContainer, $saveWallpaperPicButton, 500, 500, false);
    */
    validators.updateAccountValidator(accountValidationForm);
    validators.passwordValidator(passwordValidationForm);
    var addressValidationForm = addresses.setupAddress(validateAddressCallback);
    passwordValidationForm
        .on('keyup', 'input', function () {
            passwordBtn.disabled = !helpers.verifyContinue([passwordForm]);
        });
    $app
        .on('click', '#js-continue-btn', function () {
            completeAddress(addressValidationForm, addressForm);
        })
        .on('keypress', '#address input', function(event) {
            if (event.which === 13 || event.which === 10) {
                completeAddress(addressValidationForm, addressForm);
                return false; // handles event.preventDefault(), event.stopPropagation() and returnValue for IE8 and earlier
            }
        })
        .on('keypress', '#account-info input', function(event) {
            if (event.which === 13 || event.which === 10) {
                completeGeneral(accountValidationForm, accountForm);
                return false; // handles event.preventDefault(), event.stopPropagation() and returnValue for IE8 and earlier
            }
        })
        .on('click', '#submit_settings', function (event) {
            event.preventDefault();
            completeGeneral(accountValidationForm, accountForm);
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

function completeGeneral(accountValidationForm, accountForm) {
    accountValidationForm.data('formValidation').validate();
    if(accountValidationForm.data('formValidation').isValid() === true) {
        document.getElementById('sb-greyout-page').classList.remove('sb_hidden');
        var accountData = helpers.getSuccessFormData(accountForm);

        // accountData.date_of_birth = moment(accountData.date_of_birth, "MM/DD/YYYY").format();
        requests.patch({
            url: "/v1/profiles/" + settings.user.username + "/",
            data: JSON.stringify(accountData)
        })
            .done(function () {
                window.location.reload();
            });
    }
}

function completeAddress(addressValidationForm, addressForm) {
    addressValidationForm.data('formValidation').validate();
    if(addressValidationForm.data('formValidation').isValid() === true){
        addresses.submitAddress(addressForm, submitAddressCallback,
                                "/v1/profiles/" + settings.profile.username + "/");
    }
}


function validateAddressCallback() {
}

function submitAddressCallback() {
    var greyPage = document.getElementById('sb-greyout-page');
    greyPage.classList.add('sb_hidden');
    window.location.reload();
}