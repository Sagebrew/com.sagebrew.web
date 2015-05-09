$(document).ready(function () {
    $(".show_friend_request-action").click(function (event) {
        $("#friend_request_div").fadeToggle();
        $(".respond_friend_request-action").click(function (event) {
            event.preventDefault();
            $.ajax({
                xhrFields: {withCredentials: true},
                type: "POST",
                url: "/relationships/respond_friend_request/",
                data: JSON.stringify({
                    'response': $(this).data('response'),
                    'request_id': $(this).data('request_id')
                }),
                contentType: "application/json; charset=utf-8",
                dataType: "json",
                error: function(XMLHttpRequest, textStatus, errorThrown) {
                    if(XMLHttpRequest.status === 500){
                        $("#server_error").show();
                    }
                }
            });
        });
    });
});