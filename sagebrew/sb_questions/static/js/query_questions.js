$( document ).ready(function() {
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            ajax_security(xhr, settings)
        }
    });
    $.ajax({
        xhrFields: {withCredentials: true},
        type: "GET",
        url: "/v1/questions/renderer/?limit=5&offset=0&expand=true",
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (data) {
            $("#question_wrapper").append(data['results']["html"]);
            enable_question_functionality([data['results']["ids"]]);
        }
    });
	$("a.query_questions-action").click(function(event){
		event.preventDefault();
		$.ajaxSetup({
		    beforeSend: function (xhr, settings) {
                ajax_security(xhr, settings)
            }
		});
	   	$.ajax({
			xhrFields: {withCredentials: true},
			type: "GET",
			url: "/v1/questions/renderer/?limit=5&offset=0&expand=true&ordering=" + $(this).data('sort_by') + "",
			contentType: "application/json; charset=utf-8",
			dataType: "json",
            success: function (data) {
                $("#question_wrapper").empty();
                $("#question_wrapper").append(data['results']["html"]);
                enable_question_functionality([data['results']["ids"]]);
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                console.log(XMLHttpRequest.responseJSON["detail"]);
            }
		});
	});
});
