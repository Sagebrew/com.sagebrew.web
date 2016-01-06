var templates = require('template_build/templates'),
    helpers = require('common/helpers'),
    settings = require('settings').settings,
    charts = require('./partials/charts'),
    exportContributions = require('./partials/contribution_export').exportContributions;

export const meta = {
    controller: "quest/quest-insights",
    match_method: "path",
    check: [
       "^quests\/[A-Za-z0-9.@_%+-]{1,36}\/insights"
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
    var missionSelector = document.getElementById("mission-select");
    charts.getCharts(missionSelector.options[0].value);
    exportContributions();
    missionSelector.onchange = function() {
        charts.getCharts(missionSelector.options[missionSelector.selectedIndex].value);
    };

}