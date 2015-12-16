var request = require('api').request,
    markdown = require('common/markdown').addMarkdown;

export const meta = {
    controller: "mission/mission-manage/updates",
    match_method: "path",
    check: [
        "^missions\/[A-Za-z0-9.@_%+-]{36}\/[A-Za-z0-9.@_%+-]{1,140}\/manage\/updates"
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
        missionId = window.location.pathname.match("([A-Za-z0-9.@_%+-]{36})")[0];
    markdown($("textarea.markdown-input"));
    $app
        .on('click', '#submit', function(event) {
            event.preventDefault();
            var form = document.getElementById('updateForm');
            var data = {};
            for (var i = 0, ii = form.length; i < ii; ++i) {
                var input = form[i];
                // Don't check the value because if the use has entered a value
                // we prepopulate it. So if they remove it we want to set it to
                // an empty string in the backend.
                if (input.name) {
                  data[input.name] = input.value;
                }
            }
            if('content' in data && 'title' in data){
                request.post({url: "/v1/missions/" + missionId + "/updates/",
                    data: JSON.stringify(data)
                }).done(function (){
                    window.location.reload();
                });
            }

        });
}

/**
 * Post Load
 */
export function postload() {
    //
    // Intercom Tracking
}