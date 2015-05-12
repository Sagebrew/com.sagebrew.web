/**
 * csrftoken support for django
 */
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?

            if (cookie.substring(0, name.length + 1) == (name + '=')) {
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
     beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        }
     }
});

function save_comment(comment_area, url, object_uuid) {
    $(comment_area).click(function (event) {
        $(comment_area).attr("disabled", "disabled");
        event.preventDefault();
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "POST",
            url: url + "?html=true&expedite=true",
            data: JSON.stringify({
                'content': $('textarea#post_comment_on_' + object_uuid).val(),
                'object_uuid': $(this).data('object_uuid')
            }),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (data) {
                var comment_container = $("#sb_comments_container_" + object_uuid);
                comment_container.prepend(data['html']);
                $('textarea#post_comment_on_' + object_uuid).val("");
                enable_comment_functionality(data["ids"]);
                $(comment_area).removeAttr("disabled");
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                $(comment_area).removeAttr("disabled");
                if(XMLHttpRequest.status === 500){
                    $("#server_error").show();
                }
            }
        });
    });
}


function save_comments(populated_ids, url){
    if(typeof populated_ids !== 'undefined' && populated_ids.length > 0){
        for (i = 0; i < populated_ids.length; i++) {
            save_comment(".comment_" + populated_ids[i],
                url + populated_ids[i] + "/comments/", populated_ids[i]);
        }
    }
}


function show_edit_post(edit_area) {
    $(edit_area).click(function (event) {
        var object_uuid = $(this).data('uuid');
        $("#sb_content_" + object_uuid).hide();
        $('#edit_container_' + object_uuid).show();
        var textarea = $('textarea#' + $(this).data('uuid'));
        textarea.height( textarea[0].scrollHeight );
    });
}

function show_edit_posts(populated_ids) {
    if(typeof populated_ids !== 'undefined' && populated_ids.length > 0){
        for (i = 0; i < populated_ids.length; i++) {
            show_edit_post("a.show_edit_post_" + populated_ids[i]);
        }
    } else {
        show_edit_post("a.show_edit_post_class");
    }
}


function show_edit_comment() {
    $("a.show_edit_comment_class").click(function () {
        var object_uuid = $(this).data('comment_uuid');
        $("#sb_content_" + object_uuid).hide();
        $('#edit_container_' + object_uuid).show();
        var textarea = $('textarea#' + $(this).data('comment_uuid'));
        textarea.height( textarea[0].scrollHeight );
    });
}


function populate_comment(object_uuid, resource){
    $.ajax({
        xhrFields: {withCredentials: true},
        type: "GET",
        // TODO probably want to make a /v1/content/ endpoint so that it's more
        // explanitory that comments can be on any piece of content.
        // Then use /posts/questions/solutions where needed
        url: "/v1/" + resource + "/" + object_uuid + "/comments/render/?expedite=true&expand=true&html=true&page_size=3",
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (data) {
            var comment_container = $('#sb_comments_container_' + object_uuid);
            comment_container.append(data['results']['html']);
            if(data['count'] > 3){
                // TODO this may break in IE
                comment_container.append(
                    '<div class="row">' +
                        '<div class="col-lg-5 col-lg-offset-1">' +
                             '<a href="javascript:;" class="additional_comments" id="additional_comments_' + object_uuid + '">More Comments ...</a>' +
                        '</div>' +
                    '</div>');
                $('#additional_comments_' + object_uuid).click(function() {
                    $.ajax({
                        xhrFields: {withCredentials: true},
                        type: "GET",
                        url: "/v1/" + resource + "/" + object_uuid + "/comments/render/?expand=true&html=true&page_size=3&page=2",
                        contentType: "application/json; charset=utf-8",
                        dataType: "json",
                        success: function (data) {
                            var comment_container = $('#sb_comments_container_' + object_uuid);
                            $('#additional_comments_' + object_uuid).remove();
                            comment_container.append(data['results']['html']);
                            if (data["next"] !== null) {
                                queryComments(data["next"], object_uuid)
                            }
                            enable_comment_functionality(data['results']['ids']);
                        },
                        error: function(XMLHttpRequest, textStatus, errorThrown) {
                            if(XMLHttpRequest.status === 500){
                                $("#server_error").show();
                            }
                        }
                    });
                });

            }
            enable_comment_functionality(data['results']['ids']);
        },
        error: function(XMLHttpRequest, textStatus, errorThrown) {
            if(XMLHttpRequest.status === 500){
                $("#server_error").show();
            }
        }
    });
}

