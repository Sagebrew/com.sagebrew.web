/*global $, jQuery, ajaxSecurity, guid, Croppic*/
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
    $("textarea#epic_content_id").pagedownBootstrap({
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
    $("#submit_epic").click(function (event) {
        event.preventDefault();
        var campaignId = $(this).data('object_uuid');
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "PUT",
            url: "/v1/campaigns/" + campaignId + "/",
            contentType: "application/json; charset=utf-8",
            dataTye: "json",
            data: JSON.stringify({
                "epic": $("#wmd-input-0").val()
            }),
            success: function (data) {
                window.location.href = data.url;
            },
            error: function (XMLHttpRequest) {
                errorDisplay(XMLHttpRequest);
            }
        });
    });
    $(".cancel_edit_epic-action").click(function (event) {
        event.preventDefault();
        var campaignId = $("#submit_epic").data('object_uuid');
        window.location.href = "/quests/" + campaignId + "/";
    });
});