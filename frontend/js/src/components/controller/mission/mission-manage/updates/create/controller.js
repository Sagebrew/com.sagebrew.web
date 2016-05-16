var request = require('api').request,
    validators = require('common/validators'),
    mediumEditor = require('common/mediumeditorhelper').createMediumEditor,
    args = require('common/helpers').args;

export const meta = {
    controller: "mission/mission-manage/updates/create",
    match_method: "path",
    check: [
        "^missions\/[A-Za-z0-9.@_%+-]{36}\/[A-Za-z0-9.@_%+-]{1,140}\/manage\/updates\/create$"
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
    var missionId = window.location.pathname.match("([A-Za-z0-9.@_%+-]{36})")[0],
        $secondnav = $(".navbar-secondary"),
        editor = mediumEditor(".editable", "Type your content here"),
        $title = $("#js-title");
    $secondnav.on('click', '#submit', function(event) {
        event.preventDefault();
        var serialized = editor.serialize(),
            key = Object.keys(serialized);
        document.getElementById('sb-greyout-page').classList.remove('sb_hidden');
        request.post({url: "/v1/missions/" + missionId + "/updates/",
            data: JSON.stringify(
                {
                    'content': serialized[key].value,
                    'title': $title.val(),
                    'about_type': 'mission',
                    'about_id': missionId})
        }).done(function (){
            window.location.href = '/missions/' + missionId + '/' + args(2) + '/manage/updates/';
        });
    }).on('click', '#cancel', function(event) {
            event.preventDefault();
            window.location.href = '/missions/' + missionId + '/' + args(2) + '/manage/updates/';
        });

    validators.updateValidator($("#updateForm"));
}

/**
 * Post Load
 */
export function postload() {
    //
    // Intercom Tracking
}