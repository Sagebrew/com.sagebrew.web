/* global AutoList */
var request = require('api').request,
    markdown = require('common/markdown').addMarkdown,
    mediumEditor = require('medium-editor'),
    intro = require('intro.js').introJs;

export const meta = {
    controller: "mission/mission-manage/epic",
    match_method: "path",
    check: [
       "^missions\/[A-Za-z0-9.@_%+-]{36}\/[A-Za-z0-9.@_%+-]{1,140}\/manage\/epic"
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
    /*
    markdown($("textarea.markdown-input"));
    require('drmonty-garlicjs');
    var epicForm = $("#epicForm");
    epicForm.garlic();
    */
    var $app = $(".app-sb"),
        missionId = window.location.pathname.match("([A-Za-z0-9.@_%+-]{36})")[0],
        autolist = new AutoList(),
        editor = new mediumEditor(".editable", {
            buttonLabels: 'fontawesome',
            autoLink: true,
            buttons: ['bold', 'italic', 'underline', 'anchor', 'h2', 'h3', 'h4', 'h5', 'h6', 'quote'],
            extensions: {
                'autolist': autolist
            }
        });
    intro().addHints();
    // Uploading images here via fileUploadOptions because submitting the
    // binary data directly causes browsers to crash if the images are
    // too large/there are too many images
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
    $app
        .on('click', '#submit', function(event) {
            event.preventDefault();
            var serialized = editor.serialize(),
                key = Object.keys(editor.serialize())[0];
            request.patch({url: "/v1/missions/" + missionId + "/",
                data: JSON.stringify({'epic': serialized[key].value})
            })
                .done(function (){
                    $.notify({message: "Saved Epic Successfully"}, {type: "success"});
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