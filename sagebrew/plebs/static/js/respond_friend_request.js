$("#friend_request_div").on("mouseenter", "a", function () {
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
            dataType: "json"
        });
    });
});
