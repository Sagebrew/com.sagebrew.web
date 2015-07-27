/*global $, jQuery, ajaxSecurity*/
$(document).ready(function () {
    $("#js-get_donation_csv").click(function (event) {
        event.preventDefault();
        var campaignId = $("#campaign_id").data('object_uuid');
        window.location.href = "/v1/campaigns/" + campaignId + "/donation_data/";
    });
});