$(document).ready(function () {
    $("a.show_edit_comment_class").click(function () {
        var sb_id = $(this).data('comment_uuid');
        $("#comment_divid_" + sb_id).fadeToggle();
    });

    $("button.edit_comment-action").click(function (event) {
        event.preventDefault();
        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                ajax_security(xhr, settings)
            }
        });
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "POST",
            url: "/comments/edit_comment/",
            data: JSON.stringify({
                'content': $('textarea#' + $(this).data('comment_uuid')).val(),
                'pleb': $(this).data('pleb'),
                'comment_uuid': $(this).data('comment_uuid')
            }),
            contentType: "application/json; charset=utf-8",
            dataType: "json"
        });
    });
});


function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
