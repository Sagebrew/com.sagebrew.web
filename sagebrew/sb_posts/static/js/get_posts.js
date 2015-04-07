$( document ).ready(function() {
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
                ajax_security(xhr, settings)
            }
    });
    $.ajax({
        xhrFields: {withCredentials: true},
			type: "POST",
			url: "/posts/query_posts/",
			data: JSON.stringify({
               'page_user': $('#user_info').data('page_user_username'),
			   'range_start': 0,
               'range_end':10
			}),
			contentType: "application/json; charset=utf-8",
			dataType: "json",
            success: function (data) {
                var wall_container = $('#wall_app');
                wall_container.append(data['html']);
                enable_single_post_functionality(data['ids'])
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                if(XMLHttpRequest.status === 500){
                    $("#server_error").show();
                }
            }
    });
});
