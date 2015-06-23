/*global $, jQuery, ajaxSecurity, errorDisplay, Stripe*/
function stripeResponseHandler(status, response) {
    if (response.error) {
        $.notify(response.error.message, {type: 'danger'});
    } else {
        var token = response.id;
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "PATCH",
            url: "/v1/campaigns/" + campaignId + "/",
            data: JSON.stringify({
                "stripe_token": token
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
}
$(document).ready(function () {
    Stripe.setPublishableKey("pk_test_BvgnQJjwcednzpsx4Q4Uqv8p");
    $("#submit_settings").click(function (event) {
        event.preventDefault();
        var settingsData = {
                "website": $("#personal-social-address").val(),
                "facebook": $("#facebook-social-address").val(),
                "twitter": $("#twitter-social-address").val(),
                "linkedin": $("#linkedin-social-address").val(),
                "youtube": $("#youtube-social-address").val()
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
    $("#take_live").click(function (event) {
        event.preventDefault();
    });
});