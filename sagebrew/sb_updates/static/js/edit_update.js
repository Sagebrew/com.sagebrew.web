/*global $, ajaxSecurity, Bloodhound*/
$(document).ready(function () {
    var campaignId = $(this).data('object_uuid');
    $("#edit-update").click(function (event) {
        event.preventDefault();
        $(this).attr("disabled", "disabled");
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
                window.location.href = $("#edit-update").data('url');
            },
            error: function (XMLHttpRequest) {
                $("#edit-update").removeAttr("disabled");
                errorDisplay(XMLHttpRequest);
            }
        });
    });
});