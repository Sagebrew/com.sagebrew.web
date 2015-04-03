$( document ).ready(function() {
    $("#search_filter").click(function(e){
        e.preventDefault();
        var search_result_area = $("#search_result_div");
        var search_id = $('#search_param');
        var search_param = search_id.data('search_param');
        var search_page = search_id.data('search_page');
        var filter = $(this).data("filter");
        $.ajaxSetup({
		    beforeSend: function (xhr, settings) {
                ajax_security(xhr, settings)
            }
		});
	   	$.ajax({
			xhrFields: {withCredentials: true},
			type: "GET",
			url: "/search/api/q=" + search_param + "&page=1?filter="+filter,
			contentType: "application/json; charset=utf-8",
			dataType: "json",
            success: function (data) {
                search_result_area.empty();
                console.log(data)
            }
		});
    });
});