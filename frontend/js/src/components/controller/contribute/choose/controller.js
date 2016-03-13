var helpers = require('common/helpers'),
    missions = require('common/missions'),
    settings = require('settings').settings;

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
    require('common/handlebars_helpers');
    var $app = $(".app-sb"),
        missionList = document.getElementById('js-mission-list'),
        contributionType = helpers.args(2);
    missions.populateMissions(missionList, helpers.args(1));
    $app
        .on('click', '.js-position', function (event) {
            event.preventDefault();
            if(contributionType === "volunteer") {
                if(settings.user.type === "anon"){
                    window.location.href = "/missions/" + this.dataset.id + "/" + this.dataset.slug + "/" + contributionType + "/name/";
                } else {
                    window.location.href = "/missions/" + this.dataset.id + "/" + this.dataset.slug + "/" + contributionType + "/option/";
                }
            } else {
                window.location.href = "/missions/" + this.dataset.id + "/" + this.dataset.slug + "/" + contributionType + "/amount/";
            }
            return false;
        });

}

/**
 * Post Load
 */
export function postload() {
    //
    // Intercom Tracking
}