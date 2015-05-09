$(document).ready(function () {
    $("a.show_edit_comment_class").click(function (event) {
        var object_uuid = $(this).data('comment_uuid');
        $("#comment_divid_" + object_uuid).fadeToggle();
    });

    $("a.edit_comment-action").click(function (event) {
        event.preventDefault();

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
            dataType: "json",
            success: function (data) {
                alert(data['here']);
            }
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