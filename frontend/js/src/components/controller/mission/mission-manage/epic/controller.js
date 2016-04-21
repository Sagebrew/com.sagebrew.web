var request = require('api').request,
    markdown = require('common/markdown').addMarkdown,
    mediumEditor = require('medium-editor');

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
        editor = new mediumEditor(".editable", {
            buttonLabels: true
        });
    $(".editable").mediumInsert({
        editor: editor
    });

    $app
        .on('click', '#submit', function(event) {
            event.preventDefault();
            request.patch({url: "/v1/missions/" + missionId + "/",
                data: JSON.stringify({'epic': $('textarea#wmd-input-0').val()})
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