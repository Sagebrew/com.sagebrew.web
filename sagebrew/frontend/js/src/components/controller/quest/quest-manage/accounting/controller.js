/*global Stripe*/
/**
 * @file
 */
var request = require('api').request,
    helpers = require('common/helpers'),
    moment = require('moment'),
    settings = require('settings').settings,
    questID = helpers.args(1);
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
    if(settings.profile.quest.verification.fields_needed !== null && settings.profile.quest.verification.fields_needed !== "" && settings.profile.quest.verification.fields_needed !== undefined && settings.profile.quest.verification.fields_needed !== "undefined") {
        document.getElementById('js-fields-needed').innerHTML = String("Fields Needed: " + settings.profile.quest.verification.fields_needed).replace('Business Name', 'Name of Entity Managing Bank').replace('Business Tax Id', "EIN of Managing Bank");
    }
    if(settings.profile.quest.verification.due_date !== null && settings.profile.quest.verification.due_date !== "" && settings.profile.quest.verification.due_date !== undefined && settings.profile.quest.verification.due_date !== "undefined") {
        document.getElementById('js-due-date').innerHTML = "Fields Needed By: " + moment.unix(1458604799).format("dddd, MMMM Do YYYY, h:mm a");
    }
    if(settings.profile.quest.verification.disabled_reason !== null && settings.profile.quest.verification.disabled_reason !== undefined && settings.profile.quest.verification.disabled_reason !== 'undefined') {
        document.getElementById('js-disabled-reason').innerHTML = "Disabled: " + settings.profile.quest.verification.disabled_reason;
    }
    if(settings.profile.quest.verification.upload_id === true && (settings.profile.quest.stripe_identification_sent === false || settings.profile.quest.stripe_identification_sent === null)){
        document.getElementById("identification-upload").classList.remove("sb_hidden");
    }
    $('.fileinput').fileinput();
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
        $("#image").change(function(){
            event.preventDefault();
            greyPage.classList.remove('sb_hidden');
            var formData = new FormData($('#identificationForm'));
            formData.append('img', $('#image')[0].files[0]);
            request.post({
                url: "/v1/quests/" + questID + "/upload_identification/",
                data: formData,
                cache: false,
                contentType: false,
                processData: false
            })
                .done(function () {
                    window.location.reload();
                })
                .fail(function () {
                    greyPage.classList.add('sb_hidden');
                });
        })
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