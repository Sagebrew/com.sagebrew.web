/*global $, jQuery, ajaxSecurity, errorDisplay, Stripe, StripeCheckout*/
$(document).ready(function () {
    Stripe.setPublishableKey($("#stripe_key").data('key'));
    var handler = StripeCheckout.configure({
            key: $("#stripe_key").data('key'),
            image: $("#stripe_img").data('stripe_image'),
            token: function (token) {
                var campaignId = $("#campaign_id").data('object_uuid');
                $.ajax({
                    xhrFields: {withCredentials: true},
                    type: "PUT",
                    url: "/v1/campaigns/" + campaignId + "/",
                    data: JSON.stringify({
                        "customer_token": token.id
                    }),
                    contentType: "application/json; charset=utf-8",
                    dataType: "json",
                    success: function (data) {
                        $.notify("Updated Card Info", {type: 'success'});

                    },
                    error: function (XMLHttpRequest, textStatus, errorThrown) {
                        $(this).removeAttr("disabled");
                        errorDisplay(XMLHttpRequest);
                    }
                });
            }
        });
    $("#submit_settings").click(function (event) {
        event.preventDefault();
        var settingsData = {
                "website": $("#personal-social-address").val(),
                "facebook": $("#facebook-social-address").val(),
                "twitter": $("#twitter-social-address").val(),
                "linkedin": $("#linkedin-social-address").val(),
                "youtube": $("#youtube-social-address").val(),
                "ssn": $("#ssn").val(),
                "ein": $("#ein").val(),
                "activate": $("#js-active").data("active")
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
        window.location.href = "/quest/";
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
        var completedStripe = $("#completed-stripe").data("completed_stripe"),
            completedCustomer = $("#js-completed_customer").data("completed_customer");
        if (completedStripe === "False") {
            $("html, body").animate({scrollTop: 0}, "slow");
            $.notify("Please fill in the banking information portion of this page. You may only take your Quest active after that.", {type: "info"});
        } else if (completedCustomer === "False") {
            handler.open({
                name: "Sagebrew LLC",
                description: "Premium Sagebrew Quest Subscription",
                panelLabel: "Subscribe"
            });
        } else {
            var campaignId = $("#campaign_id").data('object_uuid');
            $.ajax({
                xhrFields: {withCredentials: true},
                type: "PATCH",
                url: "/v1/campaigns/" + campaignId + "/",
                data: JSON.stringify({
                    "activate": true
                }),
                contentType: "application/json; charset=utf-8",
                dataType: "json",
                success: function (data) {
                    if (data.active) {
                        $("#js-active").attr("data-active", "True");
                    } else {
                        $("#js-active").attr("data-active", "False");
                    }

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