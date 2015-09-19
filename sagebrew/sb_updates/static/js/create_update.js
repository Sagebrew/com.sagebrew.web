/*global $, ajaxSecurity, Bloodhound*/
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

    $("textarea#update_content_id").pagedownBootstrap({
        "sanatize": false,
        'editor_hooks': [
            {
                'event': 'insertImageDialog',
                'callback': function (callback) {
                    setTimeout(function () {
                        $('#fileModal').modal();
                        $("#insert_image_post").click(function (e) {
                            e.preventDefault();
                            $(".modal-footer").spin('small');
                            if ($("#upload_image").val().length > 1) {
                                var formdata = new FormData(),
                                    file = $("#upload_image")[0].files[0];
                                formdata.append("file", file);
                                $.ajax({
                                    xhrFields: {withCredentials: true},
                                    type: "POST",
                                    url: "/v1/upload/",
                                    contentType: false,
                                    processData: false,
                                    dataType: "json",
                                    data: formdata,
                                    success: function (data) {
                                        callback(data.url);
                                        $(".modal-footer").spin(false);
                                        $("#upload_image").val("");
                                        $("#fileModal").modal('hide');
                                        enable_post_functionality();
                                    },
                                    error: function (XMLHttpRequest) {
                                        errorDisplay(XMLHttpRequest);
                                    }
                                });
                            } else {
                                var image = $("#img-url").val();
                                $(".modal-footer").spin(false);
                                callback(image);
                                $("#img-url").val("");
                                $("#fileModal").modal('hide');
                            }
                        });
                    }, 0);
                    return true;
                }
            }
        ]
    });
    $("#submit_update").click(function (event) {
        event.preventDefault();
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
                errorDisplay(XMLHttpRequest);
            }
        });
    });
    $(".cancel_update-action").click(function (event) {
        event.preventDefault();
        window.location.href = "/quests/" + campaignId + "/updates/";
    });
});
