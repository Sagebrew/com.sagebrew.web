$(document).ready(function () {
    "use strict";
    function createQuestion() {
        var submitArea = $(".submit_question-action"),
            tags = $('#sb_tag_box').val();
        submitArea.attr("disabled", "disabled");
        if (tags === "") {
            tags = [];
        }

        $.ajax({
            xhrFields: {withCredentials: true},
            type: "POST",
            url: submitArea.data('url'),
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
    }
    $(".submit_question-action").click(function (event) {
        event.preventDefault();
        createQuestion();
    });
    $(".cancel_question-action").click(function () {
        window.location.href = "/conversations/";
    });
    $('#sb_tag_box-tokenfield').keypress(function (e) {
        if (e.which === 10 || e.which === 13) {
            e.preventDefault();
            $(".submit_question-action").removeAttr("disabled");
        }
    });
});