$( document ).ready(function() {
    $(".add_bio").click(function (event) {
        event.preventDefault();
        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                ajaxSecurity(xhr, settings)
            }
        });
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "GET",
            url: "/reps/bio/",
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function(data){
                $("#bio_added_form").append(data['rendered']);
                enable_post_functionality();
                $(".add_bio").remove();
            }
        });
    });
});

$(document).ready(function(){
    $(".submit_bio-action").click(function(event){
        event.preventDefault();
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                ajaxSecurity(xhr, settings)
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
});