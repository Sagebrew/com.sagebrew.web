/**
 * @file
 */
var request = require('api').request;

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
    console.log("quest-manage");

    //
    // Go live
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
                    $('#sb-greyout-page').hide();
                    if (data.active) {
                        $("#js-active").attr("data-active", "True");
                        window.location.href = data.url;
                    } else {
                        $("#js-active").attr("data-active", "False");
                    }

                },
                error: function (XMLHttpRequest, textStatus, errorThrown) {
                    $('#sb-greyout-page').hide();
                    $('#sb-greyout-page').spin(false);
                    errorDisplay(XMLHttpRequest);
                }
            });
        }

    });
}