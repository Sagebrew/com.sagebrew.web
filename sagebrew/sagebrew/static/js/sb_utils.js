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
        var object_uuid = $(this).data('object_uuid');
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
                'content': $('textarea#post_comment_on_' + object_uuid).val(),
                'object_uuid': $(this).data('object_uuid'),
                'object_type': $(this).data('object_type'),
                'current_pleb': $(this).data('current_pleb')
            }),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (data) {
                var comment_container = $("#sb_comments_container_"+object_uuid);
                comment_container.append(data['html']);
                $('textarea#post_comment_on_' + object_uuid).val("");
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                if(XMLHttpRequest.status === 500){
                    $("#server_error").show();
                }
            }
        });
    });
}

function show_edit_post() {
    $("a.show_edit_post_class").click(function (event) {
        var object_uuid = $(this).data('uuid');
        $("#sb_content_"+object_uuid).hide();
        $('#edit_container_' + object_uuid).show();
        var textarea = $('textarea#' + $(this).data('uuid'));
        textarea.height( textarea[0].scrollHeight );
    });
}


function show_edit_comment() {
    $("a.show_edit_comment_class").click(function () {
        var object_uuid = $(this).data('comment_uuid');
        $("#sb_content_"+object_uuid).hide();
        $('#edit_container_' + object_uuid).show();
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
            dataType: "json",
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                if(XMLHttpRequest.status === 500){
                    $("#server_error").show();
                }
            }
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
                $('div.vote_count'+uuid).text(data['total_value'])
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                if(XMLHttpRequest.status === 500){
                    $("#server_error").show();
                }
            }
        });
    });
}

function save_solution() {
    $(".submit_solution-action").click(function(event){
		event.preventDefault();
		$.ajaxSetup({
		    beforeSend: function(xhr, settings) {
                ajax_security(xhr, settings)
            }
		});
	   	$.ajax({
			xhrFields: {withCredentials: true},
			type: "POST",
			url: $(this).data('url'),
			data: JSON.stringify({
			   'content': $('textarea.sb_solution_input_area').val(),
               'current_pleb': $(this).data('current_pleb'),
               'question_uuid': $(this).data('object_uuid')
			}),
			contentType: "application/json; charset=utf-8",
			dataType: "json",
            success: function (data) {
                $("#solution_container").append(data['html']);
                $('textarea.sb_solution_input_area').val("");
                enable_single_solution_functionality();
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                if(XMLHttpRequest.status === 500){
                    $("#server_error").show();
                }
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
                'created': $(this).data('created')
            }),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function(data){
                $(data['html_object']).text(data['content']);
                $("#edit_container_"+uuid).hide();
                $("#sb_content_"+uuid).show();
                $(".sb_object_dropdown").each(function(i, obj){
                    $(obj).removeAttr("disabled");
                });
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                if(XMLHttpRequest.status === 500){
                    $("#server_error").show();
                }
            }
        });
    });
}

function edit_title() {
    $("a.edit_title-action").click(function (event) {
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
                'title': $(this).val(),
                'current_pleb': $(this).data('pleb'),
                'object_uuid': $(this).data('post_uuid'),
                'object_type': $(this).data('object_type')
            }),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                if(XMLHttpRequest.status === 500){
                    $("#server_error").show();
                }
            }
        });
    });
}

function show_edit_question() {
    $("a.show_edit_question-action").click(function(event){
        event.preventDefault();
        window.location.href = window.location.href+"edit/";
    });
}

function show_edit_solution() {
    $("a.show_edit_solution-action").click(function(event){
        event.preventDefault();
        var root = window.location.href.split("conversations/")[0];
        var question_uuid = window.location.href.split("conversations/")[1].split('/')[0];
        var solution_uuid = $(this).data("object_uuid");
        window.location.href = root+"solutions/"+question_uuid+'/'+solution_uuid+'/edit/'
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
            dataType: "json",
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                if(XMLHttpRequest.status === 500){
                    $("#server_error").show();
                }
            }
        });
    });
}

