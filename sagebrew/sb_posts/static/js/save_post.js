$( document ).ready(function() {
    // This function hits the SBPost API and saves off a given post from a user
	$(".post-action").click(function(event){
		event.preventDefault();
		$.ajaxSetup({
		    beforeSend: function (xhr, settings) {
                ajax_security(xhr, settings)
            }
		});
	   	$.ajax({
			xhrFields: {withCredentials: true},
			type: "POST",
			url: "/posts/submit_post/",
			data: JSON.stringify({
			   'content': $('textarea#post_input_id').val(),
               'current_pleb':$(this).data('current_pleb'),
               'wall_pleb':$(this).data('wall_pleb')
			}),
			contentType: "application/json; charset=utf-8",
			dataType: "json",
            success: function(data) {
                $('textarea#post_input_id').val("");
                $("#wall_app").prepend(data['html']);
            }
		});
	});
});
