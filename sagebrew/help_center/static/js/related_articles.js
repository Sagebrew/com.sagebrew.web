$( document ).ready(function() {
    var current_article = location.pathname;
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
                ajaxSecurity(xhr, settings)
            }
    });
    $.ajax({
        xhrFields: {withCredentials: true},
			type: "GET",
			url: "/help/related_articles/",
			data: {
               'current_article': current_article,
               'category': $('#category').data('category'),
			},
			contentType: "application/json; charset=utf-8",
			dataType: "json",
            success: function (data) {
                var wall_container = $('#related_articles');
                wall_container.append(data['html']);
            }
    });
});