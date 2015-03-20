$(document).ready(function(){
    var root = window.location.href.split("solutions/")[0];
    var question_uuid = window.location.href.split("solutions/")[1].split("/")[0];
    $(".edit_solution-action").click(function (event) {
        event.preventDefault();
        var uuid = $(this).data('object_uuid');
        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                ajax_security(xhr, settings)
            }
        });
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "POST",
            url: "/edit/edit_object_content_api/",
            data: JSON.stringify({
                'content': $('textarea#wmd-input-0').val(),
                'parent_object': $(this).data('parent_object'),
                'object_uuid': uuid,
                'object_type': $(this).data('object_type')
            }),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function(data){
                window.location.href = root + "conversations/"+question_uuid;
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                if(XMLHttpRequest.status === 500){
                    $("#server_error").show();
                }
            }
        });
    });
});