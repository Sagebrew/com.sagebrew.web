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
        addressValidationForm = $("#address"),
        passwordValidationForm = $('#password-form'),
        continueBtn = document.getElementById('js-continue-btn'),
        passwordBtn = document.getElementById('js-new-password');
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
    validators.updateAccountValidator($("#account-info"));
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
        .on('click', '#js-continue-btn', function () {
            addresses.submitAddress(addressForm, submitAddressCallback);
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


function validateAddressCallback() {
    var accountForm = document.getElementById('account-info'),
        continueBtn = document.getElementById('js-continue-btn'),
        addressForm = document.getElementById('address');

    continueBtn.disabled = !helpers.verifyContinue([accountForm, addressForm]);
}

function submitAddressCallback() {
    window.location.reload();
}