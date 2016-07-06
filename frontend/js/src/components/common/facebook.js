/* global FB */

/*
 * Allow users to share a Mission (may add other objects in the future) on FB
 */
export function sharing(buttonId, sharedURL) {
    console.log(document.domain);
    document.getElementById(buttonId).onclick = function() {
        FB.ui({
            method: 'share',
            display: 'popup',
            href: sharedURL
        }, function(response) {});
    };
}
