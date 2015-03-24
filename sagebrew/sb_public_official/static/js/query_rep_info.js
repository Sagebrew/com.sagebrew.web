$(document).ready(function(){
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            ajax_security(xhr, settings)
        }
    });
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
            $("#policy_list").append(data['policy_html']);
            $("#experience_list").append(data['experience_html']);
            $("#education_list").append(data['education_html'])
        }
    });
});