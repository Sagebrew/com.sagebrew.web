/*global $, jQuery, ajaxSecurity*/
function enablePromotion(campaignId) {
    $(".js-add_accountant").click(function(event) {
        event.preventDefault();
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "POST",
            url: "/v1/campaigns/" + campaignId + "/add_accountants/",
            contentType: "application/json; charset=utf-8",
            data: JSON.stringify({
                "profiles": [$(this).data('username')]
            }),
            dataType: "json",
            success: function (data) {
                $("#js-accountant_wrapper").append(data);
            },
            error: function (XMLHttpRequest) {
                if (XMLHttpRequest.status === 500) {
                    $("#server_error").show();
                }
            }
        });
    });
    $(".js-add_editor").click(function (event) {
        event.preventDefault();
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "POST",
            url: "/v1/campaigns/" + campaignId + "/add_editors/",
            contentType: "application/json; charset=utf-8",
            data: JSON.stringify({
                "profiles": [$(this).data('username')]
            }),
            dataType: "json",
            success: function (data) {
                $("#js-accountant_wrapper").append(data);
            },
            error: function (XMLHttpRequest) {
                if (XMLHttpRequest.status === 500) {
                    $("#server_error").show();
                }
            }
        });
    });
}

function enableEditorRemoval(campaignId) {
    $(".js-remove_editor").click(function (event) {
        event.preventDefault();
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "POST",
            url: "/v1/campaigns/" + campaignId + "/remove_editors/",
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            data: JSON.stringify({
                "profiles": [$(this).data('username')]
            }),
            success: function (data) {
                $("#js-accountant_wrapper").append(data);
            },
            error: function (XMLHttpRequest) {
                if (XMLHttpRequest.status === 500) {
                    $("#server_error").show();
                }
            }
        });
    });
}

function enableAccountantRemoval(campaignId) {
    $(".js-remove_accountant").click(function (event) {
        event.preventDefault();
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "POST",
            url: "/v1/campaigns/" + campaignId + "/remove_accountants/",
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            data: JSON.stringify({
                "profiles": [$(this).data('username')]
            }),
            success: function (data) {
                $("#js-accountant_wrapper").append(data);
            },
            error: function (XMLHttpRequest) {
                if (XMLHttpRequest.status === 500) {
                    $("#server_error").show();
                }
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
            if (XMLHttpRequest.status === 500) {
                $("#server_error").show();
            }
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
            if (XMLHttpRequest.status === 500) {
                $("#server_error").show();
            }
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
            if (XMLHttpRequest.status === 500) {
                $("#server_error").show();
            }
        }
    });
});