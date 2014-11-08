function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function ajax_security(xhr, settings) {
    var csrftoken = $.cookie('csrftoken');
    if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
        xhr.setRequestHeader("X-CSRFToken", csrftoken);
    }
}

function save_comment() {
    $("a.comment-action").click(function (event) {
        var sb_id = $(this).data('object_uuid');
        event.preventDefault();
        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                ajax_security(xhr, settings)
            }
        });
        $.ajax({

            xhrFields: {withCredentials: true},
            type: "POST",
            url: "/comments/submit_comment/",
            data: JSON.stringify({
                'content': $('textarea#post_comment_on_' + sb_id).val(),
                'object_uuid': $(this).data('object_uuid'),
                'object_type': $(this).data('object_type'),
                'current_pleb': $(this).data('current_pleb')
            }),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (data) {
            }
        });
    });
}

function show_edit_post() {
    $("a.show_edit_post_class").click(function (event) {
        var sb_id = $(this).data('uuid');
        $('#divid_' + sb_id).fadeToggle();
    });
}

function edit_post() {
    $("a.edit_post-action").click(function (event) {
        event.preventDefault();
        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                ajax_security(xhr, settings)
            }
        });
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "POST",
            url: "/posts/edit_post/",
            data: JSON.stringify({
                'content': $('textarea#' + $(this).data('post_uuid')).val(),
                'current_pleb': $(this).data('pleb'),
                'post_uuid': $(this).data('post_uuid')
            }),
            contentType: "application/json; charset=utf-8",
            dataType: "json"
        });
    });
}

function delete_post() {
    $("a.delete_post-action").click(function (event) {
        event.preventDefault();
        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                ajax_security(xhr, settings)
            }
        });
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "POST",
            url: "/posts/delete_post/",
            data: JSON.stringify({
                'pleb': $(this).data('pleb'),
                'post_uuid': $(this).data('post_uuid')
            }),
            contentType: "application/json; charset=utf-8",
            dataType: "json"
        });
    });
}

function save_post() {
    $("a.post-action").click(function(event){
        console.log("hello");
		event.preventDefault();
		$.ajaxSetup({
		    beforeSend: function (xhr, settings) {
                ajax_security(xhr, settings)
            }
		});
	   	$.ajax({
			xhrFields: {withCredentials: true},
			type: "POST",
			url: "/posts/submit_post/",
			data: JSON.stringify({
			   'content': $('textarea#post_input_id').val(),
               'current_pleb':$(this).data('current_pleb'),
               'wall_pleb':$(this).data('wall_pleb')
			}),
			contentType: "application/json; charset=utf-8",
			dataType: "json",
            onSuccess: function() {

            }
		});
	});
}

function vote_post() {
    $("a.vote-action").click(function (event) {
        event.preventDefault();
        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                ajax_security(xhr, settings)
            }
        });
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "POST",
            url: "/posts/vote_post/",
            data: JSON.stringify({
                'vote_type': $(this).data('vote_type'),
                'pleb': $(this).data('pleb'),
                'post_uuid': $(this).data('post_uuid')
            }),
            contentType: "application/json; charset=utf-8",
            dataType: "json"
        });
    });
}

function delete_comment() {
    $("a.delete_comment-action").click(function (event) {
        event.preventDefault();
        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                ajax_security(xhr, settings)
            }
        });
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "POST",
            url: "/comments/delete_comment/",
            data: JSON.stringify({
                'pleb': $(this).data('pleb'),
                'comment_uuid': $(this).data('comment_uuid')
            }),
            contentType: "application/json; charset=utf-8",
            dataType: "json"
        });
    });
}

function show_edit_comment() {
    $("a.show_edit_comment_class").click(function () {
        var sb_id = $(this).data('comment_uuid');
        $("#comment_divid_" + sb_id).fadeToggle();
    });
}

function edit_comment() {
    $("a.edit_comment-action").click(function (event) {
        event.preventDefault();
        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                ajax_security(xhr, settings)
            }
        });
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "POST",
            url: "/comments/edit_comment/",
            data: JSON.stringify({
                'content': $('textarea#' + $(this).data('comment_uuid')).val(),
                'pleb': $(this).data('pleb'),
                'comment_uuid': $(this).data('comment_uuid')
            }),
            contentType: "application/json; charset=utf-8",
            dataType: "json"
        });
    });
}

function vote_comment() {
    $("a.vote_comment-action").click(function (event) {
        event.preventDefault();
        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                ajax_security(xhr, settings)
            }
        });
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "POST",
            url: "/comments/vote_comment/",
            data: JSON.stringify({
                'vote_type': $(this).data('vote_type'),
                'pleb': $(this).data('pleb'),
                'comment_uuid': $(this).data('comment_uuid')
            }),
            contentType: "application/json; charset=utf-8",
            dataType: "json"
        });
    });
}

function flag_post() {
    $("a.flag_post-action").click(function (event) {
        event.preventDefault();
        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                ajax_security(xhr, settings)
            }
        });
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "POST",
            url: "/posts/flag_post/",
            data: JSON.stringify({
                'flag_reason': $(this).data('flag_reason'),
                'current_user': $(this).data('current_user'),
                'post_uuid': $(this).data('post_uuid')
            }),
            contentType: "application/json; charset=utf-8",
            dataType: "json"
        });
    });
}

