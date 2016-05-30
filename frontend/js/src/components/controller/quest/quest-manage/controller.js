 /*global Intercom*/
/**
 * @file
 */
var request = require('api').request;

/**
 * Meta.
 */
export const meta = {
    controller: "quest/quest-manage",
    match_method: "path",
    check: [
        "^quests\/[A-Za-z0-9.@_%+-]{1,36}"
    ],
    does_not_include: ['review']
};


/**
 * Load.
 */
export function load() {
    var greyPage = document.getElementById('sb-greyout-page'),
        $app = $(".app-sb");

    $('[data-toggle="tooltip"]').tooltip();
    $app
        .on('click', '#href-submit-for-review', function () {
            event.preventDefault();
            var missionID = this.dataset.missionId;
            greyPage.classList.remove('sb_hidden');
            Intercom('trackEvent', 'submitted-mission-for-review');
            request.patch({
                url: "/v1/missions/" + missionID + "/",
                data: JSON.stringify({
                    submitted_for_review: true,
                    saved_for_later: false
                })
            }).done(function () {
                window.location.reload();
            }).fail(function () {
                greyPage.classList.add('sb_hidden');
            });
        });
}