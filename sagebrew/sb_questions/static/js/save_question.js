$(document).ready(function () {
    "use strict";

    $(".submit_question-action").click(function (event) {
        event.preventDefault();
        var submitArea = $(".submit_question-action"),
            tags = $('#sb_tag_box').val();
        submitArea.attr("disabled", "disabled");


        if (tags === "") {
            tags = [];
        }

        $.ajax({
            xhrFields: {withCredentials: true},
            type: "POST",
            url: $(this).data('url'),
            data: JSON.stringify({
                'title': $('input#title_id').val(),
                'content': $('textarea#wmd-input-0').val(),
                'tags': tags
            }),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (data) {
                window.location.href = data.url;
            },
            error: function (XMLHttpRequest) {
                submitArea.removeAttr("disabled");
                errorDisplay(XMLHttpRequest);
            }
        });
    });
    $(".cancel_question-action").click(function () {
        window.location.href = "/conversations/";
    });
});