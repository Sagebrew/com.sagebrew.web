/*global Stripe*/
var requests = require('api').request,
    helpers = require('common/helpers'),
    validators = require('common/validators'),
    addresses = require('common/addresses'),
    settings = require('settings').settings;

export const meta = {
    controller: "mission/registration/account-setup",
    match_method: "path",
    check: [
       "^missions/account$"
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
        bankAccountForm = document.getElementById('banking-form'),
        addressForm = document.getElementById('address'),
        bankAccountValidationForm = $(bankAccountForm);
    validators.bankAccountValidator(bankAccountValidationForm);
    Stripe.setPublishableKey(settings.api.stripe);
    var addressValidationForm = addresses.setupAddress(function callback() {});
    $app
        .on('click', '#js-continue-btn', function (event) {
            event.preventDefault();
            completeRegistration(addressValidationForm, addressForm,
                bankAccountValidationForm, bankAccountForm);
        }).on('keypress', '#banking-form input', function(event) {
            if (event.which === 13 || event.which === 10) {
                completeRegistration(addressValidationForm, addressForm,
                    bankAccountValidationForm, bankAccountForm);
                return false;
            }
        }).on('keypress', '#address input', function(event) {
            if (event.which === 13 || event.which === 10) {
                completeRegistration(addressValidationForm, addressForm,
                    bankAccountValidationForm, bankAccountForm);
                return false;
            }
        })
        .on('change', '#account-type', function() {
            var $this = $(this),
                accountOwner = $("#js-account-owner-wrapper"),
                ein = $("#js-ein-wrapper");
            if ($this.val() === "business") {
                accountOwner.show();
                ein.show();
            } else {
                accountOwner.hide();
                ein.hide();
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


function completeRegistration(addressValidationForm, addressForm,
                              bankAccountValidationForm, bankAccountForm) {
    addressValidationForm.data('formValidation').validate();
    bankAccountValidationForm.data('formValidation').validate();
    var accountType,
        greyPage = document.getElementById('sb-greyout-page');
    if(addressValidationForm.data('formValidation').isValid() === true &&
            bankAccountValidationForm.data('formValidation').isValid()) {
        greyPage.classList.remove('sb_hidden');
        var accountData = helpers.getSuccessFormData(bankAccountForm);
        if (accountData.stripe_account_type === "business") {
            accountType = "company";
        } else {
            accountType = "individual";
        }
        addresses.submitAddress(addressForm, function callback() {
            // Call stripe after address is submitted because it requires it to
            // properly setup the Account
            Stripe.bankAccount.createToken({
                country: "US",
                currency: "USD",
                routing_number: accountData.routing_number,
                account_number: accountData.account_number,
                name: accountData.account_owner,
                account_holder_type: accountType
            }, stripeBankHandler);
        }, true);

    }
}


function stripeBankHandler(status, response){
    var greyPage = document.getElementById('sb-greyout-page');
    if (response.error) {
        // This should be done in the first place before sending off to stripe
        // Maybe we want to pre-empt the user with a warning popup if they click
        // submit when this is verified. Alerting them that it may cause
        // delays in their donations being processed.
        if ($("#completed-stripe").data("completed_stripe") !== "True") {
            $.notify(response.error.message, {type: 'danger'});
        }
        greyPage.classList.add('sb_hidden');
    } else {
        var data = helpers.getFormData(document.getElementById('banking-form'));
        data.stripe_token = response.id;
        data.tos_acceptance = true;
        requests.patch({
            url: "/v1/quests/" + settings.profile.username + "/",
            data: JSON.stringify(data)
        })
            .done(function () {
                var missionId = localStorage.getItem("recent_mission_id"),
                    missionSlug = localStorage.getItem("recent_mission_slug");
                if(missionId !== undefined && missionId !== null && missionSlug !== undefined && missionSlug !== null) {
                    window.location.href = "/missions/" + missionId + "/" + missionSlug + "/manage/epic/";
                } else {
                    window.location.href = "/quests/" + settings.profile.username + "/manage/general/";
                }
                greyPage.classList.add('sb_hidden');
            })
            .fail(function () {
                greyPage.classList.add('sb_hidden');
            });
    }
}