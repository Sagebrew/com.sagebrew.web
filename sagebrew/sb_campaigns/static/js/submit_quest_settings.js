/*global $, ajaxSecurity, errorDisplay, Stripe, StripeCheckout*/
function getSettingsData() {
    return {
        "website": $("#personal-social-address").val(),
        "facebook": $("#facebook-social-address").val(),
        "twitter": $("#twitter-social-address").val(),
        "linkedin": $("#linkedin-social-address").val(),
        "youtube": $("#youtube-social-address").val(),
        "ssn": $("#ssn").val(),
        "ein": $("#ein").val(),
        "activate": $("#js-active").data("active"),
        "routing_number": $("#routing-number").val(),
        "account_number": $("#account-number").val()
    };
}

$(document).ready(function () {
    var stripeContainer = $("#stripe_key");
    Stripe.setPublishableKey(stripeContainer.data('key'));
    var handler = StripeCheckout.configure({
            key: stripeContainer.data('key'),
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
                        var takingLive = $("#js-taking_live");
                        if (takingLive.data("taking_live") === "True") {
                            var campaignId = $("#campaign_id").data('object_uuid');
                            $('#sb-greyout-page').show();
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
                                        $.notify("Quest taken active!", {type: "success"});
                                        $('#sb-greyout-page').hide();
                                        window.location.href = data.url;
                                    } else {
                                        $('#sb-greyout-page').hide();
                                        $("#js-active").attr("data-active", "False");
                                    }

                                },
                                error: function (XMLHttpRequest, textStatus, errorThrown) {
                                    errorDisplay(XMLHttpRequest);
                                }
                            });
                        }
                    },
                    error: function (XMLHttpRequest, textStatus, errorThrown) {
                        $(this).removeAttr("disabled");
                        errorDisplay(XMLHttpRequest);
                    }
                });
            }
        });
    function stripeResponseHandler(status, response) {
        if (response.error) {
            if ($("#completed-stripe").data("completed_stripe") !== "True") {
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
                    var takingLive = $("#js-taking_live");
                    $("#completed-stripe").data("completed_stripe", data.completed_stripe);
                    if (data.completed_stripe) {
                        $("#js-banking-block").addClass("sb_hidden");
                        if (takingLive.data('taking_live') === "True" && data.paid_account && !data.completed_customer) {
                            handler.open({
                                name: "Sagebrew LLC",
                                description: "Sagebrew Quest Subscription",
                                panelLabel: "Subscribe"
                            });
                        } else if (takingLive.data('taking_live') === "True") {
                            var campaignId = $("#campaign_id").data('object_uuid');
                            $('#sb-greyout-page').show();
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
                                        $.notify("Quest taken active!", {type: "success"});
                                        $('#sb-greyout-page').hide();
                                        window.location.href = data.url;
                                    } else {
                                        $("#js-active").attr("data-active", "False");
                                        $('#sb-greyout-page').hide();
                                    }

                                },
                                error: function (XMLHttpRequest) {
                                    errorDisplay(XMLHttpRequest);
                                }
                            });
                        }
                    }
                },
                error: function (XMLHttpRequest) {
                    errorDisplay(XMLHttpRequest);
                }
            });
        }
    }
    $("#submit_settings").click(function (event) {
        event.preventDefault();
        var settingsData = getSettingsData(),
            campaignId = $("#campaign_id").data('object_uuid');
        Stripe.bankAccount.createToken({
            country: "US",
            currency: "USD",
            routing_number: settingsData.routing_number,
            account_number: settingsData.account_number
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
        var settingsData = getSettingsData(),
            campaignId = $("#campaign_id").data('object_uuid'),
            completedStripe = $("#completed-stripe").data("completed_stripe"),
            completedCustomer = $("#js-completed_customer").data("completed_customer"),
            paidAccount = $("#js-paid_account").data("paid_account"),
            takingLive = $("#js-taking_live");
        takingLive.data("taking_live", "True");
        if (completedStripe === "False") {

            if (settingsData.ssn && settingsData.routing_number && settingsData.account_number) {
                $('#sb-greyout-page').show();
                $("#sb-greyout-page").spin('large');
                $("#submit_settings").click();
            } else {
                $("html, body").animate({scrollTop: 0}, "slow");
                $.notify("Please fill in the banking information portion of this page. You may only take your Quest active after that.", {type: "info"});
            }
        } else if (completedCustomer === "False" && paidAccount === "True") {
            handler.open({
                name: "Sagebrew LLC",
                description: "Sagebrew Quest Subscription",
                panelLabel: "Subscribe"
            });
        } else {
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
    $("#js-cancel-button").click(function(event){
        event.preventDefault();
        window.location.href = "/";
    });
});
