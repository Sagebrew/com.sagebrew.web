$( document ).ready(function() {
	$(".submit_answer-action").click(function(event){
		event.preventDefault();
		$.ajaxSetup({
		    beforeSend: function(xhr, settings) {
				var csrftoken = $.cookie('csrftoken');
		        if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
		            xhr.setRequestHeader("X-CSRFToken", csrftoken);
		        }
		    }
		});
	   	$.ajax({
			xhrFields: {withCredentials: true},
			type: "POST",
			url: $(this).data('url'),
			data: JSON.stringify({
			   'content': $('textarea.sb_answer_input_area').val(),
               'current_pleb': $(this).data('current_pleb'),
               'question_uuid': $(this).data('question_uuid')
			}),
			contentType: "application/json; charset=utf-8",
			dataType: "json",
            success: function (data) {
                $("#solution_container").append(data['html']);
            }
		});
	});
});
