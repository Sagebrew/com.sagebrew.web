$( document ).ready(function() {
    var search_results = $('#search_result_div');
    var search_id = $('#search_param');
    var search_param = search_id.data('search_param');
    var search_page = search_id.data('search_page');
    var scrolled = false;
    $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                ajax_security(xhr, settings)
            }
        });
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "GET",
            url: "/search/api/q=" + search_param + '&page=' + search_page,
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (data) {
                if (data['next'] != ""){
                    search_results.append("<div class='load_next_page' style='display: none' data-next='"+data['next']+"'></div>")
                }
                var data_list = data['html'];
                $.each(data_list, function(i, item) {
                    if (data_list[i].type == 'question') {
                        var question_id = data_list[i].question_uuid;
                        $.ajaxSetup({
                            beforeSend: function (xhr, settings) {
                                ajax_security(xhr, settings)
                            }
                        });
                        $.ajax({
                            xhrFields: {withCredentials: true},
                            type: "GET",
                            url: "/questions/search/" + question_id + '/',
                            contentType: "application/json; charset=utf-8",
                            dataType: "json",
                            success: function (data) {
                                search_results.append(data["html"]);
                            }
                        });
                    }
                    if (data_list[i].type == 'pleb'){
                        var pleb_email = data_list[i].pleb_email;
                        $.ajaxSetup({
                            beforeSend: function (xhr, settings) {
                                ajax_security(xhr, settings)
                            }
                        });
                        $.ajax({
                            xhrFields: {withCredentials: true},
                            type: "GET",
                            url: "/user/search/" + pleb_email + '/',
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



