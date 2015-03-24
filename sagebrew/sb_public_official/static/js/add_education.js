$( document ).ready(function() {
    $(".add_education").click(function (event) {
        event.preventDefault();
        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                ajax_security(xhr, settings)
            }
        });
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "GET",
            url: "/reps/education/",
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function(data){
                $("#education_added_form").append(data['rendered']);
                enable_post_functionality();
                $(".add_education").attr('disabled', 'disabled');
            }
        });
    });
});

$(document).ready(function(){
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
});