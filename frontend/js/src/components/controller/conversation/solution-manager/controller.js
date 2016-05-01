/* global AutoList */
var request = require('api').request,
    helpers = require('common/helpers'),
    mediumEditor = require('medium-editor');

/**
 * Meta.
 */
export const meta = {
    controller: "conversation/solution-manager",
    match_method: "path",
    check: [
        "^conversations\/solutions\/[A-Za-z0-9.@_%+-]{36}\/edit"
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
    var solutionID = helpers.args(2),
        $app = $(".app-sb"),
        autolist = new AutoList(),
        editor = new mediumEditor(".editable", {
            buttonLabels: true,
            autoLink: true,
            extensions: {
                "autolist": autolist
            },
            placeholder: false
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
    request.get({url: "/v1/solutions/" + solutionID + "/"})
        .done(function (data) {
            var solutionContent = $('.editable');
            solutionContent.html(data.content);
        });

    $app
        .on('click', '#submit', function(event) {
            event.preventDefault();
            var serialized = editor.serialize(),
                key = Object.keys(serialized)[0];
            $("#submit").attr("disabled", "disabled");
            request.put({url: "/v1/solutions/" + solutionID + "/",
                data: JSON.stringify({
                    'content': serialized[key].value
                })
            }).done(function (data) {
                $("#submit").removeAttr("disabled");
                window.location.href = data.url;
            })
            .fail(function () {
                $("#submit").removeAttr("disabled");
            });
        })
        .on('click', '#cancel', function (event) {
            event.preventDefault();
            history.back();
        });
}

/**
 * Post Load
 */
export function postload() {
}