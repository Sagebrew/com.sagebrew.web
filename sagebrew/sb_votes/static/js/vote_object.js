$(document).ready(function () {
    $(".vote_object-action").click(function (event) {
        console.log($(this).data('current_pleb'));
        event.preventDefault();
        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                ajax_security(xhr, settings)
            }
        });
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "POST",
            url: "/vote/vote_object_api/",
            data: JSON.stringify({
                'vote_type': $(this).data('vote_type'),
                'current_pleb': $(this).data('current_pleb'),
                'object_uuid': $(this).data('object_uuid'),
                'object_type': $(this).data('object_type')
            }),
            contentType: "application/json; charset=utf-8",
            dataType: "json"
        });
    });
});