function queryComments(url, object_uuid){
    $.ajax({
        xhrFields: {withCredentials: true},
        type: "GET",
        url: url,
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (data) {
            if (data["next"] !== null) {
                queryComments(data["next"], object_uuid)
            }
            var comment_container = $('#sb_comments_container_' + object_uuid);
            comment_container.append(data['results']['html']);
            enable_comment_functionality(data['results']['ids']);
        },
        error: function(XMLHttpRequest, textStatus, errorThrown) {
            if(XMLHttpRequest.status === 500){
                $("#server_error").show();
            }
        }
    });
}

function populate_comments(object_uuids, resource){
    if(typeof object_uuids !== 'undefined' && object_uuids.length > 0){
        for (i = 0; i < object_uuids.length; i++) {
            populate_comment(object_uuids[i], resource);
        }
    }
}


function readyFlag(flag_object){
    $(flag_object).tooltip()
}

function readyVote(vote_object){
    $(vote_object).tooltip()
}

function readyVotes(object_uuids){
    if(typeof object_uuids !== 'undefined' && object_uuids.length > 0){
        for (i = 0; i < object_uuids.length; i++) {
            readyVote("#upvote_" + object_uuids[i]);
            readyVote("#downvote_" + object_uuids[i]);
        }
    }
}

function readyFlags(object_uuids){
    if(typeof object_uuids !== 'undefined' && object_uuids.length > 0){
        for (i = 0; i < object_uuids.length; i++) {
            readyFlag("#flag_" + object_uuids[i]);
        }
    }
}


function loadPosts(url){
    $("#wall_app").spin({lines: 8, length: 4, width: 3, radius: 5});
    $.ajax({
        xhrFields: {withCredentials: true},
        type: "GET",
        url: url,
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (data) {
            var wall_container = $('#wall_app');
            if (data.count == 0) {
                wall_container.append('<div id="js-wall_temp_message"><h3>Add a Spark :)</h3></div>');
            } else{
                wall_container.append(data.results.html);
                // TODO Went with this approach as the scrolling approach resulted
                // in the posts getting out of order. It also had some interesting
                // functionality that wasn't intuitive. Hopefully transitioning to
                // a JS Framework allows us to better handle this feature.
                if (data.next !== null) {
                    loadPosts(data.next);
                }
                enable_single_post_functionality(data.results.ids);
                // TODO This can probably be changed to grab the href and append
                // `comments/` to the end of it.
                populate_comments(data.results.ids, "posts");
            }
            wall_container.spin(false);
        },
        error: function(XMLHttpRequest, textStatus, errorThrown) {
            if(XMLHttpRequest.status === 500){
                $("#server_error").show();
            }
        }
    });
}


function loadQuestion(){
    var timeOutId = 0;
    var ajaxFn = function () {
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "GET",
            url: "/v1/questions/" + $('.div_data_hidden').data('question_uuid') + "/?html=true&expand=true",
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (data) {
                var question_container = $('#single_question_wrapper');
                question_container.append(data['html']);
                loadSolutionCount();
                enable_question_functionality(data['ids']);
                populate_comments(data['ids'], "questions");
                loadSolutions("/v1/questions/" + $('.div_data_hidden').data('question_uuid') + "/solutions/render/?page_size=2&expand=true");
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                if(XMLHttpRequest.status === 500){
                     timeOutId = setTimeout(ajaxFn, 1000);
                    $("#server_error").show();
                }
            }
        });
    };
    ajaxFn();
}

