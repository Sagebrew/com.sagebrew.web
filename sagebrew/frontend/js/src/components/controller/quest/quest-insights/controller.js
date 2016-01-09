var charts = require('./partials/charts'),
    exportContributions = require('./partials/contribution_export').exportContributions,
    helpers = require('common/helpers');

export const meta = {
    controller: "quest/quest-insights",
    match_method: "path",
    check: [
       "^quests\/[A-Za-z0-9.@_%+-]{1,36}\/insights",
       "^missions\/[A-Za-z0-9.@_%+-]{1,36}\/[A-Za-z0-9.@_%+-]{1,140}\/insights"
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
    var missionSelector = document.getElementById("mission-select"),
        missionId = helpers.args(1),
        objectType = helpers.args(0);
    charts.getCharts(missionId, objectType);
    exportContributions();
    missionSelector.onchange = function() {
        var selectedVal = missionSelector.options[missionSelector.selectedIndex].value,
            selectedText = missionSelector.options[missionSelector.selectedIndex].text,
            selectedSlug;
        if (selectedVal === "all") {
            selectedVal = missionSelector.options[missionSelector.selectedIndex].dataset.quest_id;
            window.history.pushState("", selectedText + " Insights", "/quests/" + selectedVal + "/insights/");
            charts.getCharts(selectedVal, "quests");
        } else {
            selectedSlug = missionSelector.options[missionSelector.selectedIndex].dataset.slug;
            window.history.pushState("", selectedText + " Insights", "/missions/" + selectedVal + "/" + selectedSlug + "/insights/");
            charts.getCharts(selectedVal, "missions");
        }
    };

}