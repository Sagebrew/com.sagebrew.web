/*global Stripe*/
var templates = require('template_build/templates'),
    helpers = require('common/helpers'),
    settings = require('settings').settings,
    request = require('api').request;

export const meta = {
    controller: "quest/quest-manage/plans",
    match_method: "path",
    check: [
       "^quests\/[A-Za-z0-9.@_%+-]{1,36}\/manage\/plan"
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
        greyPage = document.getElementById('sb-greyout-page');
    $app
        .on('click', '#js-paid-account', function () {
            greyPage.classList.remove('sb_hidden');
            request.patch({url: "/v1/quests/" + questID + "/", data: JSON.stringify({
                account_type: "paid"
            })}).done(function () {
                window.location.href = "/quests/" + questID + "/manage/billing/"
            }).fail(function (XMLHttpRequest) {
                request.errorDisplay(XMLHttpRequest);
                greyPage.classList.add('sb_hidden');
            });
        })
        .on('click', '#js-free-account', function () {
            greyPage.classList.remove('sb_hidden');
            request.patch({url: "/v1/quests/" + questID + "/", data: JSON.stringify({
                account_type: "free"
            })}).done(function () {
                window.location.href = "/quests/" + questID + "/manage/billing/"
            }).fail(function (XMLHttpRequest) {
                request.errorDisplay(XMLHttpRequest);
                greyPage.classList.add('sb_hidden');
            });
        })
}

/**
 * Post Load
 */
export function postload() {
    //
    // Intercom Tracking
}