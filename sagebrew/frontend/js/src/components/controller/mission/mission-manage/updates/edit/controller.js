var request = require('api').request,
    markdown = require('common/markdown').addMarkdown,
    validators = require('common/validators'),
    helpers = require('common/helpers');


export const meta = {
    controller: "mission/mission-manage/updates/edit",
    match_method: "path",
    check: [
        "^missions\/[A-Za-z0-9.@_%+-]{36}\/[A-Za-z0-9.@_%+-]{1,140}\/manage\/updates\/[A-Za-z0-9.@_%+-]{36}\/edit"
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
    var $app = $(".app-sb"),
        missionId = helpers.args(1),
        updateId = helpers.args(5),
        missionSlug = helpers.args(2);
    markdown($("textarea.markdown-input"));
    validators.editUpdateValidator($('updateForm'));
    $app
        .on('click', '#edit-update', function () {
            $(this).attr("disabled", "disabled");
            request.patch({url: "/v1/updates/" + updateId + "/", data: JSON.stringify({
                "content": $("#wmd-input-0").val(),
                "title": $("#title_id").val()
            })})
                .done(function () {
                    window.location.href = "/missions/" + missionId + "/" + missionSlug + "/manage/updates/";
                });
        })
        .on('click', '#js-cancel', function () {
            event.preventDefault();
            window.history.back();
        });
}

/**
 * Post Load
 */
export function postload() {
    //
    // Intercom Tracking
}