$( document ).ready(function() {
    $("a.show_edit_answer-action").click(function(event){
        var answer_uuid = $(this).data('answer_uuid');
        $('#show_edit_sb_id_'+answer_uuid).fadeToggle();
    });

	$("a.edit_answer-action").click(function(event){
		event.preventDefault();
		$.ajaxSetup({
		    beforeSend: function (xhr, settings) {
                ajax_security(xhr, settings)
            }
		});
	   	$.ajax({
			xhrFields: {withCredentials: true},
			type: "POST",
			url: "/answers/edit_answer_api/",
			data: JSON.stringify({
               'content': $('textarea#' + $(this).data('answer_uuid')).val(),
			   'answer_uuid': $(this).data('answer_uuid'),
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


function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
