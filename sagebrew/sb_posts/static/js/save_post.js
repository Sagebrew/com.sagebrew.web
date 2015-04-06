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
			url: "/v1/profiles/" + $('#user_info').data('page_user_username') + "/wall/?html=true",
			data: JSON.stringify({
			   'content': $('textarea#post_input_id').val(),
			}),
			contentType: "application/json; charset=utf-8",
			dataType: "json",
            success: function(data) {
                $('textarea#post_input_id').val("");
                $("#wall_app").prepend(data['html']);
                enable_single_post_functionality(data["object_uuid"]);
            }
		});
	});
});
