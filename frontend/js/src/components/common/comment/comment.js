var Handlebars = require('handlebars'),
    request = require('api').request,
    createCommentTemplate = require('./templates/create_comment.hbs'),
    commentsTemplate = require('./templates/comments.hbs');


export function comment() {
    Handlebars.registerPartial('create_comment', createCommentTemplate);
    Handlebars.registerPartial('comments', commentsTemplate);
    var $app = $(".app-sb");
    $app
        .on('initialize', '.js-comment-load', function (event) {
            console.log('here')
            var parentId = this.dataset.parent_id;
            console.log(parentId);
        })
}


function saveComments(){
    $(commentArea).click(function (event) {
        $(commentArea).attr("disabled", "disabled");
        event.preventDefault();
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "POST",
            url: url + "?html=true&expedite=true",
            data: JSON.stringify({
                'content': $('textarea#post_comment_on_' + objectUuid).val(),
                'object_uuid': $(this).data('object_uuid')
            }),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (data) {
                var commentContainer = $("#sb_comments_container_" + objectUuid);
                commentContainer.append(data.html);
                $('textarea#post_comment_on_' + objectUuid).val("");
                enableCommentFunctionality(data.ids);
                $(commentArea).removeAttr("disabled");
            },
            error: function (XMLHttpRequest) {
                $(commentArea).removeAttr("disabled");
                errorDisplay(XMLHttpRequest);
            }
        });
    });
}

function showEditComment() {
    $("a.show_edit_comment_class").click(function () {
        var objectUuid = $(this).data('comment_uuid');
        $("#sb_content_" + objectUuid).hide();
        $('#edit_container_' + objectUuid).show();
        var textarea = $('textarea#' + $(this).data('comment_uuid'));
        textarea.height(textarea[0].scrollHeight);
    });
}


function populateComment(objectUuid, resource) {
    $.ajax({
        xhrFields: {withCredentials: true},
        type: "GET",
        // TODO probably want to make a /v1/content/ endpoint so that it's more
        // explanitory that comments can be on any piece of content.
        // Then use /posts/questions/solutions where needed
        url: "/v1/" + resource + "/" + objectUuid + "/comments/render/?expedite=true&expand=true&html=true&page_size=3",
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (data) {
            var commentContainer = $('#sb_comments_container_' + objectUuid);
            commentContainer.append(data.results.html);
            if (data.count > 3) {
                // TODO this may break in IE
                commentContainer.append(
                        '<div class="row" id="additional-comment-wrapper-' + objectUuid + '">' +
                        '<div class="col-sm-5 col-xs-offset-1">' +
                        '<a href="javascript:;" class="additional-comments" id="additional-comments-' + objectUuid + '">Show Older Comments ...</a>' +
                        '</div>' +
                        '</div>');
            }
            enableCommentFunctionality(data.results.ids);
        },
        error: function (XMLHttpRequest) {
            errorDisplay(XMLHttpRequest);
        }
    });
}


function populateComments(objectUuids, resource) {
    if (typeof objectUuids !== 'undefined' && objectUuids.length > 0) {
        for (var i = 0; i < objectUuids.length; i+=1) {
            populateComment(objectUuids[i], resource);
        }
    }
}