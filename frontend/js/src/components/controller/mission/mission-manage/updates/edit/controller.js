var request = require('api').request,
    validators = require('common/validators'),
    helpers = require('common/helpers'),
    mediumEditor = require('common/mediumeditorhelper').createMediumEditor,
    args = require('common/helpers').args;


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
    var updateId = helpers.args(5),
        $secondnav = $(".navbar-secondary"),
        editor = mediumEditor(".editable", "Type your Update context here");
    validators.editUpdateValidator($('updateForm'));
    $secondnav.on('click', '#submit', function(event) {
        event.preventDefault();
        document.getElementById('sb-greyout-page').classList.remove('sb_hidden');
        var serialized = editor.serialize(),
            key = Object.keys(serialized)[0],
            title = $("#js-title");
        $(this).attr("disabled", "disabled");
        request.patch({
                url: "/v1/updates/" + updateId + "/", 
                data: JSON.stringify({"content": serialized[key].value, "title": title.val()
            })
        }).done(function () {
            var missionId = args(1),
                slug = args(2);
            window.location.href = "/missions/" + missionId + "/" + slug + "/manage/updates/";
        });
    })
        .on('click', '#cancel', function(event) {
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