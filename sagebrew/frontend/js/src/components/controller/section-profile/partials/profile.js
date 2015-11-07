/* global enableSinglePostFunctionality, populateComments */
/**
 * @file
 * Profile (aka wall) page.
 * TODO refactor and include the above globals.
 * 
 */
var request = require('./../../../api').request,
    helpers = require('./../../../common/helpers');

require('./../../../plugin/contentloader');

/**
 * These should really be called load or something.
 */
export function init () {
    var profile_page_user = helpers.args(1);

    //
    // Load up the wall.
    var $appWall = $(".app-wall");
    $appWall.sb_contentLoader({
        emptyDataMessage: 'Add a Spark :)',
        url: '/v1/profiles/' + profile_page_user + '/wall/render/',
        params: {
            expand: 'true',
            expedite: 'true'
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
            $container.append(data.results.html);
            enableSinglePostFunctionality(data.results.ids);
            populateComments(data.results.ids, "posts");
        }
    });

}