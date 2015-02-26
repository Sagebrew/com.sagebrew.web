$(document).ready(function () {
    $("a.vote-action").click(function (event) {
        event.preventDefault();
        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                ajax_security(xhr, settings)
            }
        });
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "POST",
            url: "/posts/vote_post/",
            data: JSON.stringify({
                'vote_type': $(this).data('vote_type'),
                'pleb': $(this).data('pleb'),
                'post_uuid': $(this).data('post_uuid')
            }),
            contentType: "application/json; charset=utf-8",
            dataType: "json"
        });
    });
});
