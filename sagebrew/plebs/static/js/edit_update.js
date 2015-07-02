/*global $, jQuery, ajaxSecurity, Bloodhound*/
$(document).ready(function () {
    $("#edit-update").click(function (event) {
        event.preventDefault();
        var campaignId = $(this).data('object_uuid');
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "PATCH",
            url: "/v1/updates/" + $("#edit-update").data('object_uuid') + "/",
            contentType: "application/json; charset=utf-8",
            dataTye: "json",
            data: JSON.stringify({
                "content": $("#wmd-input-0").val(),
                "title": $("#title_id").val()
            }),
            success: function (data) {
                window.location.href = "/quests/" + data.campaign + "/updates/";
            },
            error: function (XMLHttpRequest) {
                errorDisplay(XMLHttpRequest);
            }
        });
    });
});