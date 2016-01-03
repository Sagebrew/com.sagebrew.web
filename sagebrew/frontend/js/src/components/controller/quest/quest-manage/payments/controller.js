var addPayment = require('common/payment').addPayment,
    questPayments = require('./partials/questpayments');

export const meta = {
    controller: "quest/quest-manage/payments",
    match_method: "path",
    check: [
       "^quests\/[A-Za-z0-9.@_%+-]{1,36}\/manage\/add_payment",
        "^user\/settings\/add_payment"
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
    addPayment(questPayments.stripeResponseHandler, questPayments.questCancelRedirect);
}

/**
 * Post Load
 */
export function postload() {
    //
    // Intercom Tracking
}