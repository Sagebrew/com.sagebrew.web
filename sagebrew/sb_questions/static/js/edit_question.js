$( document ).ready(function() {
	$(".submit_edit-action").click(function(event){
		event.preventDefault();
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
                    var data_dict = {};
                    if (data["solution_count"] == 0) {
                        data_dict = {
                            'content': $('textarea#wmd-input-0').val(),
                            'title': $('input#title_id').val()
                        };
                    } else {
                        data_dict = {
                            'content': $('textarea#wmd-input-0').val()
                        };
                    }
                    $.ajaxSetup({
                        beforeSend: function (xhr, settings) {
                            ajax_security(xhr, settings)
                        }
                    });
                    $.ajax({
                        xhrFields: {withCredentials: true},
                        type: "PATCH",
                        url: "/v1/questions/" + $('.submit_edit-action').data('object_uuid') + "/",
                        data: JSON.stringify(data_dict),
                        contentType: "application/json; charset=utf-8",
                        dataType: "json",
                        success: function (data) {
                            window.location.href = data['url'];
                        },
                        error: function(XMLHttpRequest, textStatus, errorThrown) {
                            if(XMLHttpRequest.status === 500){
                                $("#server_error").show();
                            }
                        }
                    });
                },
                error: function(XMLHttpRequest, textStatus, errorThrown) {
                    if(XMLHttpRequest.status === 500){
                        $("#server_error").show();
                    }
                }
            });
        });
    $(".cancel_edit_solution-action").click(function(event){
		window.location.href = "/conversations/";
	});
});