function page_leave_endpoint() {
    $(window).on('unload', function() {
        var object_list = [];
        $(".object_uuid").each(function(){
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
            dataType: "json",
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                if(XMLHttpRequest.status === 500){
                    $("#server_error").show();
                }
            }
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
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                if(XMLHttpRequest.status === 500){
                    $("#server_error").show();
                }
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
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                if(XMLHttpRequest.status === 500){
                    $("#server_error").show();
                }
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

            },
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                if(XMLHttpRequest.status === 500){
                    $("#server_error").show();
                }
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
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                if(XMLHttpRequest.status === 500){
                    $("#server_error").show();
                }
            }
        });
    });
}

function comment_validator() {
    $("#commentSubmitForm").bootstrapValidator({
        framework: 'bootstrap',
        err: {
            container: '#fname_errors'
        },
        feedbackIcons: {
            valid: 'glyphicon glyphicon-ok',
            validating: 'glyphicon glyphicon-refresh'
        },
        live: 'enabled',
        submitButtons: '.comment-action',
        fields: {
            comment_content: {
                group: 'sb_comment',
                validators: {
                    notEmpty: {
                        message: "Content is required"
                    }
                }
            }
        }
    })
}

function submit_action() {
    $('#submit_action_form').click(function(event){
        event.preventDefault();
        var data = {};
        var form = $('#action_form_id').serializeArray();
        $.each(form, function(){
            if(data[this.name] !== undefined) {
                if (!data[this.name].push) {
                    data[this.name] = [data[this.name]];
                }
                data[this.name].push(this.value || '');
            } else {
                data[this.name] = this.value || '';
            }
        });
        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                ajax_security(xhr, settings)
            }
        });
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "POST",
            url: "/privilege/create/action/",
            data: JSON.stringify(data),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function(data) {
                $(".action_form").remove();
                $(".get_action_form").removeAttr('disabled');
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                if(XMLHttpRequest.status === 500){
                    $("#server_error").show();
                }
            }
        });
    });
}

function submit_requirement() {
    $('#submit_requirement_form').click(function(event){
        event.preventDefault();
        var data = {};
        var form = $('#requirement_form_id').serializeArray();
        $.each(form, function(){
            if(data[this.name] !== undefined) {
                if (!data[this.name].push) {
                    data[this.name] = [data[this.name]];
                }
                data[this.name].push(this.value || '');
            } else {
                data[this.name] = this.value || '';
            }
        });
        console.log(data);
        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                ajax_security(xhr, settings)
            }
        });
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "POST",
            url: "/privilege/create/requirement/",
            data: JSON.stringify(data),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function(data) {
                $(".requirement_form").remove();
                $(".get_requirement_form").removeAttr('disabled');
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                if(XMLHttpRequest.status === 500){
                    $("#server_error").show();
                }
            }
        });
    });
}

function activate_montage(){
    var $container = $('#container').imagesLoaded( function() {
      $container.packery({
          gutter: 0,
          itemSelector: '.post_images',
          transitionDuration: 0,
          columnWidth: ".grid-sizer"
      });
    });
}

function respond_friend_request(){
    $(".respond_friend_request-action").click(function (event) {
        event.preventDefault();
        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                ajax_security(xhr, settings)
            }
        });
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
            success: function(data){
                $("#friend_request_div").fadeToggle();
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                if(XMLHttpRequest.status === 500){
                    $("#server_error").show();
                }
            }
        });
    });
}

function enable_friend_request_functionality() {
    respond_friend_request();
}

function enable_single_post_functionality() {
    flag_object();
    vote_object();
    edit_object();
    save_comment();
    show_edit_post();
}

function enable_single_solution_functionality() {
    flag_object();
    vote_object();
    edit_object();
    save_comment();
    show_edit_solution();
}

function enable_post_functionality() {
    save_solution();
    flag_object();
    vote_object();
    edit_object();
    edit_title();
    save_comment();
    show_edit_question();
    show_edit_post();
    show_edit_comment();
    show_edit_solution();
    delete_object();
    page_leave_endpoint();
    submit_experience();
    submit_bio();
    submit_goal();
    comment_validator();
    submit_action();
    submit_requirement();
    activate_montage();
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

