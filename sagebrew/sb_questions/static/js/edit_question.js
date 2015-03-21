$( document ).ready(function() {
    $("a.show_edit_question-action").click(function(event){
        window.location.href = window.location.href+"edit/";
    });
    $("#sb_comment_link").click(function () {
        $(this).show("#sb_comment_container");
    });
	$("a.edit_question-action").click(function(event){
		event.preventDefault();
		$.ajaxSetup({
		    beforeSend: function (xhr, settings) {
                ajax_security(xhr, settings)
            }
		});
	   	$.ajax({
			xhrFields: {withCredentials: true},
			type: "POST",
			url: "/conversations/edit_question_api/",
			data: JSON.stringify({
               'content': $('textarea#' + $(this).data('question_uuid')).val(),
			   'question_uuid': $(this).data('question_uuid'),
               'current_pleb':$(this).data('current_pleb')
			}),
			contentType: "application/json; charset=utf-8",
			dataType: "json",
            success: function (data) {
                alert(data['detail']);
            }
		});
	});
});