function loadSolutionCount(){
    $.ajax({
        xhrFields: {withCredentials: true},
        type: "GET",
        url: "/v1/questions/" + $('.div_data_hidden').data('question_uuid') + "/solution_count/",
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (data) {
            $('#solution_count').html("");
            $('#solution_count').append(data['solution_count']);
            if(data["solution_count"] != '1'){
                $('#solution_plural').append('s');
            }
        },
        error: function(XMLHttpRequest, textStatus, errorThrown) {
            if(XMLHttpRequest.status === 500){
                $("#server_error").show();
            }
        }
    });
}



function loadSolutions(url){
    $.ajax({
        xhrFields: {withCredentials: true},
        type: "GET",
        url: url,
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (data) {
            var solution_container = $('#solution_container');
            solution_container.append(data['results']['html']);
            // TODO Went with this approach as the scrolling approach resulted
            // in the posts getting out of order. It also had some interesting
            // functionality that wasn't intuitive. Hopefully transitioning to
            // a JS Framework allows us to better handle this feature.
            if (data["next"] !== null) {
                loadSolutions(data["next"]);
            }
            enable_solution_functionality(data['results']['ids']);
            // TODO This can probably be changed to grab the href and append
            // `comments/` to the end of it.
            populate_comments(data['results']['ids'], "solutions");
        },
        error: function(XMLHttpRequest, textStatus, errorThrown) {
            if(XMLHttpRequest.status === 500){
                $("#server_error").show();
            }
        }
    });
}


function vote_object(vote_area, resource){
    $(vote_area).click(function (event) {
        var object_uuid = $(this).data('object_uuid');
        var id = $(this).parents('div.vote_wrapper').attr('id').split('_')[1];
        var vote_type = $(this).hasClass('vote_up') ? true : false;
        var vote_down = $(this).parents('div.vote_wrapper').find(".vote_down");
        var vote_up = $(this).parents('div.vote_wrapper').find(".vote_up");
        if (vote_type === true){
            vote_up.attr("disabled", "disabled");
        } else if(vote_type === false){
            vote_down.attr("disabled", "disabled");
        }
        var upvote_count = parseInt($('#vote_count_' + object_uuid).text());
        if(vote_down.hasClass('vote_down_active') && vote_type == true){
            vote_down.removeClass('vote_down_active');
            vote_up.addClass('vote_up_active');
            upvote_count += 2;
        } else if(vote_down.hasClass('vote_down_active') && vote_type === false)  {
            vote_down.removeClass('vote_down_active');
            upvote_count += 1;
        } else if(vote_up.hasClass('vote_up_active') && vote_type === true)  {
            vote_up.removeClass('vote_up_active');
            upvote_count -= 1;
        } else if(vote_up.hasClass('vote_up_active') && vote_type === false)  {
            vote_down.addClass('vote_down_active');
            vote_up.removeClass('vote_up_active');
            upvote_count -= 2;
        } else {
            if(vote_type === true) {
                $(this).addClass('vote_up_active');
                upvote_count += 1;
            }
            else {
                $(this).addClass('vote_down_active');
                upvote_count -= 1;
            }
        }

        event.preventDefault();
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "POST",
            url: "/v1/" + resource + "/" + object_uuid + "/votes/?expedite=true",
            data: JSON.stringify({
                'vote_type': vote_type
            }),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function(data){
                $('#vote_count_' + object_uuid).text(upvote_count);
                $(vote_area).removeAttr("disabled");
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                $(vote_area).removeAttr("disabled");
                if(XMLHttpRequest.status === 500){
                    $("#server_error").show();
                    //alert(textStatus);
                }
            }
        });
    });
}

function vote_objects(populated_ids, resource) {
    if(typeof populated_ids !== 'undefined' && populated_ids.length > 0){
        for (i = 0; i < populated_ids.length; i++) {
            vote_object(".vote_" + populated_ids[i], resource);
        }
    }
}

function save_solution() {
    $(".submit_solution-action").click(function(event){
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
                $("#solution_container").append(data['html']);
                $('textarea.sb_solution_input_area').val("");
                var solution_count_text = $("#solution_count").text();
                if(solution_count_text != "--") {
                    var solution_count = parseInt(solution_count_text) + 1;
                    $("#solution_count").text(solution_count.toString());
                }
                $('#wmd-preview-1').html("");
                $("#submit_solution").removeAttr("disabled");
                enable_solution_functionality(data["ids"]);
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                $("#submit_solution").removeAttr("disabled");
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
        window.location.href = "/conversations/questions/" + $(this).data('object_uuid') + "/edit/";
    });
}

