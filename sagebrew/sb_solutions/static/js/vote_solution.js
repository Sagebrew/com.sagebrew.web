$( document ).ready(function() {
	$("a.vote_solution-action").click(function(event){
		event.preventDefault();
		$.ajaxSetup({
		    beforeSend: function(xhr, settings) {
                ajax_security(xhr, settings)
            }
		});
	   	$.ajax({
			xhrFields: {withCredentials: true},
			type: "POST",
			url: "/solutions/vote_solution_api/",
			data: JSON.stringify({
               'current_pleb': $(this).data('current_pleb'),
               'solution_uuid': $(this).data('solution_uuid'),
               'vote_type': $(this).data('vote_type')
			}),
			contentType: "application/json; charset=utf-8",
			dataType: "json",
            success: function (data) {
                alert(data['detail']);
            }
		});
	});
});
