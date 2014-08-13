$( document ).ready(function() {
	$("a.full_search-action").click(function(event){
        var search_param = $('textarea#search_id').val();
        window.location.href = "https://192.168.56.101/search/q=" + search_param +"&page=1";
        console.log('here');
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
			type: "POST",
			url: "/search/results/q=" + search_param + "&page=1",
			data: JSON.stringify({
               'question_title': $('textarea#question_title_id').val(),
			   'content': $('textarea#question_content_id').val(),
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

