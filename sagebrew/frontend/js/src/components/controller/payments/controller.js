var addPayment = require('./partials/add_payment');

export const meta = {
    controller: "payments",
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
    addPayment.load();
}

/**
 * Post Load
 */
export function postload() {
    //
    // Intercom Tracking
}