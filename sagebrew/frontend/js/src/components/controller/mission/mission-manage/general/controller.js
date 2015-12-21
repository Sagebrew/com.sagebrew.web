var request = require('api').request;

export const meta = {
    controller: "mission/mission-manage/general",
    match_method: "path",
    check: [
        "^missions\/[A-Za-z0-9.@_%+-]{36}\/[A-Za-z0-9.@_%+-]{1,140}\/manage\/general"
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
    $app
        .on('click', '#submit', function(event) {
            event.preventDefault();
            var form = document.getElementById('socialForm');
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
            request.patch({url: "/v1/missions/" + missionId + "/",
                data: JSON.stringify(data)
            })
                .done(function (){
                    $.notify({message: "Updated Settings Successfully"}, {type: "success"});
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