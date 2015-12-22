/*global Stripe*/
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
    controller: "quest/quest-manage/delete",
    match_method: "path",
    check: [
       "^quests\/[A-Za-z0-9.@_%+-]{1,36}\/manage\/delete"
    ]
};


/**
 * Load.
 */
export function load() {
    var $app = $(".app-sb"),
        questID = helpers.args(1),
        loadingSpinner = $('#sb-greyout-page');
    $app
        .on('click', '#deactivate-quest', function (event) {
            event.preventDefault();
            request.patch({url: "/v1/quests/" + questID + "/",
                data: JSON.stringify({"active": false})
            }).done(function (){
                window.location.reload();
            });
        })
        .on('click', '#delete-button', function (event) {
            event.preventDefault();
            request.remove({url: "/v1/quests/" + questID + "/"}).done(function (){
                window.location.href = "/user/";
            });
        })
}
