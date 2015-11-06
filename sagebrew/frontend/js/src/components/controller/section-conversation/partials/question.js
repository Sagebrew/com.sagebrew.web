var Autolinker = require('autolinker'),
    request = require('./../../../api').request;

export function load () {
    "use strict";
    var timeOutId = 0,
        questionID = window.location.pathname.match("([A-Za-z0-9.@_%+-]{36})")[0];
    request.get({url: '/v1/questions/' + questionID + '/?html=true&expand=true&expedite=true'})
        .done(function (data) {
            var questionContainer = $('#single_question_wrapper');
            questionContainer.append(Autolinker.link(data.html));
            loadSolutionCount();
            enableQuestionFunctionality(data.ids);
            populateComments(data.ids, "questions");
            loadSolutions("/v1/questions/" + questionID + "/solutions/render/?page_size=10&expand=true");
        })
        .fail(function(){
            timeOutId = setTimeout(load, 1000);
        })
}
