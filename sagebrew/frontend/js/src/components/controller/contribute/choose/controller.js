var helpers = require('common/helpers'),
    missions = require('common/missions');

export const meta = {
    controller: "contribute/choose",
    match_method: "path",
    check: [
        "^quests\/[A-Za-z0-9.@_%+-]{2,36}\/donate\/choose",
        "^quests\/[A-Za-z0-9.@_%+-]{2,36}\/volunteer\/choose"
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
        missionList = document.getElementById('js-mission-list'),
        contributionType = helpers.args(2),
        nextUrl;
    missions.populateMissions(missionList, helpers.args(1));
    $app
        .on('click', '.js-position', function () {
            if(contributionType === "volunteer") {
                nextUrl = "option";
            } else {
                nextUrl = "amount";
            }
            window.location.href = "/missions/" + this.id + "/" + this.dataset.slug + "/" + contributionType + "/" + nextUrl + "/";
        });

}

/**
 * Post Load
 */
export function postload() {
    //
    // Intercom Tracking
}