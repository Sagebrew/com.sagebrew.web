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


function show_edit_comment() {
    $("a.show_edit_comment_class").click(function () {
        var sb_id = $(this).data('comment_uuid');
        $("#comment_divid_" + sb_id).fadeToggle();
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
        var uuid = $(this).data('object_uuid');
        var upvote_count = $('div.sb_upvote_count'+uuid).text();
        var downvote_count = $('div.sb_downvote_count'+uuid).text();
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
                'object_type': $(this).data('object_type'),
                'downvote_count': downvote_count,
                'upvote_count': upvote_count
            }),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function(data){
                $('div.sb_upvote_count'+uuid).text(data['upvote_value']);
                $('div.sb_downvote_count'+uuid).text(data['downvote_value']);
            }
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
               'question_uuid': $(this).data('object_uuid')
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
                'parent_object': $(this).data('parent_object'),
                'object_uuid': uuid,
                'object_type': $(this).data('object_type'),
                'datetime': $(this).data('datetime')
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
        var question_uuid = $(this).data('object_uuid');
        $('#edit_question_'+question_uuid).fadeToggle();
    });
}

function show_edit_answer() {
    $("a.show_edit_answer-action").click(function(event){
        var answer_uuid = $(this).data('object_uuid');
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

function page_leave_endpoint() {
    $(window).on('unload', function() {
        var object_list = [];
        $(".sb_id").each(function(){
            object_list.push($(this).data('object_uuid'))
        });
        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                ajax_security(xhr, settings)
            }
        });
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "POST",
            async: false,
            url: "/docstore/update_neo_api/",
            data: JSON.stringify({
                'object_uuids': object_list
            }),
            contentType: "application/json; charset=utf-8",
            dataType: "json"
        });
    });
}

function add_new(){
    $('.add_policy').on('click', function(){
            cloneForm('div.policy_table:last', 'form');
    });
}

function add_experience(){
    $(".add_experience").click(function (event) {
        event.preventDefault();
        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                ajax_security(xhr, settings)
            }
        });
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "GET",
            url: "/reps/experience/",
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function(data){
                $("#experience_added_form").append(data['rendered']);
                enable_post_functionality();
                $(".add_experience").attr('disabled', 'disabled');
            }
        });
    });
}

function submit_experience(){
    $(".submit_experience-action").click(function(event){
        event.preventDefault();
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                ajax_security(xhr, settings)
            }
        });
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "POST",
            url: "/reps/experience/",
            contentType: "application/json; charset=utf-8",
            data: JSON.stringify({
                'rep_id': $("#rep_id").data('rep_id'),
                'title': $('#id_title').val(),
                'start_date': $('#id_start_date').val(),
                'end_date': $('#id_end_date').val(),
                'current': $('#id_current').val(),
                'company': $('#id_company').val(),
                'location': $('#id_location').val(),
                'description': $('#id_description').val()
            }),
            dataType: "json",
            success: function(data){
                $('.add_experience').removeAttr('disabled');
                $('.add_experience_wrapper').remove();
                $("#experience_list").append(data['rendered']);
            }
        });
    });
}

function cloneForm(selector, type) {
    var newElement = $(selector).clone(true);
    var total = $('#id_'+type+'_TOTAL_FORMS').val();
    console.log(newElement);
    console.log(total);
    newElement.find(':input').each(function(){
        var name = $(this).attr('name').replace('-' + (total-1) + '-','-'+total+'-');
        var id = 'id_'+name;
        $(this).attr({'name': name, 'id': id}).val('').removeAttr('checked');
    });
    newElement.find('label').each(function() {
        var newFor = $(this).attr('for').replace('-' + (total-1) + '-','-' + total + '-');
        $(this).attr('for', newFor);
    });
    total++;
    $('#id_' + type + '-TOTAL_FORMS').val(total);
    $(selector).after(newElement);
}

function submit_policy() {
    $(".submit_policy-action").click(function(event){
        event.preventDefault();
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                ajax_security(xhr, settings)
            }
        });
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "POST",
            url: "/reps/policy/",
            contentType: "application/json; charset=utf-8",
            data: JSON.stringify({
                'rep_id': $("#rep_id").data('rep_id'),
                'policies': $('#id_policies').val(),
                'description': $('#id_description').val()
            }),
            dataType: "json",
            success: function(data){
                $('.add_policy').removeAttr('disabled');
                $('.add_policy_wrapper').remove();
                $("#policy_list").append(data['rendered']);
            }
        });
    });
}

function submit_education() {
    $(".submit_education-action").click(function(event){
        event.preventDefault();
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                ajax_security(xhr, settings)
            }
        });
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "POST",
            url: "/reps/education/",
            contentType: "application/json; charset=utf-8",
            data: JSON.stringify({
                'rep_id': $("#rep_id").data('rep_id'),
                'start_date': $('#id_start_date').val(),
                'end_date': $('#id_end_date').val(),
                'school': $('#id_school').val(),
                'degree': $('#id_degree').val()
            }),
            dataType: "json",
            success: function(data){
                $('.add_education').removeAttr('disabled');
                $('.add_education_wrapper').remove();
                $("#education_list").append(data['rendered']);
            }
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
    show_edit_question();
    show_edit_post();
    show_edit_comment();
    show_edit_answer();
    delete_object();
    page_leave_endpoint();
    submit_experience();
    submit_policy();
    submit_education();
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

