$(document).ready(function(){
    var scrolled = false;
    var question_wrapper = $("#question_wrapper");
    $(window).scroll(function() {
        if(scrolled == false) {
            if ($(window).scrollTop() + $(window).height() > ($(document).height() - $(document).height()*.5)) {
                scrolled = true;
                //TODO implement limit/offset pagination once rest works
                var next_page = $('.load_next_page').data('next');
                $.ajaxSetup({beforeSend: function (xhr, settings) {
                        ajax_security(xhr, settings)
                    }
                });
                $.ajax({
                    xhrFields: {withCredentials: true},
                    type: "GET",
                    url: "/v1/questions/?html=true",
                    contentType: "application/json; charset=utf-8",
                    dataType: "json",
                    success: function (data) {
                        scrolled = false;
                        console.log(data);
                        $(".load_next_page").remove();
                        if (data['next'] != ""){
                            question_wrapper.append("<div class='load_next_page' style='display: none' data-next='"+data['next']+"'></div>")
                        }
                        question_wrapper.append(data);
                    },
                    error: function(XMLHttpRequest, textStatus, errorThrown) {
                        if(XMLHttpRequest.status === 500){
                            $("#server_error").show();
                        }
                    }
                });
            }
        }
    });
});