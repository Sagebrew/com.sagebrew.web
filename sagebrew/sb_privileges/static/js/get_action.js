$( document ).ready(function() {
    $(".get_action_form").click(function (event) {
        event.preventDefault();

        $.ajax({
            xhrFields: {withCredentials: true},
            type: "GET",
            url: "/privilege/create/action/",
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function(data){
                $("#action_form_wrapper").append(data['html']);
                enable_post_functionality();
                $(".get_action_form").attr('disabled', 'disabled');
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                errorDisplay(XMLHttpRequest);
            }
        });
    });
});