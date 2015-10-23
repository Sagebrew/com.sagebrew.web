/**
 * @file
 * For posts. Posts only exist on the feed and profile pages, but
 * we're just going to include them in the entire profile for now.
 */
var request = require('./../../../api').request,
    helpers = require('./../../../common/helpers');
require('./../../../plugin/contentloader');

/**
 * These should really be called load or something.
 */
export function init () {
    //
    // Load up the wall.
    var $appNewsfeed = $(".app-newsfeed");

    $appNewsfeed.sb_contentLoader({
        emptyDataMessage: 'Get out there and make some news :)',
        url: '/v1/me/newsfeed/',
        params: {
            expedite: 'true',
            html: 'true'
        },
        dataCallback: function(base_url, params) {
            var urlParams = $.param(params);
            var url;
            if (urlParams) {
                url = base_url + "?" + urlParams;
            }
            else {
                url = base_url;
            }

            return request.get({url:url});

        },
        renderCallback: function($container, data) {
            for (var i = 0; i < data.results.length; i++) {
                $container.append(Autolinker.link(data.results[i].html));
                enableContentFunctionality(data.results[i].id, data.results[i].type);
                if(data.results[i].type !== "politicalcampaign" && data.results[i].type !== "update"){
                    populateComments([data.results[i].id], data.results[i].type + "s");
                }

            }
        }
    });

}