 /*global Intercom*/
/**
 * @file
 */
var request = require('api').request,
    facebook = require('common/facebook'),
    twitter = require('common/twitter');

/**
 * Meta.
 */
export const meta = {
    controller: "quest/quest-manage",
    match_method: "path",
    check: [
        "^quests\/[A-Za-z0-9.@_%+-]{1,36}\/manage"
    ],
    does_not_include: ['review']
};


/**
 * Load.
 */
export function load() {
    var greyPage = document.getElementById('sb-greyout-page'),
        $app = $(".app-sb"),
        missionID = document.getElementById('href-submit-for-review').dataset.missionId,
        missionSlug = document.getElementById('href-submit-for-review').dataset.missionSlug;
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
            }).done(function () {
                window.location.reload();
            }).fail(function () {
                greyPage.classList.add('sb_hidden');
            });
        })
        .on('click', "#" + missionID + "_FBShare", function(event) {
            event.preventDefault();
            var shareURL = window.location.protocol + "//" + window.location.hostname + "/missions/" + missionID + "/" + missionSlug + "/";
            facebook.sharing(shareURL, "/v1/missions/" + missionID + "/");
        })
        .on('click', "#" + missionID + "_TwitterShare", function() {
            twitter.sharing("/v1/missions/" + missionID + "/");
        });
}