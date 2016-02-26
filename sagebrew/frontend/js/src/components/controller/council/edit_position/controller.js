var request = require('api').request,
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
    var nameInput = $("#js-name"),
        submitEdit = $("#js-submit-edit"),
        branchInput = $("#branch-input"),
        id = helpers.args(2);
    request.get({url: "/v1/positions/" + id + "/"})
        .done(function(data){
            nameInput.val(data.name);
            branchInput.val(data.office_type);
        });
    submitEdit.on("click", function(){
        console.log(branchInput.val());
        request.patch({url: "/v1/positions/" + helpers.args(2) + "/council_update/", data:JSON.stringify({name: nameInput.val(), office_type: branchInput.val()})})
            .done(function(){
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