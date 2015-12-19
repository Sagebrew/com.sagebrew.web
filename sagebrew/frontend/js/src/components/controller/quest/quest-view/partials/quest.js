/*global StripeCheckout*/
var request = require('api').request,
    templates = require('template_build/templates'),
    settings = require('settings').settings,
    helpers = require('common/helpers');

export function load() {
    var $app = $(".app-sb"),
        missionList= document.getElementById('js-mission-list'),
        pageUser = helpers.args(1);

    request.get({url: '/v1/profiles/' + pageUser + '/missions/'})
        .done(function (data) {
            if(data.results.length === 0) {
                missionList.innerHTML = templates.position_holder({static_url: settings.static_url});
            } else {
                for(var i=0; i < data.results.length; i++){
                    data.results[i].focused_on.name = data.results[i].focused_on.name.replace('-', ' ');
                    data.results[i].focused_on.name = data.results[i].focused_on.name.replace(/\w\S*/g, function(txt){return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();});
                }
                missionList.innerHTML = templates.mission_summary({missions: data.results, static_url: settings.static_url});
            }
        });
    $app
        .on('click', '.radio-image-selector#js-donate-btn', function() {

        })
        .on('click', '.js-position', function () {
            if(this.id === "js-add-mission"){
                window.location.href = "/missions/select/";
            } else {
                window.location.href = "/missions/" + this.id + "/";
            }
        });

     var donationAmount = 0,
        stripeKey = settings.api.stripe || $("#stripe-publishable").data("stripe_key");

    var handler = StripeCheckout.configure({
        key: stripeKey,
        image: $("#stripe_img").data('stripe_image'),
        token: function (token) {
            var campaignId = $("#campaign_id").data('object_uuid');
            request.post({
                url: "/v1/campaigns/" + campaignId + "/donations/",
                data: JSON.stringify({
                    "amount": donationAmount,
                    "token": token.id
                })
            }).done(function (){
                "use strict";
                $("#donationModal").modal("hide");
                $.notify("Successfully Created Donation", {type: 'success'});
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
