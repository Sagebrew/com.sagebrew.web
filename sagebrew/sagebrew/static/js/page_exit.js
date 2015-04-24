$( document ).ready(function() {
    $(window).unload( function() {
        var object_list = [];
        $(".object_uuid").each(function(){
            object_list.push($(this).data('object_uuid'))
        });
        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                ajaxSecurity(xhr, settings)
            }
        });
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "POST",
            async: false,
            url: "/docstore/update_neo_api/",
            data: JSON.stringify({
                'object_uuids': object_list
            }),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                if(XMLHttpRequest.status === 500){
                    $("#server_error").show();
                }
            }
        });
    });
});