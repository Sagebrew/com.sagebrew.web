$(document).ready(function() {
    $.ajaxSetup({beforeSend: function (xhr, settings) {
            ajax_security(xhr, settings)
        }
    });
    $.ajax({
        xhrFields: {withCredentials: true},
        type: "GET",
        url: "/tags/get_tags/",
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (data) {
            console.log(data);
            var tags = data['tags'];
            console.log(tags);
            $('#sb_tag_box').select2({
                tags: tags,
                tokenSeparators: [",", " ","'",".","*", "_"]
            });
        }
    })
});