$(document).ready(function () {
    // TODO do we use this display function? It's defined in sb_utils.js too
    $("a.show_edit_comment_class").click(function () {
        var sb_id = $(this).data('comment_uuid');
        var textarea = $('textarea#' + $(this).data('comment_uuid'));
        console.log(textarea);
        textarea.height( textarea[0].scrollHeight );
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
                'pleb': $(this).data('current_pleb'),
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
