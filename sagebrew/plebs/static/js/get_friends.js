$(document).ready(function(){
    var username = $("#user_info").data("page_user_username");
    var scrolled = false;
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            ajaxSecurity(xhr, settings)
        }
    });
    $.ajax({
        xhrFields: {withCredentials: true},
        type: "GET",
        url: "/v1/profiles/" + username + "/friends/?html=true",
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function(data) {
            $("#friend_wrapper").append(data['results']);
            $("#next_url").data('url', data['next']);
        },
        error: function(XMLHttpRequest, textStatus, errorThrown) {
            if(XMLHttpRequest.status === 500){
                $("#server_error").show();
            }
        }
    });
    $(window).scroll(function() {
        if(scrolled == false) {
            if ($(window).scrollTop() + $(window).height() > ($(document).height() - $(document).height()*.5)) {
                scrolled = true;
                var next = $("#next_url").data('url');
                if (next !== null)
                {
                    $.ajaxSetup({beforeSend: function (xhr, settings) {
                        ajaxSecurity(xhr, settings)
                    }
                    });
                    $.ajax({
                        xhrFields: {withCredentials: true},
                        type: "GET",
                        url: next,
                        contentType: "application/json; charset=utf-8",
                        dataType: "json",
                        success: function (data) {
                            scrolled = false;
                            $("#friend_wrapper").append(data['results']);
                            $("#next_url").data('url', data['next']);
                        },
                        error: function(XMLHttpRequest, textStatus, errorThrown) {
                            if(XMLHttpRequest.status === 500){
                                $("#server_error").show();
                            }
                        }
                    });
                }
            }
        }
    });
});