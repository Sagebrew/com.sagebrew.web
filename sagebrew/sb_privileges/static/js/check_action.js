$(document).ready(function () {
    $('.action').each(function(i,obj){
        event.preventDefault();
        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                ajax_security(xhr, settings)
            }
        });
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "GET",
            url: "/privileges/check/action/",
            data: JSON.stringify({
                'action': $(this).data("action")
            }),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function(data){
                $(this).remove();
                $(data['html_object']).data("url", data['url'])
            }
        });
    });
});