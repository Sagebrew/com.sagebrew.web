$( document ).ready(function() {
	$("a.edit_comment-action").click(function(event){
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
			url: "/comments/edit_comment/",
			data: JSON.stringify({
			   'content':$(this).data('action'),
			   'pleb': $(this).data('pleb'),
               'comment_uuid': $(this).data('comment_uuid')
			}),
			contentType: "application/json; charset=utf-8",
			dataType: "json",
			success: function(data) {
			   alert(data['here']);
			}
		});
	});
});


function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function sameOrigin(url) {
    // test that a given url is a same-origin URL
    // url could be relative or scheme relative or absolute
    var host = document.location.host; // host + port
    var protocol = document.location.protocol;
    var sr_origin = '//' + host;
    var origin = protocol + sr_origin;
    // Allow absolute or scheme relative URLs to same origin
    return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
        (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
        // or any other URL that isn't scheme relative or absolute i.e relative.
        !(/^(\/\/|http:|https:).*/.test(url));
}