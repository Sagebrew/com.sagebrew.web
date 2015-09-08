/*global $, ajaxSecurity, errorDisplay*/
$(document).ready(function () {
    $("#create_vote").click(function (event) {
        $(this).attr("disabled", "disabled");
        event.preventDefault();
        var campaignId = $(this).data('object_uuid');
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
                if (data.detail === true) {
                    $.notify("Successfully Pledged Vote", {type: 'success'});
                    $("#create_vote").text("Unpledge Vote");
                } else {
                    $.notify("Successfully Unpledged Vote", {type: 'success'});
                    $("#create_vote").text("Pledge Vote");
                }
                $("#create_vote").removeAttr("disabled");
            },
            error: function (XMLHttpRequest, textStatus, errorThrown) {
                $(this).removeAttr("disabled");
                errorDisplay(XMLHttpRequest);
            }
        });
    });
});
