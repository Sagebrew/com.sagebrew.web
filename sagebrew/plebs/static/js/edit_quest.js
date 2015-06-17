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
            url: "/v1/campaigns/" + campaignId,
            data: JSON.stringify({
                "biography": $("#biography_input").val()
            }),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (data) {
                $.notify("Biography successfully updated.", {type: 'success'});
            },
            error: function (XMLHttpRequest, textStatus, errorThrown) {
                errorDisplay(XMLHttpRequest);
            }
        });
    });
    $("#delete_button").click(function (event) {
        event.preventDefault();
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "POST",
            url: "/user/delete_quest/",
            data: JSON.stringify({}),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (data) {
                $.notify(data.detail, {type: 'success'});
            },
            error: function (XMLHttpRequest, textStatus, errorThrown) {
                errorDisplay(XMLHttpRequest);
            }
        });
    });
    $("#rep_auth").click(function (event) {
        event.preventDefault();
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "POST",
            url: "/user/authenticate_representative/",
            data: JSON.stringify({}),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (data) {
                $.notify(data.detail, {type: 'success'});
            },
            error: function (XMLHttpRequest, textStatus, errorThrown) {
                errorDisplay(XMLHttpRequest);
            }
        });
    });
    $("#edit_epic").click(function (event) {
        window.location.href = "/action/" + campaignId + "/edit_epic";
    });
    $("#add_update").click(function (event) {
        window.location.href = "/action/" + campaignId + "/create_update";
    });
});
