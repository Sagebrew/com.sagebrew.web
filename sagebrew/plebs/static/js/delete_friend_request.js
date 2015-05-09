$(document).ready(function(){
    $(".delete_friend_request-action").click(function(event){
        event.preventDefault();
        $(".delete_friend_request-action").attr("disabled", "disabled");
        var object_uuid = $(this).data('uuid');
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "DELETE",
            url: "/v1/friend_requests/"+object_uuid+"/",
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (data) {
                $(".delete_friend_request-action").hide();
                $(".send_friend_request-action").show();
                $(".send_friend_request-action").removeAttr("disabled")
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                if(XMLHttpRequest.status === 500){
                    $("#server_error").show();
                }
            }
        });
    })
});
