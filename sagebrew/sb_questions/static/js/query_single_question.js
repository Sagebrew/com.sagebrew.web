$( document ).ready(function() {
    event.preventDefault();
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            ajax_security(xhr, settings)
        }
    });
    var timeOutId = 0;
    var ajaxFn = function () {
            $.ajax({
                xhrFields: {withCredentials: true},
                type: "GET",
                url: "/v1/questions/"+$(".div_data_hidden").data('question_uuid')+"/?html=true",
                contentType: "application/json; charset=utf-8",
                dataType: "json",
                success: function (data) {
                    $("#single_question_wrapper").append(data['html']);
                    enable_question_functionality(data["ids"])
                },
                error: function(XMLHttpRequest, textStatus, errorThrown) {
                    timeOutId = setTimeout(ajaxFn, 1000);
                    $("#server_error").show();
                }
            });
    };
    ajaxFn();
});