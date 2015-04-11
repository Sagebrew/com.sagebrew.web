$(document).ready(function(){
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
            type: "PUT",
            url: "/v1/solutions/" + $("#submit_solution").data("object_uuid") + "/",
            data: JSON.stringify({
                'content': $('textarea#wmd-input-0').val()
            }),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function(data){
                window.location.href = data['url'];
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                if(XMLHttpRequest.status === 500){
                    $("#server_error").show();
                }
            }
        });
    });
});