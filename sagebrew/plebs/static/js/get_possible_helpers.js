/*global $, jQuery, ajaxSecurity, errorDisplay*/
function enablePromotion(campaignId) {
    $(".js-add_accountant").click(function (event) {
        var button = $(this);
        event.preventDefault();
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "POST",
            url: "/v1/campaigns/" + campaignId + "/add_accountants/?html=true",
            contentType: "application/json; charset=utf-8",
            data: JSON.stringify({
                "profiles": [button.data('username')]
            }),
            dataType: "json",
            success: function (data) {
                $("#js-sb_friend_" + button.data('username')).remove();
                $("#js-accountant_wrapper").append(data);
                enableAccountantRemoval(campaignId);
            },
            error: function (XMLHttpRequest) {
                errorDisplay(XMLHttpRequest);
            }
        });
    });
    $(".js-add_editor").click(function (event) {
        event.preventDefault();
        var button = $(this);
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "POST",
            url: "/v1/campaigns/" + campaignId + "/add_editors/?html=true",
            contentType: "application/json; charset=utf-8",
            data: JSON.stringify({
                "profiles": [button.data('username')]
            }),
            dataType: "json",
            success: function (data) {
                $("#js-sb_friend_" + button.data('username')).remove();
                $("#js-editor_wrapper").append(data);
                enableEditorRemoval(campaignId);
            },
            error: function (XMLHttpRequest) {
                errorDisplay(XMLHttpRequest);
            }
        });
    });
}

function enableEditorRemoval(campaignId) {
    $(".js-remove_editor").click(function (event) {
        var button = $(this);
        event.preventDefault();
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "POST",
            url: "/v1/campaigns/" + campaignId + "/remove_editors/?html=true",
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            data: JSON.stringify({
                "profiles": [button.data('username')]
            }),
            success: function (data) {
                $("#js-sb_friend_" + button.data('username')).remove();
                $("#js-quest_helper_wrapper").append(data);
                enablePromotion(campaignId);
            },
            error: function (XMLHttpRequest) {
                errorDisplay(XMLHttpRequest);
            }
        });
    });
}

function enableAccountantRemoval(campaignId) {
    $(".js-remove_accountant").click(function (event) {
        var button = $(this);
        event.preventDefault();
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "POST",
            url: "/v1/campaigns/" + campaignId + "/remove_accountants/?html=true",
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            data: JSON.stringify({
                "profiles": [button.data('username')]
            }),
            success: function (data) {
                $("#js-sb_friend_" + button.data('username')).remove();
                $("#js-quest_helper_wrapper").append(data);
                enablePromotion(campaignId);
            },
            error: function (XMLHttpRequest) {
                errorDisplay(XMLHttpRequest);
            }
        });
    });
}

$(document).ready(function () {
    var campaignId = $("#js-campaign_id").data('object_uuid'),
        username = $("#js-campaign_id").data('username');
    $.ajax({
        xhrFields: {withCredentials: true},
        type: "GET",
        url: "/v1/campaigns/" + campaignId + "/possible_helpers/?html=true",
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (data) {
            $("#js-quest_helper_wrapper").append(data);
            enablePromotion(campaignId);
        },
        error: function (XMLHttpRequest) {
            errorDisplay(XMLHttpRequest);
        }
    });
    $.ajax({
        xhrFields: {withCredentials: true},
        type: "GET",
        url: "/v1/campaigns/" + campaignId + "/accountants/?html=true",
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (data) {
            $("#js-accountant_wrapper").append(data);
            enableAccountantRemoval(campaignId);
        },
        error: function (XMLHttpRequest) {
            errorDisplay(XMLHttpRequest);
        }
    });
    $.ajax({
        xhrFields: {withCredentials: true},
        type: "GET",
        url: "/v1/campaigns/" + campaignId + "/editors/?html=true",
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (data) {
            $("#js-editor_wrapper").append(data);
            enableEditorRemoval(campaignId);
        },
        error: function (XMLHttpRequest) {
            errorDisplay(XMLHttpRequest);
        }
    });
});