var request = require('api').request;

export const meta = {
    controller: "user-settings/donations",
    match_method: "path",
    check: [
       "^user/settings/donations$"
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
    var $container = $("#js-donation-wrapper");
    $container.sb_contentLoader({
        emptyDataMessage: 'Need to make some donations for this to be populated :)',
        url: "/v1/me/donations/",
        params: {
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
                $("#js-donation-container").append(data.results[i]);
            }
        }
    });
}

/**
 * Post Load
 */
export function postload() {
    //
    // Intercom Tracking
}