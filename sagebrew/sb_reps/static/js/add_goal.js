$( document ).ready(function() {
    $(".add_goal").click(function (event) {
        event.preventDefault();
        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                ajax_security(xhr, settings)
            }
        });
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "GET",
            url: "/reps/goals/",
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function(data){
                $("#goal_added_form").append(data['rendered']);
                enable_post_functionality();
                $(".add_goal").attr('disabled', 'disabled');
            }
        });
    });
});

$(document).ready(function(){
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
});