$( document ).ready(function() {
		$.ajaxSetup({
		    beforeSend: function(xhr, settings) {
				var csrftoken = $.cookie('csrftoken');
		        if (!csrfSafeMethod(settings.type) && !this.crossDomain)  {
		            xhr.setRequestHeader("X-CSRFToken", csrftoken);
		        }
		    }
		});
	   	$.ajax({
            xhrFields: {withCredentials: true},
            type: "GET",
            url: "/search/test/",
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function(data) {
                console.log(data["html"])
            }
        });
	});



function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
