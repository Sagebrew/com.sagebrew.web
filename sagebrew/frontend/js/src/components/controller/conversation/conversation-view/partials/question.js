/* global enableQuestionFunctionality, populateComments, loadSolutions */
/**
 * TODO refactor and include the above globals.
 */
var Autolinker = require('autolinker'),
    request = require('api').request,
    templates = require('template_build/templates'),
    helpers = require('common/helpers');

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

function findPos(obj) {
    var curtop = 0;
    if (obj.offsetParent) {
        do {
            curtop += obj.offsetTop;
        } while (obj = obj.offsetParent);
    return [curtop];
    }
}

export function load () {
    var timeOutId = 0,
        questionID = window.location.pathname.match("([A-Za-z0-9.@_%+-]{36})")[0],
        $app = $(".app-sb");
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

    $app
        .on('click', '.js-comment', function (event) {
            event.preventDefault();
            var parent = helpers.findAncestor(this, 'js-comment-section');
            var commentInput = parent.getElementsByClassName('js-comment-input')[0];
            commentInput.classList.remove('hidden');
            this.classList.add('hidden');
            commentInput.innerHTML = templates.comment_input({
                parent_type: parent.dataset.type,
                parent_id: parent.dataset.id,
                placeholder_text: "Help improve the " + parent.dataset.type.replace(/\w\S*/g, function(txt){return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();}) + " by providing feedback"});
            var inputArea = document.getElementById('comment-input-' + parent.dataset.id);
            var commentContainer = document.getElementById('sb_comments_container_' + parent.dataset.id);
            if(commentContainer.innerText.length > 0){
                $("body").scrollTop($(inputArea).offset().top - 250);
            }
        })
        .on('click', '.comment-btn', function (event) {
            event.preventDefault();
            var $this = this;
            var parent = helpers.findAncestor(this, 'comment-input');
            var commentSection = helpers.findAncestor(this, 'js-comment-section');
            var textArea = parent.getElementsByTagName('textarea')[0];
            this.setAttribute('disabled', 'disabled');
            request.post({url: "/v1/" + parent.dataset.type + "s/" + parent.dataset.id + "/comments/?html=true&expedite=true",
                data: JSON.stringify({
                    'content': textArea.value
                })})
                .done(function (data) {
                    var commentContainer = commentSection.getElementsByClassName('js-comment-container')[0];
                    commentContainer.innerHTML = commentContainer.innerHTML + data.html;
                    textArea.value = "";
                    $this.removeAttribute('disabled');
                })
                .fail(function () {
                    $this.removeAttribute('disabled');
                    errorDisplay(XMLHttpRequest);
                });
        });
}
