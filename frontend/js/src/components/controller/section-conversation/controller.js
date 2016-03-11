var request = require('api').request,
    Autolinker = require('autolinker'),
    missions = require('common/missions'),
    helpers = require('common/helpers'),
    questionTemplate = require('./templates/question.hbs'),
    solutionTemplate = require('./templates/solution.hbs');

export const meta = {
    controller: "section-conversation",
    match_method: "path",
    check: [
       "^conversations/[A-Za-z0-9.@_%+-]{36}"
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
    var questionID = helpers.args(1),
        $appSolutions = $("#js-conversation-solutions"),
        $app = $(".app-sb");

    request.get({url: "/v1/questions/" + questionID + "/?expand=true"})
        .done(function (data) {
            data = helpers.votableContentPrep([data])[0];
            document.getElementById('js-conversation-question').innerHTML = Autolinker.link(questionTemplate(data));
            $app.trigger("sb:populate:comments", {
                id: questionID,
                type: "question",
                commentType: "base"
            });
            $('[data-toggle="tooltip"]').tooltip();
            $appSolutions.sb_contentLoader({
                emptyDataMessage: 'Be the first to provide a Solution!',
                url: "/v1/questions/" + questionID + "/solutions/",
                params: {
                    expand: "true"
                },
                dataCallback: function (base_url, params) {
                    var urlParams = $.param(params);
                    var url;
                    if (urlParams) {
                        url = base_url + "?" + urlParams;
                    }
                    else {
                        url = base_url;
                    }
                    return request.get({url: url});
                },
                renderCallback: function ($container, data) {
                    data.results = helpers.votableContentPrep(data.results);
                    for (var i = 0; i < data.results.length; i++) {
                        $container.append(Autolinker.link(solutionTemplate(data.results[i])));
                        $('[data-toggle="tooltip"]').tooltip();
                        $app.trigger("sb:populate:comments", {
                            id: data.results[i].id,
                            type: data.results[i].type,
                            commentType: "base"
                        });
                    }
                }
            })
        });
}

/**
 * Post Load
 */
export function postload() {
    //
    // Intercom Tracking
}
