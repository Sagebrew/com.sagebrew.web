$( document ).ready(function() {
    var search_results = $('#search_result_div');
    var search_id = $('#search_param');
    var search_param = search_id.data('search_param');
    var search_page = search_id.data('search_page');
    var filter = getUrlParameter('filter');
    if (filter === 'undefined'){
        filter = "";
    }
    var scrolled = false;
    $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                ajax_security(xhr, settings)
            }
        });
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "GET",
            url: "/search/api/q=" + search_param + '&page=' + search_page+"?filter="+filter,
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (data) {
                if (data['next'] != ""){
                    search_results.append("<div class='load_next_page' style='display: none' data-next='"+data['next']+"'></div>")
                }
                var data_list = data['html'];
                $.each(data_list, function(i, item) {
                    if (data_list[i].type == 'question') {
                        var object_uuid = data_list[i].question_uuid;
                        $.ajaxSetup({
                            beforeSend: function (xhr, settings) {
                                ajax_security(xhr, settings)
                            }
                        });
                        $.ajax({
                            xhrFields: {withCredentials: true},
                            type: "GET",
                            url: "/conversations/search/" + object_uuid + '/',
                            contentType: "application/json; charset=utf-8",
                            dataType: "json",
                            success: function (data) {
                                search_results.append(data["html"]);
                            }
                        });
                    }
                    if (data_list[i].type == 'pleb'){
                        console.log(data_list);
                        var pleb_username = data_list[i].pleb_username;
                        $.ajaxSetup({
                            beforeSend: function (xhr, settings) {
                                ajax_security(xhr, settings)
                            }
                        });
                        $.ajax({
                            xhrFields: {withCredentials: true},
                            type: "GET",
                            url: "/user/search/" + pleb_username + '/',
                            contentType: "application/json; charset=utf-8",
                            dataType: "json",
                            success: function (data) {
                                search_results.append(data["html"]);
                            }
                        });
                    }
                });
            }
        });
    $(window).scroll(function() {
        if(scrolled == false) {
            if ($(window).scrollTop() + $(window).height() > ($(document).height() - $(document).height()*.5)) {
                scrolled = true;
                var next_page = $('.load_next_page').data('next');
                $.ajaxSetup({beforeSend: function (xhr, settings) {
                        ajax_security(xhr, settings)
                    }
                });
                $.ajax({
                    xhrFields: {withCredentials: true},
                    type: "GET",
                    url: "/search/api/q=" + search_param + '&page='+next_page,
                    contentType: "application/json; charset=utf-8",
                    dataType: "json",
                    success: function (data) {
                        scrolled = false;
                        $(".load_next_page").remove();
                        if (data['next'] != ""){
                            search_results.append("<div class='load_next_page' style='display: none' data-next='"+data['next']+"'></div>")
                        }
                        search_results.append(data['html']);
                    }
                });
            }
        }
    });
});

function getUrlParameter(sParam)
{
    var sPageURL = window.location.search.substring(1);
    var sURLVariables = sPageURL.split('&');
    for (var i = 0; i < sURLVariables.length; i++)
    {
        var sParameterName = sURLVariables[i].split('=');
        if (sParameterName[0] == sParam)
        {
            return sParameterName[1];
        }
    }
}


