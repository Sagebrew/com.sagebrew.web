var payment = require('common/payment'),
    donationPayments = require('./partials/donationpayment');

export const meta = {
    controller: "donations/payment",
    match_method: "path",
    check: [
        "^missions\/[A-Za-z0-9.@_%+-]{36}\/[A-Za-z0-9.@_%+-]{1,140}\/donate\/payment"
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
    payment.listPaymentMethods("/v1/me/", donationPayments.usePaymentCallback,
        donationPayments.stripeResponseHandler,
        donationPayments.donationCancelRedirect);
}

/**
 * Post Load
 */
export function postload() {
    //
    // Intercom Tracking
}