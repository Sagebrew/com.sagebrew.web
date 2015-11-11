/**
 * @file
 * Authed User Controller. Loaded on every page loaded by a logged in user.
 */
var navbar = require('./partials/navbar').initNavbar,
    request = require('api').request;


/**
 * Meta.
 */
export const meta = {
    controller: "user-auth",
    match_method: "user",
    check: "auth"
};


/**
 * Load.
 */
export function load() {
    navbar();

    //
    // Collect
    window.onbeforeunload = function () {
        var objectList = [];
        $(".js-page-object").each(function () {
            objectList.push($(this).data('object_uuid'));
        });
        if (objectList.length) {
            request.post({
                async: false,
                url: "/docstore/update_neo_api/",
                data: JSON.stringify({
                    'object_uuids': objectList
                })
            });
        }
    };
}