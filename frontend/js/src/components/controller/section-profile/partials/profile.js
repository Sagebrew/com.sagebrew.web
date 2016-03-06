/* global enableSinglePostFunctionality, populateComments */
/**
 * @file
 * Profile (aka wall) page.
 * TODO refactor and include the above globals.
 *
 */
var request = require('api').request,
    helpers = require('common/helpers');

require('plugin/contentloader');

/**
 * These should really be called load or something.
 */
export function init () {
    var profile_page_user = helpers.args(1);

    //
    // Load up the wall.
    var $appWall = $(".app-wall");
    $appWall.sb_contentLoader({
        emptyDataMessage: '<h3>Add a Spark :)</h3>' +
        '<p style="color: #838c92;">Sparks are posts that will always remain private and will only be shared with your friends.</p>',
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