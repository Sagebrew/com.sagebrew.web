/*global Stripe*/
/**
 * @file
 */
var request = require('api').request,
    helpers = require('common/helpers'),
    settings = require('settings').settings;
/**
 * Meta.
 */
export const meta = {
    controller: "quest/quest-manage/accounting",
    match_method: "path",
    check: [
       "^quests\/[A-Za-z0-9.@_%+-]{1,36}\/manage\/banking"
    ]
};


/**
 * Load.
 */
export function load() {
    var $app = $(".app-sb"),
        greyPage = document.getElementById('sb-greyout-page'),
        account_type;
    Stripe.setPublishableKey(settings.api.stripe);
    $app
        .on('click', '#submit', function(event) {
            event.preventDefault();
            var data = helpers.getFormData(document.getElementById('bankingForm'));
            if (data.stripe_account_type === "business"){
                account_type = "company";
            } else {
                account_type = "individual";
            }
            if (data.ssn && data.routing_number && data.account_number) {
                greyPage.classList.remove('sb_hidden');
                Stripe.bankAccount.createToken({
                    country: "US",
                    currency: "USD",
                    routing_number: data.routing_number,
                    account_number: data.account_number,
                    name: data.account_owner,
                    account_holder_type: account_type
                }, stripeBankHandler);
            } else {
                if(!data.ssn){
                    $.notify("Social Security Number is Required", {type: "danger"});
                }
                if(!data.routing_number){
                    $.notify("Routing Number is Required", {type: "danger"});
                }
                if(!data.account_number){
                    $.notify("Account Number is Required", {type: "danger"});
                }
            }
        });
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
        var questID = helpers.args(1),
            data = helpers.getFormData(document.getElementById('bankingForm'));
        data.stripe_token = response.id;
        data.tos_acceptance = true;
        request.patch({url: "/v1/quests/" + questID + "/",
            data: JSON.stringify(data)
        }).done(function (){
            window.location.reload();
        }).fail(function () {
            greyPage.classList.add('sb_hidden');
        });
    }
}