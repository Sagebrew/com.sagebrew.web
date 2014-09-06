$(document).ready(function () {
    $("a.show_friend_request-action").click(function (event) {
        $("#friend_request_div").fadeToggle();
        event.preventDefault();
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
                    container.append('<a class="btn btn-sm btn-primary respond_friend_request-action" data-response="accept" data-request_id="' + value["request_id"] + '">Accept</a>');
                    container.append('<a class="btn btn-sm btn-primary respond_friend_request-action" data-response="deny" data-request_id="' + value["request_id"] + '">Deny</a>');
                    container.append('<a class="btn btn-sm btn-primary respond_friend_request-action" data-response="block" data-request_id="' + value["request_id"] + '">Block</a>');

                });
            }
        });
        $("a.respond_friend_request-action").click(function (event) {
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


function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function sameOrigin(url) {
    // test that a given url is a same-origin URL
    // url could be relative or scheme relative or absolute
    var host = document.location.host; // host + port
    var protocol = document.location.protocol;
    var sr_origin = '//' + host;
    var origin = protocol + sr_origin;
    // Allow absolute or scheme relative URLs to same origin
    return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
        (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
        // or any other URL that isn't scheme relative or absolute i.e relative.
        !(/^(\/\/|http:|https:).*/.test(url));
}