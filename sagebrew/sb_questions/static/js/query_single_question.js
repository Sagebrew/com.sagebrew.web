$( document ).ready(function() {
    event.preventDefault();
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            ajax_security(xhr, settings)
        }
    });
    $.ajax({
        xhrFields: {withCredentials: true},
        type: "POST",
        url: "/conversations/query_questions_api/",
        data: JSON.stringify({
           'current_pleb': $(".div_data_hidden").data('current_pleb'),
           'question_uuid': $(".div_data_hidden").data('question_uuid'),
           'sort_by': $(".div_data_hidden").data('sort_by')
        }),
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (data) {
            $("#single_question_wrapper").append(data);
            enable_post_functionality()
        }
    });
	$("a.query_question_detail-action").click(function(event){
		event.preventDefault();
		$.ajaxSetup({
		    beforeSend: function (xhr, settings) {
                ajax_security(xhr, settings)
            }
		});
	   	$.ajax({
			xhrFields: {withCredentials: true},
			type: "POST",
			url: "/conversations/query_questions_api/",
			data: JSON.stringify({
               'question_uuid': $(this).data('question_uuid'),
               'sort_by': $(this).data('sort_by')
			}),
			contentType: "application/json; charset=utf-8",
			dataType: "json",
            success: function (data) {
                alert(data['detail']);
                enable_post_functionality()
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