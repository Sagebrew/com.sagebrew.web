$( document ).ready(function() {
	$("a.submit_question-action").click(function(event){
		event.preventDefault();
		$.ajaxSetup({
		    beforeSend: function (xhr, settings) {
                ajax_security(xhr, settings)
            }
		});
	   	$.ajax({
			xhrFields: {withCredentials: true},
			type: "POST",
			url: $(this).data('url'),
			data: JSON.stringify({
               'question_title': $('textarea#question_title_id').val(),
			   'content': $('textarea#wmd-input-0').val(),
               'current_pleb':$(this).data('current_pleb'),
               'tags': $('#sb_tag_box').val()
			}),
			contentType: "application/json; charset=utf-8",
			dataType: "json",
            success: function (data) {
                window.location.href=data['url']
            }
		});
	});
});

