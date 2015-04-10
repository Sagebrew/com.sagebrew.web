$( document ).ready(function() {
    function loadQuestionSummaries(limit, offset){
        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                ajax_security(xhr, settings)
            }
        });
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "GET",
            url: "/v1/questions/render/?limit="+ limit + "&offset=" + offset + "&expand=true",
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (data) {
                $("#question_wrapper").append(data['results']["html"]);
                var total = limit + offset;
                // TODO Went with this approach as the scrolling approach resulted
                // in the posts getting out of order. It also had some interesting
                // functionality that wasn't intuitive. Hopefully transitioning to
                // a JS Framework allows us to better handle this feature.
                if(total <= data["count"] && total < 150){
                    loadQuestionSummaries(limit, total);
                }
                enable_question_summary_functionality(data['results']["ids"]);
            }
        });
    }
    loadQuestionSummaries(2, 0);
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
			url: "/v1/questions/render/?limit=5&offset=0&expand=true&ordering=" + $(this).data('sort_by') + "",
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
