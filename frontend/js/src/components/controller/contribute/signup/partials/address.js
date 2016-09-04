/* global $ */
var requests = require('api').request,
    helpers = require('common/helpers'),
    validators = require('common/validators'),
    addresses = require('common/addresses'),
    moment = require('moment');


export function activateAddress() {
    var $app = $(".app-sb"),
        accountForm = document.getElementById('account-info'),
        addressForm = document.getElementById('address'),
        accountValidationForm = $(accountForm),
        campaignFinanceValidationForm,
        campaignFinanceForm = document.getElementById('campaign-finance');
    $(':checkbox').radiocheck();
    if(campaignFinanceForm !== undefined && campaignFinanceForm !== null) {
        campaignFinanceValidationForm = $(campaignFinanceForm);
        validators.campaignFinanceValidator(campaignFinanceValidationForm);
    }
    validators.accountValidator(accountValidationForm);
    var addressValidationForm = addresses.setupAddress(validateAddressCallback);
    $app
        .on('click', '#js-continue-btn', function (event) {
            event.preventDefault();
            completeRegistration(addressValidationForm, addressForm,
                accountValidationForm, accountForm, campaignFinanceValidationForm);
        }).on('keypress', '#account-info input', function(event) {
            if (event.which === 13 || event.which === 10) {
                completeRegistration(addressValidationForm, addressForm,
                    accountValidationForm, accountForm, campaignFinanceValidationForm);
                return false; // handles event.preventDefault(), event.stopPropagation() and returnValue for IE8 and earlier
            }
        }).on('keypress', '#address input', function(event) {
            if (event.which === 13 || event.which === 10) {
                completeRegistration(addressValidationForm, addressForm,
                    accountValidationForm, accountForm, campaignFinanceValidationForm);
                return false;
            }
        }).on('keypress', '#campaign-finance input', function(event) {
            if (event.which === 13 || event.which === 10) {
                completeRegistration(addressValidationForm, addressForm,
                    accountValidationForm, accountForm, campaignFinanceValidationForm);
                return false;
            }
        }).on('click', '#retired-or-not-employed', function () {
            if(campaignFinanceValidationForm !== null && campaignFinanceValidationForm !== undefined) {
                campaignFinanceValidationForm.formValidation('revalidateField', 'campaignFinanceForm');
                campaignFinanceValidationForm.formValidation('revalidateField', 'onlyOneSelector');

            }
        });

    $('#birthday').keyup(function (e) {
        helpers.birthdayInputManager(this, e);
    });
}


function completeRegistration(addressValidationForm, addressForm,
                              accountValidationForm, accountForm,
                              campaignFinanceValidationForm) {
    addressValidationForm.data('formValidation').validate();
    accountValidationForm.data('formValidation').validate();
    // Do this here so all the fields necessary pop up immediately and you don't have
    // to successfully fill out address and profile before seeing these warnings.
    if(campaignFinanceValidationForm !== null && campaignFinanceValidationForm !== undefined) {
        campaignFinanceValidationForm.data('formValidation').validate();
    }
    if(addressValidationForm.data('formValidation').isValid() === true &&
            accountValidationForm.data('formValidation').isValid()){
        document.getElementById('sb-greyout-page').classList.remove('sb_hidden');
        var accountData = helpers.getSuccessFormData(accountForm);

        // If employment and occupation info is available add it to the account info
        var campaignFinanceForm = document.getElementById('campaign-finance');
        if(campaignFinanceForm !== undefined && campaignFinanceForm !== null) {
            if(campaignFinanceValidationForm.data('formValidation').isValid() === true){
                var employerName = document.getElementById('employer-name').value,
                    occupationName = document.getElementById('occupation-name').value,
                    retired = document.getElementById('retired-or-not-employed').checked;
                if (retired === true) {
                    accountData.employer_name = "N/A";
                    accountData.occupation_name = "Retired or Not Employed";
                } else {
                    accountData.employer_name = employerName;
                    accountData.occupation_name = occupationName;
                }
            } else {
                document.getElementById('sb-greyout-page').classList.add('sb_hidden');
                return false;
            }
        }

        // The backend doesn't care about the user's password matching so
        // delete the second password input we use to help ensure the user
        // doesn't put int a password they don't mean to.
        delete accountData.password2;
        accountData.date_of_birth = moment(accountData.date_of_birth, "MM/DD/YYYY").format();
        requests.post({url: "/v1/profiles/", data: JSON.stringify(accountData)})
            .done(function (data) {
                addresses.submitAddress(addressForm, submitAddressCallback,
                    "/v1/profiles/" + data.id + "/");
            });
        }
}


function validateAddressCallback() {
}

function submitAddressCallback() {
    var contributionType = helpers.args(3),
        missionSlug = helpers.args(2),
        donateToID = helpers.args(1),
        greyPage = document.getElementById('sb-greyout-page');
    greyPage.classList.add('sb_hidden');
    if(contributionType === "volunteer") {
        window.location.href = "/missions/" + donateToID + "/" +
            missionSlug + "/" + contributionType + "/option/";
    } else if (contributionType === "endorse") {
        window.location.href = "/missions/" + donateToID + "/" +
            missionSlug + "/" + contributionType + "/";
    } else if (contributionType === "gifts") {
        window.location.href = "/missions/" + donateToID + "/" +
            missionSlug + "/gifts/donate/";
    } else {
        window.location.href = "/missions/" + donateToID + "/" +
            missionSlug + "/donate/payment/";
    }
}