$(document).ready(function () {
    $(".show_friend_request-action").click(function (event) {
        $("#friend_request_div").fadeToggle();
        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                ajax_security(xhr, settings)
            }
        });
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "GET",
            url: "/v1/profiles/"+$(this).data("username")+"/friend_requests/?html=true",
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (data) {
                var container = $("#friend_requests");
                container.empty();
                container.append(data);
                respond_friend_request();
            }
        });
        $(".respond_friend_request-action").click(function (event) {
            event.preventDefault();
            $.ajaxSetup({
                beforeSend: function (xhr, settings) {
                ajax_security(xhr, settings)
            }
            });
            $.ajax({
                xhrFields: {withCredentials: true},
                type: "POST",
                url: "/relationships/respond_friend_request/",
                data: JSON.stringify({
                    'response': $(this).data('response'),
                    'request_id': $(this).data('request_id')
                }),
                contentType: "application/json; charset=utf-8",
                dataType: "json"
            });
        });
    });
});