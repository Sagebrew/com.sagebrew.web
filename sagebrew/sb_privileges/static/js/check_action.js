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
            url: "/privilege/check/action/",//?action="+$(this).data("action"),
            data: {
                'action': $(this).data("action")
            },
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function(data){
                $(this).remove();
                var test_object = $(data['html_object']);
                console.log(test_object);
                $(data['html_object']).data("url", data['url']);
                $(data['html_object']).removeAttr('disabled')
            }
        });
    });
});