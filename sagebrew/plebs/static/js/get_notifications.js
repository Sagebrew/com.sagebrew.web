$( document ).ready(function() {
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
                ajax_security(xhr, settings)
            }
    });
    $.ajax({
        xhrFields: {withCredentials: true},
			type: "POST",
			url: "/notifications/query_notifications/",
			data: JSON.stringify({
               'email': $('#pleb_info').data('current_user_email'),
			   'range_start': 0,
               'range_end':10
			}),
			contentType: "application/json; charset=utf-8",
			dataType: "json",
            success: function (data) {
                var notification_div = $('#notification_div');
                notification_div.append(data['html']);
            }
    });
});
