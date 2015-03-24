$( document ).ready(function() {
    $(".add_policy").click(function (event) {
        event.preventDefault();
        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                ajax_security(xhr, settings)
            }
        });
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "GET",
            url: "/reps/policy/",
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function(data){
                $("#policy_added_form").append(data['rendered']);
                enable_post_functionality();
                $(".add_policy").attr('disabled', 'disabled');
            }
        });
    });
});

$(document).ready(function(){
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
                $(".policy_list").append(data['rendered']);
            }
        });
    });
});