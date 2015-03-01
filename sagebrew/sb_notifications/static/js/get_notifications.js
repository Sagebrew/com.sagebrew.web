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
			   'range_start': 0,
               'range_end':10
			}),
			contentType: "application/json; charset=utf-8",
			dataType: "json",
            success: function (data) {
                var notification_div = $('#notification_wrapper');
                notification_div.append(data['html']);
            }
    });
});
