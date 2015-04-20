$( document ).ready(function() {
	$(".full_search-action").click(function(event){
        var search_param = ($('#sb_search_input').val());
        window.location.href = "/search/?q=" + search_param +"&page=1&filter=general";
	});
});


function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

