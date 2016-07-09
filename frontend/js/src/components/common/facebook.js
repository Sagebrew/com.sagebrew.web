/* global FB */
var requests = require('api').request;
/*
 * Allow users to share a Mission (may add other objects in the future) on FB
 */
export function sharing(buttonId, sharedURL, updateURL) {
    document.getElementById(buttonId).onclick = function() {
        FB.ui({
            method: 'share',
            display: 'popup',
            href: sharedURL
        }, function(response) {
            // Check for an actual response object to be returned,
            // only occurs on successful sharing
            if (response !== undefined && updateURL) {
                requests.patch({
                        url: updateURL,
                        data: JSON.stringify({shared_on_facebook: true})
                    })
                    .done(function() {
                        $.notify({message: "Thanks for sharing your Mission!", type: "success"});
                });
            }
        });
    };
}
