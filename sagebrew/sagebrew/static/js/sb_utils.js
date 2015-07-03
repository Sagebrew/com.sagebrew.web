/**
 * csrftoken support for django
 */
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i += 1) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?

            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$.ajaxSetup({
    beforeSend: function (xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        }
    }
});

function saveComment(commentArea, url, objectUuid) {
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


function saveComments(populatedIds, url) {
    if (typeof populatedIds !== 'undefined' && populatedIds.length > 0) {
        for (var i = 0; i < populatedIds.length; i += 1) {
            saveComment(".comment_" + populatedIds[i],
                    url + populatedIds[i] + "/comments/", populatedIds[i]);
        }
    }
}


function showEditPost(editArea) {
    $(editArea).click(function () {
        var objectUuid = $(this).data('uuid');
        $("#sb_content_" + objectUuid).hide();
        $('#edit_container_' + objectUuid).show();
        var textarea = $('textarea#' + $(this).data('uuid'));
        textarea.height(textarea[0].scrollHeight);
    });
}

function showEditPosts(populatedIds) {
    if (typeof populatedIds !== 'undefined' && populatedIds.length > 0) {
        for (var i = 0; i < populatedIds.length; i += 1) {
            showEditPost("a.show_edit_post_" + populatedIds[i]);
        }
    } else {
        showEditPost("a.show_edit_post_class");
    }
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
                commentContainer.prepend(
                        '<div class="row">' +
                        '<div class="col-lg-5 col-lg-offset-1">' +
                        '<a href="javascript:;" class="additional_comments" id="additional_comments_' + objectUuid + '">More Comments ...</a>' +
                        '</div>' +
                        '</div>');
                $('#additional_comments_' + objectUuid).click(function () {
                    $.ajax({
                        xhrFields: {withCredentials: true},
                        type: "GET",
                        url: "/v1/" + resource + "/" + objectUuid + "/comments/render/?expand=true&html=true&page_size=3&page=2",
                        contentType: "application/json; charset=utf-8",
                        dataType: "json",
                        success: function (data) {
                            var commentContainer = $('#sb_comments_container_' + objectUuid);
                            $('#additional_comments_' + objectUuid).remove();
                            commentContainer.prepend(data.results.html);
                            if (data.next !== null) {
                                queryComments(data.next, objectUuid);
                            }
                            enableCommentFunctionality(data.results.ids);
                        },
                        error: function (XMLHttpRequest) {
                            errorDisplay(XMLHttpRequest);
                        }
                    });
                });

            }
            enableCommentFunctionality(data.results.ids);
        },
        error: function (XMLHttpRequest) {
            errorDisplay(XMLHttpRequest);
        }
    });
}

