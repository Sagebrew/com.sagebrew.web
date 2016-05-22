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
        "^quests\/[A-Za-z0-9.@_%+-]{1,36}",
        "^missions\/[A-Za-z0-9.@_%+-]{36}\/"
    ]
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
            var missionID = this.dataset.missionId,
                missionSlug = this.dataset.missionSlug;
            greyPage.classList.remove('sb_hidden');
            Intercom('trackEvent', 'submitted-mission-for-review');
            request.patch({
                url: "/v1/missions/" + missionID + "/",
                data: JSON.stringify({
                    submitted_for_review: true
                })
            }).done(function () {
                window.location.href = "/missions/" + missionID + "/" + missionSlug + "/manage/epic/";
            }).fail(function () {
                greyPage.classList.add('sb_hidden');
            });
        });
}