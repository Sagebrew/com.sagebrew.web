var amount = require('./partials/amount').amount;

export const meta = {
    controller: "donations",
    match_method: "path",
    check: [
       "^missions\/[A-Za-z0-9.@_%+-]{36}\/[A-Za-z0-9.@_%+-]{1,140}\/donate\/amount"
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
    amount();
}

/**
 * Post Load
 */
export function postload() {
    //
    // Intercom Tracking
}