var request = require('api').request,
    templates = require('template_build/templates'),
    helpers = require('common/helpers');


export const meta = {
    controller: "council/edit_position",
    match_method: "path",
    check: [
        "^council\/positions\/[A-Za-z0-9.@_%+-]{36}\/edit$"
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
    var nameInput = $("#js-position-edit"),
        submitEdit = $("#js-submit-edit");
    console.log(helpers.args());
    submitEdit.on("click", function(){
        request.patch({url: "/v1/positions/" + helpers.args(2) + "/council_update/", data:JSON.stringify({name: nameInput.val()})})
            .done(function(data){
                window.location.href = "/council/positions/";
            });
    });


}

/**
 * Post Load
 */
export function postload() {
    //
    // Intercom Tracking
}