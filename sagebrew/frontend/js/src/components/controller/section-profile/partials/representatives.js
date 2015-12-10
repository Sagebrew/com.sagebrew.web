/**
 * @file
 * Load reps onto page.
*/
var request = require('api').request,
    settings = require('settings').settings,
    helpers = require('common/helpers');

/**
 * TODO:turn reps into some sort of tree structure so that we can get all the
 * info from one request.
 */
export function init() {
    var pageUser = helpers.args(1);
    if(pageUser === "newsfeed" || pageUser === "undefined" || pageUser === undefined || pageUser === ""){
        pageUser = settings.user.username;
    }
    if ($("#president_wrapper").length) {
        var rcp = request.get({url: '/v1/profiles/' + pageUser + '/president/?html=true'}),
            rcs = request.get({url: '/v1/profiles/' + pageUser + '/senators/?html=true'}),
            rchr = request.get({url: '/v1/profiles/' + pageUser + '/house_representative/?html=true'}),
            rps = request.get({url: '/v1/profiles/' + pageUser + '/possible_senators/?html=true'}),
            rphr = request.get({url: '/v1/profiles/' + pageUser + '/possible_house_representatives/?html=true'}),
            rpp = request.get({url: '/v1/profiles/' + pageUser + '/possible_presidents/?html=true'}),
            rplr = request.get({url: '/v1/profiles/' + pageUser + '/possible_local_representatives/?html=true'});

        $.when(rcp, rcs, rchr, rps, rphr, rpp, rplr).done(function (dcp, dcs, dchr, dps, dphr, dpp, dplr) {
            $("#president_wrapper").append(dcp[0]);
            $("#senator_wrapper").append(dcs[0]);
            $("#house_rep_wrapper").append(dchr[0]);
            $("#potential_senator_wrapper").append(dps[0]);
            $("#potential_rep_wrapper").append(dphr[0]);
            $("#potential_president_wrapper").append(dpp[0]);
            $("#potential_local_wrapper").append(dplr[0]);
        });
    }
}