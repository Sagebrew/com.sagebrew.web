$( document ).ready(function() {
	$("a.full_search-action").click(function(event){
        var search_param = encodeURIComponent($('textarea#search_id').val());
        // TODO This needs to be changed to a dynamic address somehow or we
        // At least need to make a note to change it before launch
        // Might also cause issues with Circle or Selenium since they probably
        // run at localhost, 127.0.0.1
        window.location.href = "https://192.168.56.101/search/q=" + search_param +"&page=1";
		$.ajaxSetup({
		    beforeSend: function (xhr, settings) {
                ajax_security(xhr, settings)
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
                //alert(data['detail']);
            }
		});
	});
});


function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

