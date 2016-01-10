var graphs = require('common/graphs'),
    request = require('api').request,
    helpers = require('common/helpers');

export const meta = {
    controller: "quest/quest-manage/insights",
    match_method: "path",
    check: [
       "^quests\/[A-Za-z0-9.@_%+-]{1,36}\/manage\/insights"
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
    var questID = helpers.args(1);
    request.get({url: "/v1/quests/" + questID + "/donations/"})
        .done(function (data) {
            graphs.donationsGraph(data, "#js-individual-donation-chart");
        });
}