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
            type: "POST",
            url: "/relationships/query_friend_requests/",
            data: JSON.stringify({
                'email': $(this).data('email')
            }),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (data) {
                var container = $("#friend_request_div");
                $.each(data, function (key, value) {
                    container.append("<div>" + value['from_name'] + "</div>");
                    container.append('<button class="btn btn-sm btn-primary respond_friend_request-action" data-response="accept" data-request_id="' + value["request_id"] + '">Accept</button>');
                    container.append('<button class="btn btn-sm btn-primary respond_friend_request-action" data-response="deny" data-request_id="' + value["request_id"] + '">Deny</button>');
                    container.append('<button class="btn btn-sm btn-primary respond_friend_request-action" data-response="block" data-request_id="' + value["request_id"] + '">Block</button>');

                });
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