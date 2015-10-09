/*global $, ajaxSecurity, errorDisplay*/
function enablePromotion(campaignId, ids) {
    $.each(ids, function (index, value) {
        $(".js-add_accountant_" + value).click(function (event) {
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
                    $("#js-accountant_wrapper").append(data.html);
                    enableAccountantRemoval(campaignId, data.ids);
                },
                error: function (XMLHttpRequest) {
                    errorDisplay(XMLHttpRequest);
                }
            });
        });
        $(".js-add_editor_" + value).click(function (event) {
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
                    $("#js-editor_wrapper").append(data.html);
                    enableEditorRemoval(campaignId, data.ids);
                },
                error: function (XMLHttpRequest) {
                    errorDisplay(XMLHttpRequest);
                }
            });
        });
    });
}

function enableEditorRemoval(campaignId, ids) {
    $.each(ids, function (index, value) {
        $(".js-remove_editor_" + value).click(function (event) {
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
                    $("#js-quest_helper_wrapper").append(data.html);
                    enablePromotion(campaignId, data.ids);
                },
                error: function (XMLHttpRequest) {
                    errorDisplay(XMLHttpRequest);
                }
            });
        });
    });
}

function enableAccountantRemoval(campaignId, ids) {
    $.each(ids, function (index, value) {
        $(".js-remove_accountant_" + value).click(function (event) {
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
                    $("#js-quest_helper_wrapper").append(data.html);
                    enablePromotion(campaignId, data.ids);
                },
                error: function (XMLHttpRequest) {
                    errorDisplay(XMLHttpRequest);
                }
            });
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
            $("#js-quest_helper_wrapper").append(data.html);
            enablePromotion(campaignId, data.ids);
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
            $("#js-accountant_wrapper").append(data.html);
            enableAccountantRemoval(campaignId, data.ids);
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
            $("#js-editor_wrapper").append(data.html);
            enableEditorRemoval(campaignId, data.ids);
        },
        error: function (XMLHttpRequest) {
            errorDisplay(XMLHttpRequest);
        }
    });
});