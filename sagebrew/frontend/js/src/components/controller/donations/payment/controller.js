var requests = require('api').request,
    helpers = require('common/helpers'),
    payment = require('common/payment'),
    settings = require('settings').settings,
    validators = require('common/validators'),
    moment = require('moment');

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
    payment.addPayment();
}

/**
 * Post Load
 */
export function postload() {
    //
    // Intercom Tracking
}