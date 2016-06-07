/* global Autolinker */
var request = require('api').request,
    helpers = require('common/helpers'),
    Handlebars = require('handlebars'),
    questionTemplate = require('../templates/question.hbs');


export function load () {
    var $app = $(".app-sb"),
        questionID = helpers.args(1);
    Handlebars.registerPartial('question', questionTemplate);
    request.get({url: "/v1/questions/" + questionID + "/?expand=true"})
        .done(function (data) {
            data = helpers.votableContentPrep([data])[0];
            document.getElementById('js-conversation-question').innerHTML = Autolinker.link(questionTemplate(data));
            $app.trigger("sb:populate:comments", {
                id: questionID,
                type: "question",
                commentType: "base"
            });
            $app.trigger("sb:populate:solutions", {
                id: questionID,
                solutionType: "base",
                insertElement: "#js-conversation-solutions"
            });
            $('[data-toggle="tooltip"]').tooltip();
            helpers.disableFigcapEditing($('#js-conversation-question'));
        });
    $app
        .on('click', '.js-delete-question', function() {
            var objectID = this.dataset.id;
            request.remove({
                url: "/v1/questions/" + this.dataset.id + "/"
            }).done(function () {
                document.getElementById("question-block-" + objectID).remove();
            });
        });
}