function queryComments(url, objectUuid) {
    $.ajax({
        xhrFields: {withCredentials: true},
        type: "GET",
        url: url,
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (data) {
            if (data.next !== null) {
                queryComments(data.next, objectUuid);
            }
            var commentContainer = $('#sb_comments_container_' + objectUuid);
            commentContainer.prepend(data.results.html);
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


function toolTipObject(toolObject) {
    $(toolObject).tooltip();
}

function readyVotes(objectUuids) {
    if (typeof objectUuids !== 'undefined' && objectUuids.length > 0) {
        for (var i = 0; i < objectUuids.length; i += 1) {
            toolTipObject("#upvote_" + objectUuids[i]);
            toolTipObject("#downvote_" + objectUuids[i]);
        }
    }
}

function readyComments(objectUuids) {
    "use strict";
    if (typeof objectUuids !== 'undefined' && objectUuids.length > 0) {
        for (var i = 0; i < objectUuids.length; i += 1) {
            toolTipObject("#post_comment_on_" + objectUuids[i]);
        }
    }
}

function readyFlags(objectUuids) {
    if (typeof objectUuids !== 'undefined' && objectUuids.length > 0) {
        for (var i = 0; i < objectUuids.length; i += 1) {
            toolTipObject("#flag_" + objectUuids[i]);
        }
    }
}


function loadPosts(url) {
    $("#wall_app").spin({lines: 8, length: 4, width: 3, radius: 5});
    $.ajax({
        xhrFields: {withCredentials: true},
        type: "GET",
        url: url,
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (data) {
            var wallContainer = $('#wall_app');
            if (data.count === 0) {
                wallContainer.append('<div id="js-wall_temp_message"><h3>Add a Spark :)</h3></div>');
            } else {
                wallContainer.append(data.results.html);
                // TODO Went with this approach as the scrolling approach resulted
                // in the posts getting out of order. It also had some interesting
                // functionality that wasn't intuitive. Hopefully transitioning to
                // a JS Framework allows us to better handle this feature.
                if (data.next !== null) {
                    loadPosts(data.next);
                }
                enableSinglePostFunctionality(data.results.ids);
                // TODO This can probably be changed to grab the href and append
                // `comments/` to the end of it.
                populateComments(data.results.ids, "posts");
            }
            wallContainer.spin(false);
        },
        error: function (XMLHttpRequest) {
            errorDisplay(XMLHttpRequest);
        }
    });
}


function loadQuestion() {
    var timeOutId = 0;
    var ajaxFn = function () {
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "GET",
            url: "/v1/questions/" + $('.div_data_hidden').data('question_uuid') + "/?html=true&expand=true&expedite=true",
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (data) {
                var questionContainer = $('#single_question_wrapper');
                questionContainer.append(data.html);
                loadSolutionCount();
                enableQuestionFunctionality(data.ids);
                populateComments(data.ids, "questions");
                loadSolutions("/v1/questions/" + $('.div_data_hidden').data('question_uuid') + "/solutions/render/?page_size=10&expand=true");
            },
            error: function (XMLHttpRequest) {
                timeOutId = setTimeout(ajaxFn, 1000);
                errorDisplay(XMLHttpRequest);
            }
        });
    };
    ajaxFn();
}

function loadSolutionCount() {
    $.ajax({
        xhrFields: {withCredentials: true},
        type: "GET",
        url: "/v1/questions/" + $('.div_data_hidden').data('question_uuid') + "/solution_count/",
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (data) {
            $('#solution_count').html("");
            $('#solution_count').append(data.solution_count);
            if (data.solution_count !== '1') {
                $('#solution_plural').append('s');
            }
        },
        error: function (XMLHttpRequest) {
            errorDisplay(XMLHttpRequest);
        }
    });
}


function loadSolutions(url) {
    $.ajax({
        xhrFields: {withCredentials: true},
        type: "GET",
        url: url,
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (data) {
            var solutionContainer = $('#solution_container');
            solutionContainer.append(data.results.html);
            // TODO Went with this approach as the scrolling approach resulted
            // in the posts getting out of order. It also had some interesting
            // functionality that wasn't intuitive. Hopefully transitioning to
            // a JS Framework allows us to better handle this feature.
            if (data.next !== null) {
                loadSolutions(data.next);
            }
            enableSolutionFunctionality(data.results.ids);
            // TODO This can probably be changed to grab the href and append
            // `comments/` to the end of it.
            populateComments(data.results.ids, "solutions");
        },
        error: function (XMLHttpRequest) {
            errorDisplay(XMLHttpRequest);
        }
    });
}


function voteObject(voteArea, resource) {
    $(voteArea).click(function (event) {
        var objectUuid = $(this).data('object_uuid');
        var id = $(this).parents('div.vote_wrapper').attr('id').split('_')[1];
        var voteType = $(this).hasClass('vote_up') ? true : false;
        var voteDown = $(this).parents('div.vote_wrapper').find(".vote_down");
        var voteUp = $(this).parents('div.vote_wrapper').find(".vote_up");
        if (voteType === true) {
            voteUp.attr("disabled", "disabled");
        } else if (voteType === false) {
            voteDown.attr("disabled", "disabled");
        }
        // the reasoning for the addition of the 10 here is
        // http://solidlystated.com/scripting/missing-radix-parameter-jslint/
        var upvoteCount = parseInt($('#vote_count_' + objectUuid).text(), 10);
        if (voteDown.hasClass('vote_down_active') && voteType === true) {
            voteDown.removeClass('vote_down_active');
            voteUp.addClass('vote_up_active');
            upvoteCount += 2;
        } else if (voteDown.hasClass('vote_down_active') && voteType === false) {
            voteDown.removeClass('vote_down_active');
            upvoteCount += 1;
        } else if (voteUp.hasClass('vote_up_active') && voteType === true) {
            voteUp.removeClass('vote_up_active');
            upvoteCount -= 1;
        } else if (voteUp.hasClass('vote_up_active') && voteType === false) {
            voteDown.addClass('vote_down_active');
            voteUp.removeClass('vote_up_active');
            upvoteCount -= 2;
        } else {
            if (voteType === true) {
                $(this).addClass('vote_up_active');
                upvoteCount += 1;
            }
            else {
                $(this).addClass('vote_down_active');
                upvoteCount -= 1;
            }
        }

        event.preventDefault();
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "POST",
            url: "/v1/" + resource + "/" + objectUuid + "/votes/?expedite=true",
            data: JSON.stringify({
                'vote_type': voteType
            }),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function () {
                $('#vote_count_' + objectUuid).text(upvoteCount);
                $(voteArea).removeAttr("disabled");
            },
            error: function (XMLHttpRequest) {
                $(voteArea).removeAttr("disabled");
                errorDisplay(XMLHttpRequest);
            }
        });
    });
}

