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
        var post_id = $(this).data('post_uuid');
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
                'content': $('textarea#post_comment_on_' + post_id).val(),
                'post_uuid': $(this).data('post_uuid'),
                'pleb': $(this).data('pleb')
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
        var post_id = $(this).data('uuid');
        $('#divid_' + post_id).fadeToggle();
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
        var comment_id = $(this).data('comment_uuid');
        $("#comment_divid_" + comment_id).fadeToggle();
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
function enable_post_functionality() {
    flag_post();
    vote_comment();
    vote_post();
    edit_comment();
    save_comment();
    delete_comment();
    show_edit_post();
    edit_post();
    show_edit_comment();
    flag_comment();
    delete_post();
}