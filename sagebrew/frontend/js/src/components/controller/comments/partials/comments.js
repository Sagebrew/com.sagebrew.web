/* global enableQuestionFunctionality, populateComments, loadSolutions */
/**
 * TODO refactor and include the above globals.
 */
var Autolinker = require('autolinker'),
    request = require('api').request,
    templates = require('template_build/templates'),
    helpers = require('common/helpers');

function queryComments(url, objectUuid) {
    request.get({url: url})
        .done(function (data) {
            if (data.next !== null) {
                queryComments(data.next, objectUuid);
            }
            var commentContainer = $('#sb_comments_container_' + objectUuid);
            commentContainer.prepend(data.results.html);
            enableCommentFunctionality(data.results.ids);
        });
}

export function load () {
    var $app = $(".app-sb");
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
                placeholder_text: "Help improve the " + parent.dataset.type.replace(/\w\S*/g, function (txt) {
                    return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
                }) + " by providing feedback"
            });
            var inputArea = document.getElementById('comment-input-' + parent.dataset.id);
            var commentContainer = document.getElementById('sb_comments_container_' + parent.dataset.id);
            if (commentContainer.innerText.length > 0) {
                $("body").scrollTop($(inputArea).offset().top - 250);
            }
        })
        .on('click', '.additional-comments', function (event) {
            // TODO this is common for all content
            event.preventDefault();
            var parent = helpers.findAncestor(this, 'js-comment-section');
            request.get({url: "/v1/" + parent.dataset.type + "s/" + parent.dataset.id + "/comments/render/?expand=true&html=true&page_size=3&page=2"})
                .done(function (data) {
                    var commentContainer = document.getElementById('sb_comments_container_' + parent.dataset.id);
                    var additionalCommentWrapper = document.getElementById('additional-comment-wrapper-' + parent.dataset.id)
                    if (additionalCommentWrapper !== null) {
                        additionalCommentWrapper.remove();
                    }
                    $(commentContainer).prepend(data.results.html);
                    // TODO: May be able to use content loader here
                    // TODO opportunity to get rid of ?html=true in this file too
                    if (data.next !== null) {
                        queryComments(data.next, parent.dataset.id);
                    }
                    enableCommentFunctionality(data.results.ids);
                });
        })
        .on('click', '.comment-btn', function (event) {
            event.preventDefault();
            var $this = this;
            var parent = helpers.findAncestor(this, 'comment-input');
            var commentSection = helpers.findAncestor(this, 'js-comment-section');
            var textArea = parent.getElementsByTagName('textarea')[0];
            this.setAttribute('disabled', 'disabled');
            request.post({
                    url: "/v1/" + commentSection.dataset.type + "s/" + commentSection.dataset.id + "/comments/?html=true&expedite=true",
                    data: JSON.stringify({
                        'content': textArea.value
                    })
                })
                .done(function (data) {
                    var commentContainer = commentSection.getElementsByClassName('js-comment-container')[0];
                    commentContainer.innerHTML = commentContainer.innerHTML + data.html;
                    var additionalCommentWrapper = document.getElementById('additional-comment-wrapper-' + commentSection.dataset.id);
                    if (additionalCommentWrapper !== null) {
                        additionalCommentWrapper.remove();
                        commentContainer.innerHTML = commentContainer.innerHTML + templates.show_more_comments({id: commentSection.dataset.id})
                    }
                    textArea.value = "";
                    $this.removeAttribute('disabled');
                })
                .fail(function () {
                    $this.removeAttribute('disabled');
                    errorDisplay(XMLHttpRequest);
                });
        });
}