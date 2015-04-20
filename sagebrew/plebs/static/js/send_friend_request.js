$(document).ready(function () {
    $("button.send_friend_request-action").click(function (event) {
        event.preventDefault();
        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                ajax_security(xhr, settings)
            }
        });
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "POST",
            url: "/relationships/create_friend_request/",
            data: JSON.stringify({
                'from_username': $(this).data('from_username'),
                'to_username': $(this).data('to_username')
            }),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (data) {
                if (data['action'] == true) {
                    $("button.send_friend_request-action").hide();
                    $("button.delete_friend_request-action").show();
                }
            }
        });
    });
});
