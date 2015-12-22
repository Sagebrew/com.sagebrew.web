/*global Stripe*/
var templates = require('template_build/templates'),
    helpers = require('common/helpers'),
    settings = require('settings').settings;

export const meta = {
    controller: "quest/quest-manage/billing",
    match_method: "path",
    check: [
       "^quests\/[A-Za-z0-9.@_%+-]{1,36}\/manage\/billing"
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
        questID = helpers.args(1),
        paymentInfo = document.getElementById('js-payment-info-block'),
        paymentData;
    Stripe.setPublishableKey(settings.api.stripe);
    if(settings.profile.quest.card !== null){
        paymentData = {
            card_on_file: true,
            brand: settings.profile.quest.card.brand,
            dynamic_last4: settings.profile.quest.card.last4,
            exp_month: settings.profile.quest.card.exp_month,
            exp_year: settings.profile.quest.card.exp_year,
            next_due_date: "12/29/2015",
            bill_rate: "100.00"
        };
    } else {
        paymentData = {
            card_on_file: false,
            brand: "N/A",
            dynamic_last4: "",
            exp_month: "00",
            exp_year: "00",
            next_due_date: "You're on the Free account",
            bill_rate: "0.00"
        };
    }
    paymentInfo.innerHTML = templates.payment_info(paymentData);
    $app
        .on('click', '#js-payment-method', function(event) {
            event.preventDefault();
            window.location.href = "/quests/" + questID + "/manage/add_payment/"
        })
        .on('click', '#deactivate-quest', function (event) {
            event.preventDefault();
            request.patch({url: "/v1/quests/" + questID + "/",
                data: JSON.stringify({"active": false})
            }).done(function (){
                window.location.reload();
            });
        })
        .on('click', '#delete-button', function (event) {
            event.preventDefault();
            request.remove({url: "/v1/quests/" + questID + "/"}).done(function (){
                window.location.href = "/user/";
            });
        });
}

/**
 * Post Load
 */
export function postload() {
    //
    // Intercom Tracking
}