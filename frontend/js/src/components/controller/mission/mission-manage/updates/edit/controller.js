/* global AutoList */
var request = require('api').request,
    validators = require('common/validators'),
    helpers = require('common/helpers'),
    mediumEditor = require('medium-editor');


export const meta = {
    controller: "mission/mission-manage/updates/edit",
    match_method: "path",
    check: [
        "^missions\/[A-Za-z0-9.@_%+-]{36}\/[A-Za-z0-9.@_%+-]{1,140}\/manage\/updates\/[A-Za-z0-9.@_%+-]{36}\/edit$"
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
    var updateId = helpers.args(5),
        autolist = new AutoList(),
        editor = new mediumEditor(".editable", {
            buttonLabels: 'fontawesome',
            autoLink: true,
            toolbar: {
                buttons: ['bold', 'italic', 'underline', 'anchor', 'h2',
                    'h3', 'justifyLeft', 'justifyCenter', 'justifyRight', 'quote']
            },
            extensions: {
                'autolist': autolist
            }
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
    $("#submit").on('click', function(event) {
        event.preventDefault();
        var serialized = editor.serialize(),
            key = Object.keys(serialized)[0],
            title = $("#js-title");
        $(this).attr("disabled", "disabled");
        request.patch({
                url: "/v1/updates/" + updateId + "/", 
                data: JSON.stringify({"content": serialized[key].value, "title": title.val()
            })
        }).done(function () {
            window.history.back();
        });
    });
    $("#cancel").on('click', function(event) {
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