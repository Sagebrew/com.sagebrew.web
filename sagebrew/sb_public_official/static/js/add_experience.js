$( document ).ready(function() {
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
});

$(document).ready(function(){
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
});