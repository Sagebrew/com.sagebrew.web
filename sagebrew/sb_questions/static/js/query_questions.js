$( document ).ready(function() {
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            ajax_security(xhr, settings)
        }
    });
    $.ajax({
        xhrFields: {withCredentials: true},
        type: "GET",
        url: "/v1/questions/?expand=true&html=true",
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (data) {
            $("#question_wrapper").append(data["html"]);
            enable_question_functionality([data["ids"]]);
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
			url: "/v1/questions/?expand=true&html=true&sort_by=" + $(this).data('sort_by') + "",
			contentType: "application/json; charset=utf-8",
			dataType: "json",
            success: function (data) {
                $("#question_wrapper").empty();
                $("#question_wrapper").append(data["html"]);
                enable_question_functionality([data["ids"]]);
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                console.log(XMLHttpRequest.responseJSON["detail"]);
            }
		});
	});
});
