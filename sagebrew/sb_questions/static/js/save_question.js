$( document ).ready(function() {
	$(".submit_question-action").click(function(event){
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
               'title': $('input#title_id').val(),
			   'content': $('textarea#wmd-input-0').val(),
               'tags': $('#sb_tag_box').val()
			}),
			contentType: "application/json; charset=utf-8",
			dataType: "json",
            success: function (data) {
                window.location.href = data['url']
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                if(XMLHttpRequest.status === 500){
                    $("#server_error").show();
                }
            }
		});
	});
    $(".cancel_question-action").click(function(event){
		window.location.href = "/conversations/";
	});
});