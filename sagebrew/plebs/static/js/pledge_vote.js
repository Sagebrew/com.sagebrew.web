/*global $, jQuery, ajaxSecurity, errorDisplay*/
$(document).ready(function () {
    $("#create_vote").click(function (event) {
        $(this).attr("disabled", "disabled");
        event.preventDefault();
        var campaignId = $("#submit_goal").data('object_uuid');
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "POST",
            url: "/v1/campaigns/" + campaignId + "/vote/",
            data: JSON.stringify({
                "vote_type": 1
            }),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (data) {
                $("#create_vote").removeAttr("disabled");
                $.notify(data.detail, {type: 'success'});
            },
            error: function (XMLHttpRequest, textStatus, errorThrown) {
                $(this).removeAttr("disabled");
                errorDisplay(XMLHttpRequest);
            }
        });
    });
});
