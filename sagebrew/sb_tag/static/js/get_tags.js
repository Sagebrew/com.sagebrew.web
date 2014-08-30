$(document).ready(function() {
    $.ajaxSetup({beforeSend: function (xhr, settings) {
            ajax_security(xhr, settings)
        }
    });
    $.ajax({
        xhrFields: {withCredentials: true},
        type: "GET",
        url: "/get_tags/",
    })
});