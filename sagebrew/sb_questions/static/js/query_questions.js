$(document).ready(function () {
    $(".sb_border_question").spin("small");
    function loadQuestionSummaries(url) {
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "GET",
            url: url,
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (data) {
                $(".sb_border_question").spin(false);
                $("#question_wrapper").append(data.results.html);
                if (data.next !== null) {
                    loadQuestionSummaries(data.next);
                }
                enableQuestionSummaryFunctionality(data.results.ids);
            }
        });
    }
    loadQuestionSummaries("/v1/questions/render/?page_size=5&expand=true&expedite=true");
    $("a.query_questions-action").click(function (event) {
        event.preventDefault();
        var sortBy = $(this).data('sort_by'),
            taggedAs = $(this).data('tagged_as');
        if (sortBy === undefined) {
            sortBy = "";
        }
        if (taggedAs === undefined) {
            taggedAs = "";
        }
        $(".sb_border_question").spin('small');
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "GET",
            url: "/v1/questions/render/?page_size=5&expedite=true&expand=true&ordering=" + sortBy + "&tagged_as=" + taggedAs,
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (data) {
                $(".sb_border_question").spin(false);
                $("#question_wrapper").empty();
                $("#question_wrapper").append(data.results.html);
                if (data.count === 0) {
                    $("#js-no_result").show();
                } else {
                    $("#js-no_result").hide();
                }
                enableQuestionFunctionality([data.results.ids]);
            },
            error: function (XMLHttpRequest) {
                errorDisplay(XMLHttpRequest);
            }
        });
    });
});
