$(document).ready(function () {
    $("a.flag_comment-action").click(function (event) {
        event.preventDefault();
        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                ajax_security(xhr, settings)
            }
        });
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "POST",
            url: "/comments/flag_comment/",
            data: JSON.stringify({
                'flag_reason': $('textarea#' + $(this).data('comment_uuid')).val(),
                'current_user': $(this).data('pleb'),
                'comment_uuid': $(this).data('comment_uuid')
            }),
            contentType: "application/json; charset=utf-8",
            dataType: "json"
        });
    });
});