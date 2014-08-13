$( document ).ready(function() {
    var search_param = $('#search_param').data('search_param');
    var search_page = $('#search_param').data('search_page');
    var scrolled = false;
    $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                var csrftoken = $.cookie('csrftoken');
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            }
        });
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "GET",
            url: "/search/api/q=" + search_param + '&page=' + search_page,
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (data) {
                $('#search_param').remove();
                $('#search_result_div').append(data["html"]);
                $('.questions').each(function(i) {
                var question_id = $(this).data('question_uuid');
                $.ajaxSetup({
                    beforeSend: function (xhr, settings) {
                        var csrftoken = $.cookie('csrftoken');
                        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                            xhr.setRequestHeader("X-CSRFToken", csrftoken);
                        }
                    }
                });
                $.ajax({
                    xhrFields: {withCredentials: true},
                    type: "GET",
                    url: "/questions/search/" + question_id + '/',
                    contentType: "application/json; charset=utf-8",
                    dataType: "json",
                    success: function (data) {
                        console.log(data['html']);
                        $('#search_result_div').append(data["html"]);
                        $('.questions').remove();
                    }
                });
            });
        }
    });
    $(window).scroll(function() {
        if(scrolled == false) {
            if ($(window).scrollTop() + $(window).height() > ($(document).height() - $(document).height()*.2)) {
                scrolled = true;
                var next_page = $('.load_next_page').data('next');
                $('.load_next_page').remove();
                console.log(next_page);
                $.ajax({
                    xhrFields: {withCredentials: true},
                    type: "GET",
                    url: "/search/api/q=" + search_param + '&page='+next_page,
                    contentType: "application/json; charset=utf-8",
                    dataType: "json",
                    success: function (data) {
                        $('#search_param').remove();
                        console.log(data["html"]);
                        $('#search_result_div').append(data["html"]);
                        $('.questions').each(function (i) {
                            var question_id = $(this).data('question_uuid');
                            $.ajaxSetup({
                                beforeSend: function (xhr, settings) {
                                    var csrftoken = $.cookie('csrftoken');
                                    if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                                        xhr.setRequestHeader("X-CSRFToken", csrftoken);
                                    }
                                }
                            });
                            $.ajax({
                                xhrFields: {withCredentials: true},
                                type: "GET",
                                url: "/questions/search/" + question_id + "/",
                                contentType: "application/json; charset=utf-8",
                                dataType: "json",
                                success: function (data) {
                                    $('#search_result_div').append(data["html"]);
                                    $('.questions').remove();
                                    scrolled = false;
                                }
                            });
                        });
                    }
                });
            }
        }
    });
});



function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}