/**
 * @file
 */
var request = require('api').request,
    helpers = require('common/helpers'),
    settings = require('settings').settings;

/**
 * Meta.
 */
export const meta = {
    controller: "quest/quest-manage",
    match_method: "path",
    check: [
        "^quests\/[A-Za-z0-9.@_%+-]{1,36}",
        "^missions\/[A-Za-z0-9.@_%+-]{36}\/"
    ]
};


/**
 * Load.
 */
export function load() {
    var greyPage = document.getElementById('sb-greyout-page'),
        $app = $(".app-sb"),
        questID = helpers.args(1);
    $app
        .on('click', '#take-live', function () {
            event.preventDefault();
            if (settings.profile.quest.account_verified !== "verified") {
                $.notify('You must add a bank account under "Accounting" prior to taking your Quest live so we can get you your donations', {type: "danger"});
            } else if (settings.profile.quest.account_type === "paid" && settings.profile.quest.card_on_file !== true) {
                $.notify('You must add a credit card under "Billing" or change your account to free prior to taking the Quest live', {type: "danger"});
            } else {
                greyPage.classList.remove('sb_hidden');
                request.patch({
                    url: "/v1/quests/" + questID + "/",
                    data: JSON.stringify({
                        active: true
                    })
                }).done(function () {
                    window.location.reload();
                }).fail(function () {
                    greyPage.classList.add('sb_hidden');
                });
            }
        });
}