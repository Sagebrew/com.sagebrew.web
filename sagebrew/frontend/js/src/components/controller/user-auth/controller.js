/**
 * @file
 * Authed User Controller. Loaded on every page loaded by a logged in user.
 */
var navbar = require('./partials/navbar').initNavbar,
    request = require('./../../api').request;



/**
 *  Scope - User Authed
 *  Adds an event handler to page unload that ajax posts all the user's actions that occured during the page.
 *  TODO: Stop doing this.
 *  Not only are non-async ajax calls deprecated it holds the page load up for the user.
 *  They can't even start loading the next page until this is completed.
 */
function collectAuthedActions() {
    /* Commenting this out as we no longer need this functionality.
    $(document).ready(function () {
        window.onbeforeunload = function () {
            var objectList = JSON.parse(localStorage.getItem("objectUpdates"));
            if (objectList) {
                localStorage.removeItem("objectUpdates");
                request.post({
                    async: false,
                    url: "/docstore/update_neo_api/",
                    data: JSON.stringify({
                        'object_uuids': objectList
                    })
                });
            }
        };
    });
    */
}





export function init() {
    collectAuthedActions();

    $(document).ready(function() {
        navbar();
    });

}


