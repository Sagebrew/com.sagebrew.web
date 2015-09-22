/*global $, errorDisplay*/
$(document).ready(function () {
    "use strict";
    function sendQuestionRequest(url, title, content, tags, submitButton) {
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "POST",
            url: url,
            data: JSON.stringify({
                'title': title,
                'content': content,
                'tags': tags
            }),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (data) {
                window.location.href = data.url;
            },
            error: function (XMLHttpRequest) {
                submitButton.removeAttr("disabled");
                errorDisplay(XMLHttpRequest);
            }
        });
    }
    function createQuestion() {
        var submitArea = $(".submit_question-action"),
            tags = $('#sb_tag_box').val(),
            textArea = $('textarea#wmd-input-0'),
            regExp = /\b((?:https?:(?:|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw))(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’])|(?:[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b(?!@)))/gi,
            regexMatches = textArea.val().match(regExp),
            title = $('input#title_id').val(),
            url = submitArea.data('url'),
            content = textArea.val();
        submitArea.attr("disabled", "disabled");
        if (tags === "") {
            tags = [];
        }
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "GET",
            url: "/v1/me/",
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (data) {
                if (data.privileges.indexOf("comment") > -1) {
                    sendQuestionRequest(url, title, content, tags, submitArea);
                } else if (!regexMatches) {
                    $.notify({message: "Please include at least 1 url linking to information to add context or support to your question!"}, {type: "danger"});
                    submitArea.removeAttr("disabled");
                } else {
                    sendQuestionRequest(url, title, content, tags, submitArea);
                }
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