$(document).ready(function () {
    $("button.send_friend_request-action").click(function (event) {
        event.preventDefault();
        var send_request = $("button.send_friend_request-action");
        $(send_request).attr("disabled", "disabled");
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
                    $(send_request).hide();
                    $(".delete_friend_request-action").data(
                        'uuid', data['friend_request_id']);
                    $(".delete_friend_request-action").removeAttr("disabled");
                    $(".delete_friend_request-action").show();
                }
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                if(XMLHttpRequest.status === 500){
                    $(send_request).removeAttr("disabled");
                    $("#server_error").show();
                }
            }
        });
    });
});
