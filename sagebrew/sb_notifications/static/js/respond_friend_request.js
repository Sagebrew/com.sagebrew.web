$( "#friend_request_div" ).delegate("a","mouseenter", function() {
	$("a.respond_friend_request-action").click(function(event){
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
			url: "/notifications/respond_friend_request/",
			data: JSON.stringify({
			   'response': $(this).data('response'),
               'request_id': $(this).data('request_id')
			}),
			contentType: "application/json; charset=utf-8",
			dataType: "json"
		});
	});
});
