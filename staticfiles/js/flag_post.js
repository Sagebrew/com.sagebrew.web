$(document).ready(function () {
    $("a.flag_post-action").click(function (event) {
        event.preventDefault();

        $.ajax({
            xhrFields: {withCredentials: true},
            type: "POST",
            url: "/posts/flag_post/",
            data: JSON.stringify({
                'flag_reason': $(this).data('flag_reason'),
                'current_pleb': $(this).data('pleb'),
                'post_uuid': $(this).data('post_uuid')
            }),
            contentType: "application/json; charset=utf-8",
            dataType: "json"
        });
    });
});