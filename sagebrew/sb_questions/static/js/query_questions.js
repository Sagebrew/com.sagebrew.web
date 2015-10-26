$(document).ready(function () {
    $(".sb_border_question").append('<div class="loader" id="question-loader"></div>');
    function loadQuestionSummaries(url) {
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "GET",
            url: url,
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (data) {
                $("#question-loader").remove();
                $("#question_wrapper").append(data.results.html);
                if (data.next !== null) {
                    loadQuestionSummaries(data.next);
                }
                enableQuestionSummaryFunctionality(data.results.ids);
            }
        });
    }
    loadQuestionSummaries("/v1/questions/render/?ordering=-created&page_size=5&expand=true&expedite=true");
    $("a.query_questions-action").click(function (event) {
        $(".query_questions-action").each(function (index, value) {
            $(value).removeClass("active");
        });
        $(this).addClass("active");
        event.preventDefault();
        var sortBy = $(this).data('sort_by'),
            taggedAs = $(this).data('tagged_as');
        if (sortBy === undefined) {
            sortBy = "";
        }
        if (taggedAs === undefined) {
            taggedAs = "";
        }
        var questionWrapper = $("#question_wrapper");
        $("#js-no_result").hide();
        questionWrapper.empty();
        questionWrapper.append('<div class="loader" id="question-loader"></div>');
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "GET",
            url: "/v1/questions/render/?page_size=5&expedite=true&expand=true&ordering=" + sortBy + "&tagged_as=" + taggedAs,
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (data) {
                var questionWrapper = $("#question_wrapper");
                $("#question-loader").remove();
                questionWrapper.empty();
                questionWrapper.append(data.results.html);
                if (data.next !== null) {
                    loadQuestionSummaries(data.next);
                }
                if (data.count === 0) {
                    $("#js-no_result").show();
                } else {
                    $("#js-no_result").hide();
                }
                enableQuestionSummaryFunctionality(data.results.ids);
            },
            error: function (XMLHttpRequest) {
                errorDisplay(XMLHttpRequest);
            }
        });
    });
});