function voteObjects(populatedIds, resource) {
    if (typeof populatedIds !== 'undefined' && populatedIds.length > 0) {
        for (var i = 0; i < populatedIds.length; i += 1) {
            voteObject(".vote_" + populatedIds[i], resource);
        }
    }
}

function saveSolution() {
    $(".submit_solution-action").click(function (event) {
        event.preventDefault();
        $("#submit_solution").attr("disabled", "disabled");
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "POST",
            url: "/v1/questions/" + $(this).data('object_uuid') + "/solutions/?html=true&expand=true",
            data: JSON.stringify({
                'content': $('textarea.sb_solution_input_area').val()
            }),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (data) {
                $("#solution_container").append(data.html);
                $('textarea.sb_solution_input_area').val("");
                var solutionCountText = $("#solution_count").text();
                if (solutionCountText !== "--") {
                    // the reasoning for the addition of the 10 here is
                    // http://solidlystated.com/scripting/missing-radix-parameter-jslint/
                    var solutionCount = parseInt(solutionCountText, 10) + 1;
                    $("#solution_count").text(solutionCount.toString());
                }
                $('#wmd-preview-1').html("");
                $("#submit_solution").removeAttr("disabled");
                enableSolutionFunctionality(data.ids);
            },
            error: function (XMLHttpRequest) {
                $("#submit_solution").removeAttr("disabled");
                errorDisplay(XMLHttpRequest);
            }
        });
    });
}


function showEditQuestion() {
    $("a.show_edit_question-action").click(function (event) {
        event.preventDefault();
        window.location.href = "/conversations/questions/" + $(this).data('object_uuid') + "/edit/";
    });
}

function showEditSolution() {
    $("a.show_edit_solution-action").click(function (event) {
        event.preventDefault();
        var solutionUuid = $(this).data("object_uuid");
        window.location.href = "/conversations/solutions/" + solutionUuid + '/edit/';
    });
}


function editObject(editArea, url, objectUuid, dataArea) {
    $(editArea).click(function (event) {
        event.preventDefault();
        var editButton = ".edit_" + objectUuid;
        $(editButton).attr("disabled", "disabled");
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "PUT",
            url: url,
            contentType: "application/json; charset=utf-8",
            data: JSON.stringify({
                'content': $(dataArea).val()
            }),
            dataType: "json",
            success: function (data) {
                $(editButton).removeAttr("disabled");
                var contentContainer = $("#sb_content_" + objectUuid);
                contentContainer.text(data.content);
                $("#edit_container_" + objectUuid).hide();
                contentContainer.show();
            },
            error: function (XMLHttpRequest) {
                $(editButton).removeAttr("disabled");
                errorDisplay(XMLHttpRequest);
            }
        });
    });
}


function editObjects(url, populatedIds) {
    if (typeof populatedIds !== 'undefined' && populatedIds.length > 0) {
        for (var i = 0; i < populatedIds.length; i += 1) {
            // Eventually we should just be able to get the href
            editObject(".edit_" + populatedIds[i],
                    url + populatedIds[i] + "/", populatedIds[i], "textarea#" + populatedIds[i]);
        }
    }
}


function deleteObjects(url, populatedIds, objectType) {
    if (typeof populatedIds !== 'undefined' && populatedIds.length > 0) {
        for (var i = 0; i < populatedIds.length; i += 1) {
            deleteObject(".delete_" + populatedIds[i],
                    url + populatedIds[i] + "/", populatedIds[i], objectType);
        }
    }
}

