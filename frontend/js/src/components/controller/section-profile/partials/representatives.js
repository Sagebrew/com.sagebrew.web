/**
 * @file
 * Load reps onto page.
*/
var request = require('api').request,
    settings = require('settings').settings,
    sittingRepTemplate = require('../templates/sitting_representative.hbs'),
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
        var rcp = request.get({url: '/v1/profiles/' + pageUser + '/president/'}),
            rcs = request.get({url: '/v1/profiles/' + pageUser + '/senators/'}),
            rchr = request.get({url: '/v1/profiles/' + pageUser + '/house_representative/'});

        $.when(rcp, rcs, rchr).done(function (dcp, dcs, dchr) {
            dcp[0].terms = helpers.getOrdinal(dcp[0].terms);
            dcp[0].has_website = !!dcp[0].quest.website;
            $("#president_wrapper").append(sittingRepTemplate({"representative": [dcp[0]]}));

            for(var i = 0; dcs[0].length > i; i++){
                dcs[0][i].terms = helpers.getOrdinal(dcs[0][i].terms);
                dcs[0][i].has_website = !!dcs[0][i].quest.website;
            }
            $("#senator_wrapper").append(sittingRepTemplate({"representative": dcs[0]}));

            dchr[0].terms = helpers.getOrdinal(dchr[0].terms);
            dchr[0].has_website = !!dchr[0].quest.website;
            $("#house_rep_wrapper").append(sittingRepTemplate({"representative": [dchr[0]]}));
        });
    }
}