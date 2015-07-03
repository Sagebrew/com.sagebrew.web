/*global $, jQuery, ajaxSecurity, errorDisplay, Stripe*/

$(document).ready(function () {
    Stripe.setPublishableKey("pk_test_4VQN9H9N2kXFGMIziWSa09ak");
    $("#submit_settings").click(function (event) {
        event.preventDefault();
        var settingsData = {
                "website": $("#personal-social-address").val(),
                "facebook": $("#facebook-social-address").val(),
                "twitter": $("#twitter-social-address").val(),
                "linkedin": $("#linkedin-social-address").val(),
                "youtube": $("#youtube-social-address").val(),
                "ssn": $("#ssn").val(),
                "ein": $("#ein").val()
            },
            campaignId = $("#campaign_id").data('object_uuid');
        Stripe.bankAccount.createToken({
            country: "US",
            currency: "USD",
            routing_number: $("#routing-number").val(),
            account_number: $("#account-number").val()
        }, stripeResponseHandler);
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "PATCH",
            url: "/v1/campaigns/" + campaignId + "/",
            data: JSON.stringify(settingsData),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (data) {
                $.notify("Successfully updated Quest!", {type: 'success'});
            },
            error: function (XMLHttpRequest, textStatus, errorThrown) {
                errorDisplay(XMLHttpRequest);
            }
        });
    });
    $("#register-for-quest").click(function (event) {
        window.location.href = "/registration/quest_info/";
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
    $("#take_live").click(function (event) {
        event.preventDefault();
        var completedStripe = $("#completed-stripe").data("completed_stripe");
        if (completedStripe === "False") {
            $("html, body").animate({scrollTop: 0}, "slow");
            $.notify("Please fill in the banking information portion of this page. You may only take your Quest active after that.", {type: "success"});
        } else {
            var campaignId = campaignId = $("#campaign_id").data('object_uuid');
            $.ajax({
                xhrFields: {withCredentials: true},
                type: "PATCH",
                url: "/v1/campaigns/" + campaignId + "/",
                data: JSON.stringify({
                    "active": true
                }),
                contentType: "application/json; charset=utf-8",
                dataType: "json",
                success: function (data) {
                },
                error: function (XMLHttpRequest, textStatus, errorThrown) {
                    errorDisplay(XMLHttpRequest);
                }
            });
        }
    });
});
function stripeResponseHandler(status, response) {
    if (response.error) {
        if (!$("#completed-stripe").data("completed_stripe")) {
            $.notify(response.error.message, {type: 'danger'});
        }
    } else {
        var token = response.id,
            campaignId = $("#campaign_id").data('object_uuid'),
            stripeData = {
                "stripe_token": token
            };
        if ($("#ssn").val() !== "") {
            stripeData.ssn = $("#ssn").val();
        }
        if ($("#ein").val() !== "") {
            stripeData.ein = $("#ein").val();
        }
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "PATCH",
            url: "/v1/campaigns/" + campaignId + "/",
            data: JSON.stringify(stripeData),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (data) {
            },
            error: function (XMLHttpRequest, textStatus, errorThrown) {
                errorDisplay(XMLHttpRequest);
            }
        });
    }
}