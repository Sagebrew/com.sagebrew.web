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
                'from_pleb': $(this).data('from_pleb'),
                'to_pleb': $(this).data('to_pleb')
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
