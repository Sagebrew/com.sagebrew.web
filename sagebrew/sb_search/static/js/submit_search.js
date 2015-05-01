$( document ).ready(function() {
	$(".full_search-action").click(function(event){
        var search_param = ($('#sb_search_input').val());
        window.location.href = "/search/?q=" + search_param + "&page=1&filter=general";
	});
    $("#sb_search_input").keyup(function(e) {
        if(e.which == 10 || e.which == 13) {
            var search_param = ($('#sb_search_input').val());
            window.location.href = "/search/?q=" + search_param + "&page=1&filter=general";
        }
    })
});