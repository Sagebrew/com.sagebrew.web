var request = require('api').request,
    helpers = require('common/helpers'),
    addresses = require('common/addresses'),
    settings = require('settings').settings;

// Requiring validators like this to cut down on JSHint errors.
// The way we required them previously had us assigning the require to a
// variable but the variable was never used as the validators logic was
// immediately ran up on importing thus causing a JSHint unused variable error.
// Importing like this gives us the exact same functionality.
require("common/validators");


export function completeSelect(donateToID, campaignFinanceValidationForm,
                               addressForm, addressValidationForm) {
    var addressFormExists = false,
        campaignFinanceFormExists = false;
    if(addressValidationForm !== null && addressValidationForm !== undefined && addressValidationForm.length !== 0) {
        addressFormExists = true;
    }
    if(campaignFinanceValidationForm !== null && campaignFinanceValidationForm !== undefined && campaignFinanceValidationForm.length !== 0) {
        campaignFinanceFormExists = true;
    }
    if(settings.user.type === "anon"){
        window.location.href = "/missions/" + donateToID + "/" +
            helpers.args(2) + "/gifts/name/";
    } else {
        if(addressFormExists && campaignFinanceFormExists){
            addressValidationForm.data('formValidation').validate();
            campaignFinanceValidationForm.data('formValidation').validate();
            if(addressValidationForm.data('formValidation').isValid() === true && campaignFinanceValidationForm.data('formValidation').isValid() === true) {
                document.getElementById('sb-greyout-page').classList.remove('sb_hidden');
                addresses.submitAddress(addressForm,
                    submitCampaignFinance,
                    "/v1/profiles/" + settings.profile.username + "/");
            } else {
                $.notify(
                    {message: "Please complete the address and campaign " +
                    "finance sections below. We require this as you are " +
                    "giving a Gift to a Political Mission which must be " +
                    "legally recorded as a campaign contribution"},
                    {type: "danger"}
                );
            }
        } else if (addressFormExists && !campaignFinanceFormExists) {
            addressValidationForm.data('formValidation').validate();
            if (addressValidationForm.data('formValidation').isValid() === true) {
                document.getElementById('sb-greyout-page').classList.remove('sb_hidden');
                addresses.submitAddress(addressForm, redirectToPaymentSelect(donateToID),
                    "/v1/profiles/" + settings.profile.username + "/");
            } else {
                $.notify(
                    {message: "Please complete the address section below. " +
                    "We require this as you are giving a Gift to a Political " +
                    "Mission which must be legally recorded as a campaign " +
                    "contribution"},
                    {type: "danger"}
                );
            }
        } else if (!addressFormExists && campaignFinanceFormExists) {
            campaignFinanceValidationForm.data('formValidation').validate();
            if(campaignFinanceValidationForm.data('formValidation').isValid() === true){
                submitCampaignFinance();
            } else {
                $.notify(
                    {message: "Please complete the campaign finance section below. " +
                    "We require this as you are giving a Gift to a Political " +
                    "Mission which must be legally recorded as a campaign " +
                    "contribution"},
                    {type: "danger"}
                );
            }
        } else {
            createOrder(donateToID);
        }
    }
}

function redirectToPaymentSelect(donateToID) {
    document.getElementById('sb-greyout-page').classList.add('sb_hidden');
    window.location.href = "/missions/" + donateToID + "/" +
        helpers.args(2) + "/gifts/payment/";
}


function createOrder(donateToID) {
    var productIds = [],
        greyPage = $(".sb-greyout-page"),
        total = $("#js-order-total-price").text();
    greyPage.removeClass("sb_hidden");
    $(".selected-product-container").each(function(i, obj) {
        productIds.push($(obj).data("object_uuid"));
    });
    total = parseInt(parseFloat(total) * 100, 10);
    request.post({
        url: "/v1/orders/",
        data: JSON.stringify({
            product_ids: productIds,
            total: total,
            mission: donateToID
        })
    }).done(function(response){
        greyPage.addClass("sb_hidden");
        localStorage.setItem(donateToID + "_OrderId", response.id);
        redirectToPaymentSelect(donateToID);
    });
}


function submitCampaignFinance() {
    document.getElementById('sb-greyout-page').classList.remove('sb_hidden');
    var donateToID = helpers.args(1),
        employerName = document.getElementById('employer-name').value,
        occupationName = document.getElementById('occupation-name').value,
        retired = document.getElementById('retired-or-not-employed').checked,
        data;
    if (retired === true) {
        employerName = "N/A";
        occupationName = "Retired or Not Employed";
    }
    data = {
        employer_name: employerName,
        occupation_name: occupationName
    };
    request.patch({url: "/v1/me/", data: JSON.stringify(data)})
        .done(function () {
            createOrder(donateToID);
        });
}