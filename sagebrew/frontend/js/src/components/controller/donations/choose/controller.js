var requests = require('api').request,
    helpers = require('common/helpers'),
    missions = require('common/missions'),
    settings = require('settings').settings,
    validators = require('common/validators'),
    moment = require('moment');

export const meta = {
    controller: "donations/choose",
    match_method: "path",
    check: [
        "^quests\/[A-Za-z0-9.@_%+-]{2,36}\/donate\/choose"
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
        missionList = document.getElementById('js-mission-list');
    missions.populateMissions(missionList, helpers.args(1));
    $app
        .on('click', '.js-position', function () {
            window.location.href = "/missions/" + this.id + "/" + this.dataset.slug + "/donate/amount/";
        });

}

/**
 * Post Load
 */
export function postload() {
    //
    // Intercom Tracking
}