var helpers = require('common/helpers'),
    request = require('api').request,
    settings = require('settings').settings;

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
            if(settings.profile.quest.card_on_file === true){
                request.patch({url: "/v1/quests/" + questID + "/", data: JSON.stringify({
                    account_type: "paid"
                })}).done(function () {
                    window.location.href = "/quests/" + questID + "/manage/billing/";
                }).fail(function () {
                    greyPage.classList.add('sb_hidden');
                });
            } else {
                localStorage.setItem('quest_account', 'upgrade');
                window.location.href = "/quests/" + questID +"/manage/add_payment/";
            }
        })
        .on('click', '#js-free-account', function () {
            console.log('here');
            greyPage.classList.remove('sb_hidden');
            request.patch({url: "/v1/quests/" + questID + "/", data: JSON.stringify({
                account_type: "free"
            })}).done(function () {
                window.location.href = "/quests/" + questID + "/manage/billing/";
            }).fail(function () {
                greyPage.classList.add('sb_hidden');
            });
        });
}

/**
 * Post Load
 */
export function postload() {
    //
    // Intercom Tracking
}