function deleteObject(deleteArea, url, objectUuid, objectType) {
    $(deleteArea).click(function (event) {
        event.preventDefault();
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "DELETE",
            url: url,
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function () {
                $(".block_" + objectUuid).remove();
                if (objectType === 'solution') {
                    $('textarea.sb_solution_input_area').val("");
                    var solutionCountText = $("#solution_count").text();
                    if (solutionCountText !== "--") {
                        // the reasoning for the addition of the 10 here is
                        // http://solidlystated.com/scripting/missing-radix-parameter-jslint/
                        var solutionCount = parseInt(solutionCountText, 10) - 1;
                        $("#solution_count").text(solutionCount.toString());
                    }
                }
            },
            error: function (XMLHttpRequest) {
                errorDisplay(XMLHttpRequest);
            }
        });
    });
}


function cloneForm(selector, type) {
    var newElement = $(selector).clone(true);
    var total = $('#id_' + type + '_TOTAL_FORMS').val();
    newElement.find(':input').each(function () {
        var name = $(this).attr('name').replace('-' + (total - 1) + '-', '-' + total + '-');
        var id = 'id_' + name;
        $(this).attr({'name': name, 'id': id}).val('').removeAttr('checked');
    });
    newElement.find('label').each(function () {
        var newFor = $(this).attr('for').replace('-' + (total - 1) + '-', '-' + total + '-');
        $(this).attr('for', newFor);
    });
    total += 1;
    $('#id_' + type + '-TOTAL_FORMS').val(total);
    $(selector).after(newElement);
}

function commentValidator() {
    $("#commentSubmitForm").formValidation({
        framework: 'bootstrap',
        err: {
            container: '#fname_errors'
        },
        icon: {
            valid: 'glyphicon glyphicon-ok',
            validating: 'glyphicon glyphicon-refresh'
        },
        live: 'enabled',
        button: {
            selector: '.comment-action'
        },
        fields: {
            comment_content: {
                row: 'sb_comment',
                validators: {
                    notEmpty: {
                        message: "Content is required"
                    }
                }
            }
        }
    });
}

function submitAction() {
    $('#submit_action_form').click(function (event) {
        event.preventDefault();
        var data = {};
        var form = $('#action_form_id').serializeArray();
        $.each(form, function () {
            if (data[this.name] !== undefined) {
                if (!data[this.name].push) {
                    data[this.name] = [data[this.name]];
                }
                data[this.name].push(this.value || '');
            } else {
                data[this.name] = this.value || '';
            }
        });
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "POST",
            url: "/privilege/create/action/",
            data: JSON.stringify(data),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (data) {
                $(".action_form").remove();
                $(".get_action_form").removeAttr('disabled');
            },
            error: function (XMLHttpRequest) {
                errorDisplay(XMLHttpRequest);
            }
        });
    });
}

function submitRequirement() {
    $('#submit_requirement_form').click(function (event) {
        event.preventDefault();
        var data = {};
        var form = $('#requirement_form_id').serializeArray();
        $.each(form, function () {
            if (data[this.name] !== undefined) {
                if (!data[this.name].push) {
                    data[this.name] = [data[this.name]];
                }
                data[this.name].push(this.value || '');
            } else {
                data[this.name] = this.value || '';
            }
        });
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "POST",
            url: "/privilege/create/requirement/",
            data: JSON.stringify(data),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function () {
                $(".requirement_form").remove();
                $(".get_requirement_form").removeAttr('disabled');
            },
            error: function (XMLHttpRequest) {
                errorDisplay(XMLHttpRequest);
            }
        });
    });
}

function activateMontage() {
    var $container = $('#container').imagesLoaded(function () {
        $container.packery({
            gutter: 0,
            itemSelector: '.post_images',
            transitionDuration: 0,
            columnWidth: ".grid-sizer"
        });
    });
}

function respondFriendRequest() {
    $(".respond_friend_request-action").click(function (event) {
        event.preventDefault();
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "POST",
            url: "/relationships/respond_friend_request/",
            data: JSON.stringify({
                'response': $(this).data('response'),
                'request_id': $(this).data('request_id')
            }),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function () {
                $("#friend_request_div").fadeToggle();
            },
            error: function (XMLHttpRequest) {
                errorDisplay(XMLHttpRequest);
            }
        });
    });
}


