/*global $, jQuery, ajaxSecurity, errorDisplay*/
$(document).ready(function () {
    var campaignId = $("#campaign_id").data('object_uuid');
    $("#show_edit_bio").click(function (event) {
        event.preventDefault();
        $("#bio_edit").toggle();
        $("#bio_wrapper").toggle();
    });
    $("#submit_biography").click(function (event) {
        event.preventDefault();
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "PUT",
            url: "/v1/campaigns/" + campaignId + "/",
            data: JSON.stringify({
                "biography": $("#biography_input").val()
            }),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (data) {
                $.notify("Biography successfully updated.", {type: 'success'});
                $("#bio_edit").toggle();
                $("#bio_wrapper").text(data.biography);
                $("#bio_wrapper").append('<button class="btn btn-primary sb_btn_icon sb_btn_icon_green" id="show_edit_bio"><span class="fa fa-edit"></span></button>');
                $("#biography_input").text(data.biography);
                $("#bio_wrapper").toggle();
                $("#show_edit_bio").click(function (event) {
                    event.preventDefault();
                    $("#bio_edit").toggle();
                    $("#bio_wrapper").toggle();
                });
            },
            error: function (XMLHttpRequest, textStatus, errorThrown) {
                errorDisplay(XMLHttpRequest);
            }
        });
    });
    $("#edit_epic").click(function (event) {
        window.location.href = "/quests/" + campaignId + "/edit_epic/";
    });
    $("#add_update").click(function (event) {
        window.location.href = "/quests/" + campaignId + "/create_update/";
    });
    $("#manage_goals").click(function (event) {
        window.location.href = "/quests/" + campaignId + "/manage_goals/";
    });

});
