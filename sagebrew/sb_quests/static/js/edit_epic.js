/*global $, ajaxSecurity, guid, Croppic*/
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