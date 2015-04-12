$( document ).ready(function() {
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
                ajax_security(xhr, settings)
            }
        });
        var timeOutId = 0;
        var questionEditLoad = function () {
            $.ajax({
                xhrFields: {withCredentials: true},
                type: "GET",
                url: "/v1/questions/" + $('.submit_edit-action').data('object_uuid') + "/",
                contentType: "application/json; charset=utf-8",
                dataType: "json",
                success: function (data) {
                    var question_title = $('#title_id');
                    question_title.html("");
                    question_title.val(data['title']);

                    var question_content = $('#wmd-input-0');
                    question_content.html("");
                    question_content.append(data['content']);

                    var question_preview = $("#wmd-preview-0");
                    question_preview.html("");
                    question_preview.append(data['html_content']);
                    checkSolutionCount();
                },
                error: function(XMLHttpRequest, textStatus, errorThrown) {
                    if(XMLHttpRequest.status === 500){
                         timeOutId = setTimeout(ajaxFn, 1000);
                        $("#server_error").show();
                    }
                }
            });
        };
    var checkSolutionCount = function (){
        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                    ajax_security(xhr, settings)
                }
            });
            $.ajax({
                xhrFields: {withCredentials: true},
                type: "GET",
                url: "/v1/questions/" + $('.submit_edit-action').data('object_uuid') + "/solution_count/",
                contentType: "application/json; charset=utf-8",
                dataType: "json",
                success: function (data) {
                    if (data["solution_count"] == 0) {
                        $('.title_input').removeAttr('disabled');

                    } else {
                        $('.title_input').append("<small><em>Cannot Update Title After Solutions Have Been Posed</em></small>")
                    }
                },
                error: function(XMLHttpRequest, textStatus, errorThrown) {
                    if(XMLHttpRequest.status === 500){
                        $("#server_error").show();
                    }
                }
            });
    };
    questionEditLoad();
});