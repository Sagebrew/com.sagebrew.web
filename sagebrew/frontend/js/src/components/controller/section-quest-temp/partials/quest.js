var request = require('./../../../api').request,
    templates = require('./../../../template_build/templates'),
    settings = require('./../../../settings').settings,
    helpers = require('./../../../common/helpers');

export function load() {
    var $app = $(".app-sb"),
        missionList= document.getElementById('js-mission-list'),
        endorsedList = document.getElementById('js-endorsed-list'),
        pageUser = helpers.args(1);

    request.get({url: '/v1/profiles/' + pageUser + '/missions/'})
        .done(function (data) {
            "use strict";
            if(data.results.length == 0) {
                missionList.innerHTML = templates.position_holder();
            } else {
                missionList.innerHTML = templates.mission_summary({missions: data.results});
            }
        });
    $app
        .on('click', '.radio-image-selector#js-add-mission', function() {
            "use strict";
            window.location.href = "/quest/mission/select/";
        })
        .on('click', '#js-donate-btn', function() {
            "use strict";

        });

     var donationAmount = 0,
        stripeKey = settings.api.stripe || $("#stripe-publishable").data("stripe_key");

    handler = StripeCheckout.configure({
        key: stripeKey,
        image: $("#stripe_img").data('stripe_image'),
        token: function (token) {
            var campaignId = $("#campaign_id").data('object_uuid');
            $.ajax({
                xhrFields: {withCredentials: true},
                type: "POST",
                url: "/v1/campaigns/" + campaignId + "/donations/",
                data: JSON.stringify({
                    "amount": donationAmount,
                    "token": token.id
                }),
                contentType: "application/json; charset=utf-8",
                dataType: "json",
                success: function () {
                    $("#donationModal").modal("hide");
                    $.notify("Successfully Created Donation", {type: 'success'});
                },
                error: function (XMLHttpRequest) {
                    $(this).removeAttr("disabled");
                    errorDisplay(XMLHttpRequest);
                }
            });
        }
    });
    $(".donation-amount-selector").click(function (event) {
        event.preventDefault();
        donationAmount = $(this).data("amount") * 100;
        handler.open({
            name: "Sagebrew LLC",
            description: "Quest Donation",
            amount: $(this).data("amount") * 100,
            panelLabel: "Pledge {{amount}}"
        });
    });
    $("#custom-donation-btn").click(function (event) {
        event.preventDefault();
        donationAmount = $("#custom-donation").val() * 100;
        handler.open({
            name: "Sagebrew LLC",
            description: "Quest Donation",
            amount: $("#custom-donation").val() * 100,
            panelLabel: "Pledge {{amount}}"
        });
    });
    $(window).on('popstate', function () {
        handler.close();
    });
}
