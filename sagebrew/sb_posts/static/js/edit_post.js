$(document).ready(function () {
    // TODO Do we use this display function? It's displayed in sb_utils.js too
    $("a.show_edit_post_class").click(function (event) {
        var sb_id = $(this).data('uuid');
        var textarea = $('textarea#' + $(this).data('uuid'));
        textarea.height( textarea[0].scrollHeight );
        $('#divid_' + sb_id).fadeToggle();
    });
    $("button.edit_post-action").click(function (event) {
        event.preventDefault();
        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                ajax_security(xhr, settings)
            }
        });
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "POST",
            url: "/posts/edit_post/",
            data: JSON.stringify({
                'content': $('textarea#' + $(this).data('post_uuid')).val(),
                'current_pleb': $(this).data('pleb'),
                'post_uuid': $(this).data('post_uuid')
            }),
            contentType: "application/json; charset=utf-8",
            dataType: "json"
        });
    });
});
