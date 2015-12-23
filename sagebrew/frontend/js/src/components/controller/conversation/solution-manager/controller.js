var addMarkdown = require('common/markdown').addMarkdown,
    request = require('api').request,
    helpers = require('common/helpers');

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
        $app = $(".app-sb");
    addMarkdown($('#solution_content_id'));
    request.get({url: "/v1/solutions/" + solutionID + "/"})
        .done(function (data) {
            var solution_content = $('#wmd-input-0');
            solution_content.html("");
            solution_content.append(data.content);
            var solution_preview = $("#wmd-preview-0");
            solution_preview.html("");
            solution_preview.append(data.html_content);
        });

    $app
        .on('click', '#submit', function(event) {
            event.preventDefault();
            $("#submit").attr("disabled", "disabled");
            request.put({url: "/v1/solutions/" + solutionID + "/",
                data: JSON.stringify({
                    'content': $('textarea#wmd-input-0').val()
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