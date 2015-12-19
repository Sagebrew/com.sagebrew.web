/* global enableQuestionFunctionality, populateComments, loadSolutions */
/**
 * TODO refactor and include the above globals.
 */
var Autolinker = require('autolinker'),
    request = require('api').request;

function loadSolutionCount(questionID) {
    request.get({url: '/v1/questions/' + questionID + "/solution_count/"})
        .done(function (data) {
            var solutionCount = $('#solution_count');
            solutionCount.html("");
            solutionCount.append(data.solution_count);
            if (data.solution_count === 0) {
                document.getElementById('js-solution-count-header').innerHTML = "Provide the First Solution";
            } else if (data.solution_count !== 1) {
                $('#solution_plural').append('s');
            }

        });
}

export function load () {
    var timeOutId = 0,
        questionID = window.location.pathname.match("([A-Za-z0-9.@_%+-]{36})")[0];
    request.get({url: '/v1/questions/' + questionID + '/?html=true&expand=true&expedite=true'})
        .done(function (data) {
            var questionContainer = $('#single_question_wrapper');
            questionContainer.append(Autolinker.link(data.html));
            loadSolutionCount(questionID);
            enableQuestionFunctionality(data.ids);
            populateComments(data.ids, "questions");
            loadSolutions("/v1/questions/" + questionID + "/solutions/render/?page_size=10&expand=true");
        })
        .fail(function(){
            timeOutId = setTimeout(load, 1000);
        });

}
