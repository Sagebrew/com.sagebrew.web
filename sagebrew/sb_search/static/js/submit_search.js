$( document ).ready(function() {
	$(".full_search-action").click(function(event){
        var search_param = ($('#sb_search_input').val());
        window.location.href = "/search/" + search_param +"/1/general/";
	});
});


function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

