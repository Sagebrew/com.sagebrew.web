/**
 * @file
 */
var request = require('api').request,
    helpers = require('common/helpers');

/**
 * Meta.
 */
export const meta = {
    controller: "mission/mission-manage",
    match_method: "path",
    check: [
       "^missions\/[A-Za-z0-9.@_%+-]{36}"
    ]
};


/**
 * Load.
 */
export function load() {
    var greyPage = document.getElementById('sb-greyout-page'),
        $app = $(".app-sb"),
        missionID = helpers.args(1);
    $app
        .on('click', '#take-live-mission', function () {
            event.preventDefault();
            greyPage.classList.remove('sb_hidden');
            request.patch({
                url: "/v1/missions/" + missionID + "/",
                data: JSON.stringify({
                    active: true
                })
            }).done(function () {
                window.location.reload();
            }).fail(function () {
                greyPage.classList.add('sb_hidden');
            });
        });
}