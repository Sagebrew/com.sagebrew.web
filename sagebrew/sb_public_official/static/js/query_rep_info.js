$(document).ready(function(){
    $.ajax({
        xhrFields: {withCredentials: true},
        type: "POST",
        url: "/reps/get_info/",
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify({
            'rep_id': $("#rep_id").data('rep_id')
        }),
        dataType: "json",
        success: function(data){
            $("#experience_list").append(data['experience_html']);
        }
    });
});