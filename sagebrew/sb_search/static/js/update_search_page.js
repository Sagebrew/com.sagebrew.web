$( document ).ready(function() {
    var search_param = $('#search_param').data('search_param');
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
            url: "/search/api/q=" + search_param,
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
                        $('#search_result_div').append(data["html"]);
                        $('.questions').remove();
                    }
                });
            });
        }
    });
});



function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}