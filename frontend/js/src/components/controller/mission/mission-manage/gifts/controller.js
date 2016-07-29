var args = require('common/helpers').args,
    goods = require('../../../donations/partials/goods');

export const meta = {
    controller: "mission/mission-manage/gifts",
    match_method: "path",
    check: [
        "^missions\/[A-Za-z0-9.@_%+-]{36}\/[A-Za-z0-9.@_%+-]{1,70}\/manage\/gifts$"
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
    var giftContainer = $("#js-gift-container"),
        selectedGiftContainer = $("#js-selected-gift-container"),
        missionId = args(1);
    goods.search(giftContainer, selectedGiftContainer);
    goods.populateSelected(missionId, selectedGiftContainer);
}

/**
 * Post Load
 */
export function postload() {
    //
    // Intercom Tracking
}