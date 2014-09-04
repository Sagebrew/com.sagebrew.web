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
               'current_user': $('#pleb_info').data('current_user_email'),
               'email': $('#pleb_info').data('page_user_email'),
			   'range_start': 0,
               'range_end':10
			}),
			contentType: "application/json; charset=utf-8",
			dataType: "json",
            success: function (data) {
                var wall_container = $('.sb_profile_container_wall');
                wall_container.append(data['html']);
                save_comment()
        }
    });
});

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}