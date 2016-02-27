/**
 * @file
 */
var request = require('api').request,
    helpers = require('common/helpers');
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
        greyPage = document.getElementById('sb-greyout-page');
    $app
        .on('click', '#deactivate-quest', function (event) {
            event.preventDefault();
            greyPage.classList.remove('sb_hidden');
            request.patch({url: "/v1/quests/" + questID + "/",
                data: JSON.stringify({"active": false})
            }).done(function (){
                window.location.reload();
            });
        })
        .on('click', '#delete-button', function (event) {
            event.preventDefault();
            greyPage.classList.remove('sb_hidden');
            request.remove({url: "/v1/quests/" + questID + "/"})
                .done(function (){
                    window.location.href = "/user/";
                })
                .fail(function() {
                    greyPage.classList.add('sb_hidden');
                });
        });
}
