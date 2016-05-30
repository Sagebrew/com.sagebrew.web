 /*global Intercom*/
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
    ],
    does_not_include: ['advocate', 'public_office', 'select', 'account']
};


/**
 * Load.
 */
export function load() {
    var greyPage = document.getElementById('sb-greyout-page'),
        $app = $(".app-sb"),
        missionID = helpers.args(1),
        missionSlug = helpers.args(2);
    $('[data-toggle="tooltip"]').tooltip();
    $app
        .on('click', '#href-submit-for-review', function () {
            event.preventDefault();
            greyPage.classList.remove('sb_hidden');
            Intercom('trackEvent', 'submitted-mission-for-review');
            request.patch({
                url: "/v1/missions/" + missionID + "/",
                data: JSON.stringify({
                    submitted_for_review: true,
                    saved_for_later: false
                })
            }).done(function (data) {
                if(helpers.args(3) === "review"){
                    window.location.href = "/missions/" + missionID + "/" + missionSlug + "/manage/epic/";
                } else {
                    window.location.reload();
                }
            }).fail(function () {
                greyPage.classList.add('sb_hidden');
            });
        })
        .on('click', '#js-save-for-later', function () {
            event.preventDefault();
            greyPage.classList.remove('sb_hidden');
            Intercom('trackEvent', 'saved-mission-for-later');
            request.patch({
                url: "/v1/missions/" + missionID + "/",
                data: JSON.stringify({
                    saved_for_later: true
                })
            }).done(function () {
                window.location.href = "/missions/" + missionID + "/" + missionSlug + "/manage/epic/";
            }).fail(function () {
                greyPage.classList.add('sb_hidden');
            });
        });

}