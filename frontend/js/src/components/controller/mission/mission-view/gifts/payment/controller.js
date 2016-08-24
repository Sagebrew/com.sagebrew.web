/* global $ */
var settings = require('settings').settings,
    args = require('common/helpers').args,
    goods = require('../../../../donations/partials/goods'),
    payment = require('common/payment'),
    giftPayment = require('./partials/giftpayment'),
    donationPayment = require('../../../../donations/payment/partials/donationpayment');

export const meta = {
    controller: "mission/mission-view/gifts/payment",
    match_method: "path",
    check: [
        "^missions\/[A-Za-z0-9.@_%+-]{36}\/[A-Za-z0-9.@_%+-]{1,70}\/gifts\/payment$"
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
    var app = $(".app-sb"),
        giftContainer = $("#js-gift-container"),
        selectedGiftContainer = $("#js-selected-items"),
        missionId = args(1);
    giftContainer.append('<div class="loader"></div>');
    goods.populateCheckout(missionId, selectedGiftContainer);
    
    payment.listPaymentMethods("/v1/me/", giftPayment.usePaymentCallback,
        donationPayment.stripeResponseHandler,
        donationPayment.donationCancelRedirect);
}

/**
 * Post Load
 */
export function postload() {
    //
    // Intercom Tracking
}