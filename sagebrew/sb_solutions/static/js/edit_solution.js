$( document ).ready(function() {
    $("a.show_edit_solution-action").click(function(event){
        var solution_uuid = $(this).data('solution_uuid');
        $('#show_edit_object_uuid_'+solution_uuid).fadeToggle();
    });

	$("a.edit_solution-action").click(function(event){
		event.preventDefault();
		$.ajaxSetup({
		    beforeSend: function (xhr, settings) {
                ajax_security(xhr, settings)
            }
		});
	   	$.ajax({
			xhrFields: {withCredentials: true},
			type: "POST",
			url: "/solutions/edit_solution_api/",
			data: JSON.stringify({
               'content': $('textarea#' + $(this).data('solution_uuid')).val(),
			   'solution_uuid': $(this).data('solution_uuid'),
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
