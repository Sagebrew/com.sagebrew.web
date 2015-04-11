$( document ).ready(function() {
    $(".filter_button").click(function(e){
        e.preventDefault();
        var search_result_area = $("#search_result_div");
        var search_id = $('#search_param');
        var search_param = search_id.data('search_param');
        var search_page = search_id.data('search_page');
        var filter = $(this).data("filter");
        window.location.href = "/search/?q=" + search_param + "&page=1&filter=" + filter
    });
});