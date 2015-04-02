$( document ).ready(function() {
    event.preventDefault();
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            ajax_security(xhr, settings)
        }
    });
    $.ajax({
        xhrFields: {withCredentials: true},
        type: "GET",
        url: "/v1/questions/"+$(".div_data_hidden").data('question_uuid')+"/?html=true",
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (data) {
            $("#single_question_wrapper").append(data);
        },
        error: function(XMLHttpRequest, textStatus, errorThrown) {
            if(XMLHttpRequest.status === 500){
                $("#server_error").show();
            }
        }
    });
});