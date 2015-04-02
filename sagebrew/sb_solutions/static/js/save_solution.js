$( document ).ready(function() {
	$(".submit_solution-action").click(function(event){
		event.preventDefault();
		$.ajaxSetup({
		    beforeSend: function(xhr, settings) {
                ajax_security(xhr, settings)
            }
		});
	   	$.ajax({
			xhrFields: {withCredentials: true},
			type: "POST",
			url: $(this).data('url'),
			data: JSON.stringify({
			   'content': $('textarea.sb_solution_input_area').val(),
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