function show_edit_solution() {
    $("a.show_edit_solution-action").click(function(event){
        event.preventDefault();
        var solution_uuid = $(this).data("object_uuid");
        window.location.href = "/conversations/solutions/" + solution_uuid + '/edit/'
    });
}


function edit_object(edit_area, url, object_uuid, data_area) {
    $(edit_area).click(function (event) {
        event.preventDefault();
        var edit_button = ".edit_" + object_uuid;
        $(edit_button).attr("disabled", "disabled");
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "PUT",
            url: url,
            contentType: "application/json; charset=utf-8",
            data: JSON.stringify({
                'content': $(data_area).val()
            }),
            dataType: "json",
            success: function(data){
                $(edit_button).removeAttr("disabled");
                var content_container = $("#sb_content_" + object_uuid);
                content_container.text(data['content']);
                $("#edit_container_" + object_uuid).hide();
                content_container.show();
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                if(XMLHttpRequest.status === 500){
                    $(edit_button).removeAttr("disabled");
                    $("#server_error").show();
                }
            }
        });
    });
}


function edit_objects(url, populated_ids){
    if(typeof populated_ids !== 'undefined' && populated_ids.length > 0){
        for (i = 0; i < populated_ids.length; i++) {
            // Eventually we should just be able to get the href
            edit_object(".edit_" + populated_ids[i],
                url + populated_ids[i] + "/", populated_ids[i], "textarea#" + populated_ids[i]);
        }
    }
}


function delete_objects(url, populated_ids){
    if(typeof populated_ids !== 'undefined' && populated_ids.length > 0){
        for (i = 0; i < populated_ids.length; i++) {
            delete_object(".delete_" + populated_ids[i],
                url + populated_ids[i] + "/", populated_ids[i]);
        }
    }
}

function delete_object(delete_area, url, object_uuid) {
    $(delete_area).click(function (event) {
        event.preventDefault();
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "DELETE",
            url: url,
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function(data){
                $(".block_" + object_uuid).remove();
                $('textarea.sb_solution_input_area').val("");
                var solution_count_text = $("#solution_count").text();
                if(solution_count_text != "--") {
                    var solution_count = parseInt(solution_count_text) - 1;
                    $("#solution_count").text(solution_count.toString());
                }
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


function enable_object_functionality(populated_ids) {
    readyFlags(populated_ids);
    readyVotes(populated_ids)
}


function enable_friend_request_functionality() {
    respond_friend_request();
}

function enable_comment_functionality(populated_ids){
    enable_object_functionality(populated_ids);
    show_edit_comment(populated_ids);
    comment_validator();
    vote_objects(populated_ids, "comments");
    edit_objects("/v1/comments/", populated_ids);
    delete_objects("/v1/comments/", populated_ids);
}

function enable_question_summary_functionality(populated_ids) {
    vote_objects(populated_ids, "questions");
    readyVotes(populated_ids)
}

function enable_question_functionality(populated_ids) {
    enable_object_functionality(populated_ids);
    save_comments(populated_ids, "/v1/questions/");
    show_edit_question(populated_ids);
    save_solution(populated_ids);
    vote_objects(populated_ids, "questions");
    delete_objects("/v1/questions/", populated_ids);
}

function enable_single_post_functionality(populated_ids) {
    enable_object_functionality(populated_ids);
    save_comments(populated_ids, '/v1/posts/');
    show_edit_posts(populated_ids);
    vote_objects(populated_ids, "posts");
    edit_objects("/v1/posts/", populated_ids);
    delete_objects("/v1/posts/", populated_ids);
}

function enable_solution_functionality(populated_ids) {
    enable_object_functionality(populated_ids);
    save_comments(populated_ids, '/v1/solutions/');
    vote_objects(populated_ids, "solutions");
    show_edit_solution(populated_ids);
    delete_objects("/v1/solutions/", populated_ids);
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

