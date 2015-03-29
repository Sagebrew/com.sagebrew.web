$( document ).ready(function() {
    event.preventDefault();
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            ajax_security(xhr, settings)
        }
    });
    $.ajax({
        xhrFields: {withCredentials: true},
        type: "POST",
        url: "/conversations/query_questions_api/",
        data: JSON.stringify({
           'current_pleb': $(".div_data_hidden").data('current_pleb'),
           'question_uuid': $(".div_data_hidden").data('question_uuid'),
           'sort_by': $(".div_data_hidden").data('sort_by')
        }),
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (data) {
            $("#single_question_wrapper").append(data);
            enable_post_functionality()
        }
    });
	$("a.query_question_detail-action").click(function(event){
		event.preventDefault();
		$.ajaxSetup({
		    beforeSend: function (xhr, settings) {
                ajax_security(xhr, settings)
            }
		});
	   	$.ajax({
			xhrFields: {withCredentials: true},
			type: "POST",
			url: "/conversations/query_questions_api/",
			data: JSON.stringify({
               'question_uuid': $(this).data('question_uuid'),
               'sort_by': $(this).data('sort_by')
			}),
			contentType: "application/json; charset=utf-8",
			dataType: "json",
            success: function (data) {
                alert(data['detail']);
                enable_post_functionality()
            }
		});
	});
});