function flag_comment() {
    $("a.flag_comment-action").click(function (event) {
        event.preventDefault();
        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                ajax_security(xhr, settings)
            }
        });
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "POST",
            url: "/comments/flag_comment/",
            data: JSON.stringify({
                'flag_reason': $(this).data('flag_reason'),
                'current_user': $(this).data('current_user'),
                'comment_uuid': $(this).data('comment_uuid')
            }),
            contentType: "application/json; charset=utf-8",
            dataType: "json"
        });
    });
}

function flag_object() {
    $("a.flag_object-action").click(function (event) {
        event.preventDefault();
        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                ajax_security(xhr, settings)
            }
        });
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "POST",
            url: "/flag/flag_object_api/",
            data: JSON.stringify({
                'flag_reason': $(this).data('flag_reason'),
                'current_pleb': $(this).data('current_user'),
                'object_uuid': $(this).data('object_uuid'),
                'object_type': $(this).data('object_type')
            }),
            contentType: "application/json; charset=utf-8",
            dataType: "json"
        });
    });
}

function vote_object() {
    $("a.vote_object-action").click(function (event) {
        event.preventDefault();
        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                ajax_security(xhr, settings)
            }
        });
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "POST",
            url: "/vote/vote_object_api/",
            data: JSON.stringify({
                'vote_type': $(this).data('vote_type'),
                'current_pleb': $(this).data('current_pleb'),
                'object_uuid': $(this).data('object_uuid'),
                'object_type': $(this).data('object_type')
            }),
            contentType: "application/json; charset=utf-8",
            dataType: "json"
        });
    });
}

function save_answer() {
    $("a.submit_answer-action").click(function(event){
		event.preventDefault();
		$.ajaxSetup({
		    beforeSend: function(xhr, settings) {
				var csrftoken = $.cookie('csrftoken');
		        if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
		            xhr.setRequestHeader("X-CSRFToken", csrftoken);
		        }
		    }
		});
	   	$.ajax({
			xhrFields: {withCredentials: true},
			type: "POST",
			url: "/answers/submit_answer_api/",
			data: JSON.stringify({
			   'content': $('textarea#answer_content_id').val(),
               'current_pleb': $(this).data('current_pleb'),
               'question_uuid': $(this).data('question_uuid')
			}),
			contentType: "application/json; charset=utf-8",
			dataType: "json",
            success: function (data) {
            }
		});
	});
}

function edit_object() {
    $("a.edit_object-action").click(function (event) {
        event.preventDefault();
        var uuid = $(this).data('object_uuid');
        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                ajax_security(xhr, settings)
            }
        });
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "POST",
            url: "/edit/edit_object_content_api/",
            data: JSON.stringify({
                'content': $('textarea#'+uuid).val(),
                'current_pleb': $(this).data('current_pleb'),
                'object_uuid': uuid,
                'object_type': $(this).data('object_type')
            }),
            contentType: "application/json; charset=utf-8",
            dataType: "json"
        });
    });
}

function edit_question_title() {
    $("a.edit_question_title-action").click(function (event) {
        event.preventDefault();
        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                ajax_security(xhr, settings)
            }
        });
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "POST",
            url: "/edit/edit_object_content_api/",
            data: JSON.stringify({
                'question_title': $(this).val(),
                'current_pleb': $(this).data('pleb'),
                'object_uuid': $(this).data('post_uuid'),
                'object_type': $(this).data('object_type')
            }),
            contentType: "application/json; charset=utf-8",
            dataType: "json"
        });
    });
}

function show_edit_question() {
    $("a.show_edit_question-action").click(function(event){
        var question_uuid = $(this).data('question_uuid');
        $('#edit_question_'+question_uuid).fadeToggle();
    });
}

function show_edit_answer() {
    $("a.show_edit_answer-action").click(function(event){
        var answer_uuid = $(this).data('answer_uuid');
        $('#show_edit_sb_id_'+answer_uuid).fadeToggle();
    });
}

function delete_object() {
    $("a.delete_object-action").click(function (event) {
        event.preventDefault();
        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                ajax_security(xhr, settings)
            }
        });
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "POST",
            url: "/delete/delete_object_api/",
            data: JSON.stringify({
                'current_pleb': $(this).data('current_pleb'),
                'object_uuid': $(this).data('object_uuid'),
                'object_type': $(this).data('object_type')
            }),
            contentType: "application/json; charset=utf-8",
            dataType: "json"
        });
    });
}


function enable_post_functionality() {
    save_answer();
    flag_object();
    vote_object();
    edit_object();
    edit_question_title();
    save_comment();
    delete_comment();
    show_edit_question();
    show_edit_post();
    show_edit_comment();
    show_edit_answer();
    delete_post();
    delete_object();
}

function getUrlParameter(sParam)
{
    var sPageURL = window.location.search.substring(1);
    var sURLVariables = sPageURL.split('&');
    for (var i = 0; i < sURLVariables.length; i++)
    {
        var sParameterName = sURLVariables[i].split('=');
        if (sParameterName[0] == sParam)
        {
            return sParameterName[1];
        }
    }
}