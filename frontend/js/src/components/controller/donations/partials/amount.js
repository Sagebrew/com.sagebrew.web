var request = require('api').request,
    radioSelector = require('common/radioimage').radioSelector,
    helpers = require('common/helpers'),
    validators = require('common/validators'),
    settings = require('settings').settings;

export function amount() {
    var continueBtn = document.getElementById('js-continue-btn'),
        customInput = document.getElementById('custom-contribution'),
        customInputWrapper = document.getElementById('custom-amount-wrapper'),
        errorFormatWrapper = document.getElementById('error-wrong-format'),
        errorMinDonationWrapper = document.getElementById('error-min-donation'),
        donateToID = helpers.args(1),
        campaignFinanceValidationForm,
        campaignFinanceForm = document.getElementById('campaign-finance'),
        contributionKey = donateToID + 'contributionAmount',
        subscriptionKey = donateToID + 'subscriptionType';
    $(':radio').radiocheck();
    $(':checkbox').radiocheck();
    if(campaignFinanceForm !== undefined && campaignFinanceForm !== null) {
        campaignFinanceValidationForm = $(campaignFinanceForm);
        validators.campaignFinanceValidator(campaignFinanceValidationForm);
    }
    if(typeof(Storage) !== "undefined") {
        // Set form back up if user has already been here and not
        // submitted their donation
        var setContribution = localStorage.getItem(contributionKey);
        if(setContribution !== undefined && setContribution !== null) {
            var refreshPage = document.getElementById(setContribution);
            if(refreshPage !== undefined && refreshPage !== null) {
                refreshPage.classList.add("radio-selected");
            } else {
                customInput.value = setContribution.slice(0, setContribution.length-2) +
                    "." + setContribution.slice(setContribution.length - 2);
                document.getElementById('js-custom-contribution').classList.add('radio-selected');
                customInputWrapper.classList.remove("sb_hidden");
            }
            continueBtn.disabled = false;
        }

        var setSubscription = localStorage.getItem(subscriptionKey);
        if(subscriptionKey !== undefined && subscriptionKey !== null) {
            var refreshSubscription = document.getElementById(setSubscription);
            if(refreshSubscription !== undefined && refreshSubscription !== null) {
                refreshSubscription.setAttribute('checked', 'checked');
            }
        }
    }
    $(".app-sb")
        .on('click', '.radio-image-selector', function(event) {
            event.preventDefault();
            if(this.classList.contains("radio-selected")){
                // If we select a button that was already selected we
                // need to remove the custom amount input if it's displayed
                // and remove the currently set contribution
                customInputWrapper.classList.add("sb_hidden");
                localStorage.removeItem(contributionKey);
                continueBtn.disabled = true;
                customInput.value = "";
            } else if(this.classList.contains("js-custom-contribution")){
                // If the user selects the custom button we need to show the
                // custom contribution input
                customInputWrapper.classList.remove("sb_hidden");
                localStorage.removeItem(contributionKey);
                continueBtn.disabled = true;
            } else if (this.classList.contains("js-contribution")){
                // If the user selects a button we need to set the contribution
                // to the selection and if the custom button had been selected
                // and was unselected we need to add the hidden class
                customInputWrapper.classList.add("sb_hidden");
                localStorage.setItem(contributionKey, this.id);
                continueBtn.disabled = false;
                customInput.value = "";
            }
            radioSelector(this);
        })
        .on('keyup', '#custom-contribution', function () {
            var decimalFormat  = /^\d+(?:\.\d{2})$/,
                nonDecimalFormat = /^[0-9]*$/,
                numStr = this.value;
            if (!decimalFormat.test(numStr) && !nonDecimalFormat.test(numStr)){
                errorFormatWrapper.classList.remove("sb_hidden");
                continueBtn.disabled = true;
            } else if (parseInt(numStr) < 1) {
                errorMinDonationWrapper.classList.remove("sb_hidden");
                continueBtn.disabled = true;
            } else if (numStr.replace(/\s/g, "").length === 0 || numStr === null) {
                errorMinDonationWrapper.classList.remove("sb_hidden");
                continueBtn.disabled = true;
            } else if (decimalFormat.test(numStr)) {
                errorMinDonationWrapper.classList.add("sb_hidden");
                errorFormatWrapper.classList.add("sb_hidden");
                continueBtn.disabled = false;
                localStorage.setItem(contributionKey, numStr.replace(".", ""));
            } else if (nonDecimalFormat.test(numStr)) {
                errorMinDonationWrapper.classList.add("sb_hidden");
                errorFormatWrapper.classList.add("sb_hidden");
                continueBtn.disabled = false;
                localStorage.setItem(contributionKey, numStr + "00");
            }
        })
        .on('click', '.js-subscription', function (){
            localStorage.setItem(subscriptionKey, this.id);
        })
        .on('click', '#js-continue-btn', function(event){
            event.preventDefault();
            completeAmount(donateToID, campaignFinanceValidationForm);
        })
        .on('keypress', '#campaign-finance input', function(event) {
            if (event.which === 13 || event.which === 10) {
                completeAmount(donateToID, campaignFinanceValidationForm);
                return false;
            }
        })
        .on('click', '#retired-or-not-employed', function () {
            if(campaignFinanceValidationForm !== null && campaignFinanceValidationForm !== undefined) {
                campaignFinanceValidationForm.formValidation('revalidateField', 'campaignFinanceForm');
                campaignFinanceValidationForm.formValidation('revalidateField', 'onlyOneSelector');

            }
        });
}


function completeAmount(donateToID, campaignFinanceValidationForm) {
    if(settings.user.type === "anon"){
        window.location.href = "/missions/" + donateToID + "/" +
            helpers.args(2) + "/donate/name/";
    } else {
        if(campaignFinanceValidationForm !== null && campaignFinanceValidationForm !== undefined) {
            campaignFinanceValidationForm.data('formValidation').validate();
            if(campaignFinanceValidationForm.data('formValidation').isValid() === true){
                document.getElementById('sb-greyout-page').classList.remove('sb_hidden');
                var employerName = document.getElementById('employer-name').value,
                    occupationName = document.getElementById('occupation-name').value,
                    retired = document.getElementById('retired-or-not-employed').checked;
                if(retired === true){
                    employerName = "N/A";
                    occupationName = "Retired or Not Employed";
                }
                var data = {
                    employer_name: employerName,
                    occupation_name: occupationName
                };
                request.patch({url: "/v1/me/", data: JSON.stringify(data)})
                    .done(function () {
                        document.getElementById('sb-greyout-page').classList.add('sb_hidden');
                        window.location.href = "/missions/" + donateToID + "/" +
                            helpers.args(2) + "/donate/payment/";
                    });
            }
        } else {
            document.getElementById('sb-greyout-page').classList.add('sb_hidden');
            window.location.href = "/missions/" + donateToID + "/" +
                helpers.args(2) + "/donate/payment/";
        }
    }
}