/*global Stripe*/
var //// templates = require('template_build/templates'),
    helpers = require('common/helpers'),
    settings = require('settings').settings,
    moment = require('moment');


var template_payment_info = require('common/templates/payment_info.hbs');

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
            exp_year: settings.profile.quest.card.exp_year
        };
        if(settings.profile.quest.subscription !== null) {
            paymentData.next_due_date = moment.unix(settings.profile.quest.subscription.current_period_end).format("MM/DD/YYYY");
            paymentData.bill_rate = settings.profile.quest.subscription.amount / 100;
        } else {
            paymentData.next_due_date = "Never";
            paymentData.bill_rate = "0.00";
        }
    } else if (settings.profile.quest.account_type === "paid" ||
            settings.profile.quest.account_type === "promotion") {
        var subscription = settings.profile.quest.subscription,
            formattedPaymentDate;
        if(subscription !== "undefined" && subscription !== undefined && subscription !== null){
            formattedPaymentDate = moment.unix(subscription.current_period_end).format("MM/DD/YYYY");
        } else {
            formattedPaymentDate = "You need to add a payment method";
        }
        paymentData = {
            card_on_file: false,
            next_due_date: formattedPaymentDate,
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
    paymentInfo.innerHTML = template_payment_info(paymentData);
    $app
        .on('click', '#js-payment-method', function(event) {
            event.preventDefault();
            window.location.href = "/quests/" + questID + "/manage/add_payment/";
        });
}

/**
 * Post Load
 */
export function postload() {
    //
    // Intercom Tracking
}