function enableObjectFunctionality(populatedIds) {
    readyFlags(populatedIds);
    readyVotes(populatedIds);
    readyComments(populatedIds);
}


function enableFriendRequestFunctionality() {
    respondFriendRequest();
}

function enableCommentFunctionality(populatedIds) {
    enableObjectFunctionality(populatedIds);
    showEditComment(populatedIds);
    commentValidator();
    voteObjects(populatedIds, "comments");
    editObjects("/v1/comments/", populatedIds);
    deleteObjects("/v1/comments/", populatedIds, 'comment');
}

function enableQuestionSummaryFunctionality(populatedIds) {
    voteObjects(populatedIds, "questions");
    readyVotes(populatedIds);
}

function enableQuestionFunctionality(populatedIds) {
    enableObjectFunctionality(populatedIds);
    saveComments(populatedIds, "/v1/questions/");
    showEditQuestion(populatedIds);
    saveSolution(populatedIds);
    voteObjects(populatedIds, "questions");
    deleteObjects("/v1/questions/", populatedIds, 'question');
}

function enableSinglePostFunctionality(populatedIds) {
    enableObjectFunctionality(populatedIds);
    saveComments(populatedIds, '/v1/posts/');
    showEditPosts(populatedIds);
    voteObjects(populatedIds, "posts");
    editObjects("/v1/posts/", populatedIds);
    deleteObjects("/v1/posts/", populatedIds, 'post');
}

function enableSolutionFunctionality(populatedIds) {
    enableObjectFunctionality(populatedIds);
    saveComments(populatedIds, '/v1/solutions/');
    voteObjects(populatedIds, "solutions");
    showEditSolution(populatedIds);
    deleteObjects("/v1/solutions/", populatedIds, 'solution');
}

function enableContentFunctionality(populateId, type) {
    "use strict";
    enableObjectFunctionality([populateId]);
    saveComments([populateId], '/v1/'+ type + 's/');
    voteObjects([populateId], type + "s");
    editObjects("/v1/"+ type + "s/", [populateId]);
    deleteObjects("/v1/" + type +"s/", [populateId], type);
}

function getUrlParameter(sParam) {
    var sPageURL = window.location.search.substring(1);
    var sURLVariables = sPageURL.split('&');
    for (var i = 0; i < sURLVariables.length; i += 1) {
        var sParameterName = sURLVariables[i].split('=');
        if (sParameterName[0] === sParam) {
            return sParameterName[1];
        }
    }
}

function errorDisplay(XMLHttpRequest) {
    if (XMLHttpRequest.status === 500) {
        $.notify({message: "Sorry looks like we're having some server issues right now. "}, {type: "danger"});
    }
    if (XMLHttpRequest.status === 401) {
        $.notify({message: "Sorry doesn't look like you're allowed to do that. "}, {type: "danger"});
    }
    if (XMLHttpRequest.status === 400) {
        var notification, badItemCap, errorMessage, reportMsg;
        var notificationDetail = XMLHttpRequest.responseJSON;
        var notificationText = XMLHttpRequest.responseText;
        if (!(typeof notificationDetail === "undefined" || notificationDetail === null)) {
            notification = notificationDetail;
        } else if( notificationText !== undefined) {
            notification = notificationText;
        } else {
            $.notify({message: "Sorry looks like you didn't include all the necessary information."}, {type: 'danger'});
        }
        if (typeof(notification) !== 'object'){
            notification = JSON.parse(notification);
        } else {
            try
            {
                notification = JSON.parse(notification.detail);
            }
            catch(e) {
                $.notify({message: notification.detail}, {type: 'danger'});
                notification = [];
            }
        }
        for (var badItem in notification) {
            for (var message in notification[badItem]) {
                if (typeof(notification[badItem]) === 'object'){
                    reportMsg = notification[badItem][message].message;
                } else {
                    reportMsg = notification[badItem][message];
                }
                badItemCap = badItem.charAt(0).toUpperCase() + badItem.slice(1);
                errorMessage = badItemCap + ": " + reportMsg;
                $.notify({message: errorMessage.replace('_', " ")}, {type: 'danger'});
            }
        }

    }
    if (XMLHttpRequest.status === 404) {
        $.notify({message: "Sorry, we can't seem to find what you're looking for"}, {type: 'danger'});
    }
}
