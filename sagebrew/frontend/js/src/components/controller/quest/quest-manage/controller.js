/*global getSettingsData*/

/**
 * @file
 */
var request = require('api').request,
    helpers = require('common/helpers');

/**
 * Meta.
 */
export const meta = {
    controller: "quest/quest-manage",
    match_method: "path",
    check: [
       "^quests\/[A-Za-z0-9.@_%+-]{1,36}\/manage"
    ]
};


/**
 * Load.
 */
export function load() {

    //
    // Go live
    $("#take_live").click(function (event) {
        event.preventDefault();
        var settingsData = getSettingsData(),
            campaignId = $("#campaign_id").data('object_uuid'),
            completedStripe = $("#completed-stripe").data("completed_stripe"),
            completedCustomer = $("#js-completed_customer").data("completed_customer"),
            paidAccount = $("#js-paid_account").data("paid_account"),
            takingLive = $("#js-taking_live"),
            greyPage = $('#sb-greyout-page');
        takingLive.data("taking_live", "True");
        if (completedStripe === "False") {
            if (settingsData.ssn && settingsData.routing_number && settingsData.account_number) {
                greyPage.show();
                greyPage.spin('large');
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
            $('#sb-greyout-page').show();
            request.patch({
                url: "/v1/campaigns/" + campaignId + "/",
                data: JSON.stringify({
                    "activate": true
                })
            }).done(function (data) {
                $('#sb-greyout-page').hide();
                if (data.active) {
                    $("#js-active").attr("data-active", "True");
                    window.location.href = data.url;
                } else {
                    $("#js-active").attr("data-active", "False");
                }
            }).fail(function () {
                greyPage.hide();
                greyPage.spin(false);
                request.errorDisplay(XMLHttpRequest);
            });
        }

    });
}