var request = require('api').request,
    helpers = require('common/helpers'),
    convoTopicsTemplate = require('common/templates/select_all.hbs');

export function loadInterests() {
    var $selectAllList = $('#js-option-list');
    helpers.selectAllFields('#select_all_checkboxes');

    $("body").tooltip({ selector: '[data-toggle=tooltip]' });

    $(".tooltip").addClass(function () {
        if ($(this).prev().attr("data-tooltip-style")) {
            return "tooltip-" + $(this).prev().attr("data-tooltip-style");
        }
    });
    request.optionsMethod({url:"/v1/me/add_topics_of_interest/"})
        .done(function (data) {
            document.getElementById("select-loader").remove();
            $selectAllList.append(convoTopicsTemplate({
                options: data.actions.POST.interests.choices,
                select_all_statement: "I like a bit of everything"}));
            helpers.selectAllFields('#js-select-all');
        });
}

