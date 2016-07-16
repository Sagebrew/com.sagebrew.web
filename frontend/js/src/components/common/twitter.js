/* global twttr */
var requests = require('api').request;
/*
 * Allow users to share a Mission (may add other objects in the future) on FB
 */
export function sharing(updateURL) {
    requests.patch({
        url: updateURL,
        data: JSON.stringify({shared_on_twitter: true})
    })
    .done(function() {
       location.reload()
    });
}
