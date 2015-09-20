/*global $, ajaxSecurity, Bloodhound, errorDisplay*/
$(document).ready(function () {
    /*
    Can manipulate converter hooks by doing the following:
    'converter_hooks': [
            {
                'event': 'plainLinkText',
                'callback': function (url) {
                    return "heello";
            }
        }

        ],
     */
    "use strict";
    var campaignId = $("#campaign-id").data('object_uuid');
    $.ajax({
        xhrFields: {withCredentials: true},
        type: "GET",
        url: "/v1/campaigns/" + campaignId + "/goals/",
        contentType: "application/json; charset=utf-8",
        success: function (data) {
            var titleList = [];
            $.each(data.results, function (index, value) {
                titleList.push({"value": value.title});
            });
            var engine = new Bloodhound({
                local: titleList,
                datumTokenizer: function (d) {
                    return Bloodhound.tokenizers.whitespace(d.value);
                },
                queryTokenizer: Bloodhound.tokenizers.whitespace
            });
            engine.initialize();
            $('#goal-selector').tokenfield({
                limit: 50,
                typeahead: [null, {source: engine.ttAdapter()}],
                delimiter: [",", "'", ".", "*", "_"]
            });
        },
        error: function (XMLHttpRequest) {
            errorDisplay(XMLHttpRequest);
        }
    });

    $("#submit_update").click(function (event) {
        event.preventDefault();
        $(this).attr("disabled", "disabled");
        var campaignId = $(this).data('object_uuid'),
            goals = $("#goal-selector").val().split(", ");
        for(var i = 0; i < goals.length; i++) {
            if(goals[i] === ""){
                goals.splice(i, 1);
            }
        }
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "POST",
            url: "/v1/campaigns/" + campaignId + "/updates/",
            contentType: "application/json; charset=utf-8",
            dataTye: "json",
            data: JSON.stringify({
                "content": $("#wmd-input-0").val(),
                "title": $("#title_id").val(),
                "goals": goals
            }),
            success: function (data) {
                window.location.href = "/quests/" + campaignId + "/updates/";
            },
            error: function (XMLHttpRequest) {
                $("#submit_update").removeAttr("disabled");
                errorDisplay(XMLHttpRequest);
            }
        });
    });
    $(".cancel_update-action").click(function (event) {
        event.preventDefault();
        window.location.href = "/quests/" + campaignId + "/updates/";
    });
});
