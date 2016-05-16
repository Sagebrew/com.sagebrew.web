var request = require('api').request,
    helpers = require('common/helpers'),
    mediumEditor = require('common/mediumeditorhelper').createMediumEditor;

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
    var solutionID = helpers.args(2),
        $secondnav = $(".navbar-secondary"),
        editor;
    request.get({url: "/v1/solutions/" + solutionID + "/"})
        .done(function (data) {
            var solutionContent = $('.editable');
            solutionContent.html(data.content);
        });
    editor = mediumEditor(".editable", "")
    // This is a solution to our edit solution content being dynamically
    // populated, meaning we cant pass the back_url parameter to the
    // secondary navbar
    $secondnav.on('click', ".navbar-brand-secondary", function(event) {
        event.preventDefault();
        history.back();
    });

    $secondnav.on('click', '#submit', function(event) {
        event.preventDefault();
        document.getElementById('sb-greyout-page').classList.remove('sb_hidden');
        var serialized = editor.serialize(),
            key = Object.keys(serialized)[0];
        $("#submit").attr("disabled", "disabled");
        request.put({url: "/v1/solutions/" + solutionID + "/",
            data: JSON.stringify({
                'content': serialized[key].value
            })
        })
        .done(function (data) {
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