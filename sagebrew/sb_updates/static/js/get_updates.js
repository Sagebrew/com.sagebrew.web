/*global $, jQuery, ajaxSecurity, errorDisplay*/
$(document).ready(function () {
    var campaignId = $("#campaign_id").data('object_uuid');
    $.ajax({
        xhrFields: {withCredentials: true},
        type: "GET",
        url: "/v1/campaigns/" + campaignId + "/updates/render/?expand=true",
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (data) {
            $("#update-container").append(data.results.html);
            $(".edit-update").click(function (event) {
                event.preventDefault();
                window.location.href = "/updates/" + $(this).data('object_uuid') + "/edit/";
            });
            //$.notify("Updated next goal set!", {type: 'success'});
        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
            errorDisplay(XMLHttpRequest);
        }
    });
});