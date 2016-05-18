var request = require('api').request,
    mediumEditor = require('common/mediumeditorhelper').createMediumEditor,
    moment = require('moment'),
    args = require('common/helpers').args;

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

function finishedTyping(editor, missionId) {
    var serialized = editor.serialize(),
        key = Object.keys(editor.serialize())[0];
    console.log(serialized[key].value);
    request.patch({url: "/v1/missions/" + missionId + "/",
        data: JSON.stringify(
                {'temp_epic': serialized[key].value})
    }).done(function (){
        $("#livestamp").livestamp(moment().format());
    });
}

/**
 * Load
 */
export function load() {
    var missionId = window.location.pathname.match("([A-Za-z0-9.@_%+-]{36})")[0],
        $secondnav = $(".navbar-secondary"),
        typingTimer,
        // how long after typing has finished should we auto save? 1000=1 second, 10000=10 seconds, etc.
        finishedTypingInterval = 1000,
        editor = mediumEditor(".editable", "Type your Epic here"),
        $editable = $(".editable"),
        slug = args(2);
    $editable.on('keyup', function() {
        clearTimeout(typingTimer);
        typingTimer = setTimeout(
            function(){finishedTyping(editor, missionId);},
            finishedTypingInterval);
    });

    $editable.on('keydown', function() {
        clearTimeout(typingTimer);
    });

    $secondnav.on('click', '#cancel', function(event){
        event.preventDefault();
        request.post({url: "/v1/missions/" + missionId + "/reset_epic/",
        }).done(function (){
            window.location.href = "/missions/" + missionId + "/" + slug + "/manage/epic/";
        });
    })
        .on('click', '#submit', function(event){
            event.preventDefault();
            document.getElementById('sb-greyout-page').classList.remove('sb_hidden');
            var serialized = editor.serialize(),
                key = Object.keys(editor.serialize())[0];
            request.patch({url: "/v1/missions/" + missionId + "/",
                data: JSON.stringify(
                        {'temp_epic': serialized[key].value, 'epic': serialized[key].value})
            }).done(function (){
                window.location.href = "/missions/" + missionId + "/" + slug + "/manage/epic/";
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