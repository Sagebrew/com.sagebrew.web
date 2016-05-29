var request = require('api').request,
    helpers = require('common/helpers'),
    graphs = require('common/graphs');

export const meta = {
    controller: "mission/mission-manage/insights",
    match_method: "path",
    check: [
        "^missions\/[A-Za-z0-9.@_%+-]{36}\/[A-Za-z0-9.@_%+-]{1,70}\/manage\/insights"
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
    var missionID = helpers.args(1);
    request.get({url: "/v1/missions/" + missionID + "/donations/"})
        .done(function (data) {
            graphs.donationsGraph(data, "#js-individual-donation-chart");
        });
}


/**
 * Post Load
 */
export function postload() {
    //
    // Intercom Tracking
}