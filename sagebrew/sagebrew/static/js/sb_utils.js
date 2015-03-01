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
    $(".comment-action").click(function (event) {
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
                $("sb_comments_container_"+$(this).data('object_uuid')).append(data['html'])
            }
        });
    });
}

function show_edit_post() {
    $("a.show_edit_post_class").click(function (event) {
        var sb_id = $(this).data('uuid');
        $("#sb_content_"+sb_id).hide();
        $('#edit_container_' + sb_id).show();
        var textarea = $('textarea#' + $(this).data('uuid'));
        textarea.height( textarea[0].scrollHeight );
    });
}


function show_edit_comment() {
    $("a.show_edit_comment_class").click(function () {
        var sb_id = $(this).data('comment_uuid');
        $("#sb_content_"+sb_id).hide();
        $('#edit_container_' + sb_id).show();
        var textarea = $('textarea#' + $(this).data('comment_uuid'));
        textarea.height( textarea[0].scrollHeight );
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
    $(".vote_object-action").click(function (event) {
        var id = $(this).parents('div.vote_wrapper').attr('id').split('_')[1];
        var vote_type = $(this).hasClass('vote_up') ? true : false;
        var vote_down = $(this).parents('div.vote_wrapper').find(".vote_down");
        var vote_up = $(this).parents('div.vote_wrapper').find(".vote_up");
        if(vote_down.hasClass('vote_down_active') && vote_type == true){
            vote_down.removeClass('vote_down_active');
            vote_up.addClass('vote_up_active');
        } else if(vote_down.hasClass('vote_down_active') && vote_type === false)  {
            vote_down.removeClass('vote_down_active');
        } else if(vote_up.hasClass('vote_up_active') && vote_type === true)  {
            vote_up.removeClass('vote_up_active');
        } else if(vote_up.hasClass('vote_up_active') && vote_type === false)  {
            vote_down.addClass('vote_down_active');
            vote_up.removeClass('vote_up_active');
        } else {
            if(vote_type === true) {
                $(this).addClass('vote_up_active');
            }
            else {
                $(this).addClass('vote_down_active');
            }
        }

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
                'vote_type': vote_type,
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
    $(".submit_answer-action").click(function(event){
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
			url: $(this).data('url'),
			data: JSON.stringify({
			   'content': $('textarea.sb_answer_input_area').val(),
               'current_pleb': $(this).data('current_pleb'),
               'question_uuid': $(this).data('object_uuid')
			}),
			contentType: "application/json; charset=utf-8",
			dataType: "json",
            success: function (data) {
                $("#solution_container").append(data['html']);
                $('textarea.sb_answer_input_area').val("");
            }
		});
	});
}

function edit_object() {
    $(".edit_object-action").click(function (event) {
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
            dataType: "json",
            success: function(data){
                $(data['html_object']).text(data['content']);
                $("#edit_container_"+uuid).hide();
                $("#sb_content_"+uuid).show();
            }
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
        $('#sb_content_'+question_uuid).hide();
        $("#edit_container_"+question_uuid).show();
        var markdown = $("textarea#"+question_uuid).pagedownBootstrap();
        markdown.attr("id", question_uuid);
    });
}

function show_edit_answer() {
    $("a.show_edit_answer-action").click(function(event){
        var answer_uuid = $(this).data('object_uuid');
        $('#sb_content_'+answer_uuid).hide();
        $('#edit_container_'+answer_uuid).show();
        var markdown = $("textarea#"+answer_uuid).pagedownBootstrap();
        markdown.attr("id", answer_uuid)
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

function submit_bio() {
    $(".submit_bio-action").click(function(event){
        event.preventDefault();
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                ajax_security(xhr, settings)
            }
        });
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "POST",
            url: "/reps/bio/",
            contentType: "application/json; charset=utf-8",
            data: JSON.stringify({
                'rep_id': $("#rep_id").data('rep_id'),
                'bio': $('#id_bio').val()
            }),
            dataType: "json",
            success: function(data){
                $('.add_bio_wrapper').remove();
                $("#bio_wrapper").append(data['rendered']);
            }
        });
    });
}

function submit_goal() {
    $(".submit_goal-action").click(function(event){
        event.preventDefault();
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                ajax_security(xhr, settings)
            }
        });
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "POST",
            url: "/reps/goals/",
            contentType: "application/json; charset=utf-8",
            data: JSON.stringify({
                'rep_id': $("#rep_id").data('rep_id'),
                'initial': $('#id_initial').val(),
                'money_req': $('#id_money_req').val(),
                'vote_req': $("#id_vote_req").val(),
                'description': $('#id_description').val()
            }),
            dataType: "json",
            success: function(data){
                $('.add_goal').removeAttr('disabled');
                $('.add_goal_wrapper').remove();
                $("#goal_list").append(data['rendered']);
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
    submit_bio();
    submit_goal();
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

