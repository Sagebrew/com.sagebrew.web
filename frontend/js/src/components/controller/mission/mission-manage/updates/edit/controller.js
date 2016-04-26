var request = require('api').request,
    markdown = require('common/markdown').addMarkdown,
    validators = require('common/validators'),
    helpers = require('common/helpers'),
    mediumEditor = require('medium-editor');;


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
    require('medium-editor-insert-plugin');
    var $app = $(".app-sb"),
        missionId = helpers.args(1),
        updateId = helpers.args(5),
        missionSlug = helpers.args(2),
        editor = new mediumEditor(".editable", {
            buttonLabels: true,
            autoLink: true
        });
    $(".editable").mediumInsert({
        editor: editor,
        addons: {
            images: {
                fileUploadOptions: {
                    url: "/v1/upload/?editor=true",
                    acceptFileTypes: /(.|\/)(gif|jpe?g|png)$/i,
                    paramName: "file_object"
                }
            },
            embeds: {
                oembedProxy: null
            }
        }
    });
    validators.editUpdateValidator($('updateForm'));
    $app
        .on('click', '#edit-update', function (e) {
            e.preventDefault();
            var serialized = editor.serialize(),
                key = Object.keys(serialized)[0],
                title = $("#js-title");
            $(this).attr("disabled", "disabled");
            request.patch({url: "/v1/updates/" + updateId + "/", data: JSON.stringify({
                "content": serialized[key].value,
                "title": title.val()
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