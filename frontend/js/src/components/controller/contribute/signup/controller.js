/* global $ */
var requests = require('api').request,
    helpers = require('common/helpers'),
    validators = require('common/validators'),
    addresses = require('common/addresses'),
    moment = require('moment'),
    noAddress = require('./partials/noaddress'),
    reqAddress = require('./partials/address'),
    addressFormPartial = require('../templates/address_form_partial.hbs'),
    campaignFinancePartial = require('../templates/campaign_finance_partial.hbs'),
    signupButtonPartial = require('../templates/signup_button_partial.hbs');

export const meta = {
    controller: "contribute/signup",
    match_method: "path",
    check: [
        "^missions\/[A-Za-z0-9.@_%+-]{36}\/[A-Za-z0-9.@_%+-]{1,70}\/donate\/name$",
        "^missions\/[A-Za-z0-9.@_%+-]{36}\/[A-Za-z0-9.@_%+-]{1,70}\/endorse\/name$",
        "^missions\/[A-Za-z0-9.@_%+-]{36}\/[A-Za-z0-9.@_%+-]{1,70}\/volunteer\/name$",
        "^missions\/[A-Za-z0-9.@_%+-]{36}\/[A-Za-z0-9.@_%+-]{1,70}\/gifts\/name$"
    ]
};


/**
 * Init
 */
export function init() {

}

/**
 * Load
 */
export function load() {
    var missionId = helpers.args(1),
        slug = helpers.args(2),
        url = window.location.href,
        live = $(".live"),
        accountInfoBlock = $("#js-account-info-block"),
        campaignFinanceBlock = $("#js-campaign-finance-block");
    requests.get({url: "/v1/missions/" + missionId + "/"})
        .done(function(response) {
            if (response.focus_on_type === "position") {
                if (url.indexOf("/donate/name/") !== -1 || url.indexOf("/gifts/name") !== -1) {
                    // populate required forms for political campaign donation/gift signup
                    live.append(addressFormPartial());
                    var addressInfo = $("#js-address-block");
                    campaignFinanceBlock.append(campaignFinancePartial());
                    addressInfo.append(signupButtonPartial({back_url: "/missions/" + missionId + "/" + slug + "/", terms_and_conditions_url: "/help/terms/"}));

                    // activate page elements
                    reqAddress.activateAddress();
                } else {
                    // populate required forms for poltiical campaign endorse/volunteer signup
                    accountInfoBlock.append(signupButtonPartial({back_url: "/missions/" + missionId + "/" + slug + "/", terms_and_conditions_url: "/help/terms/"}));

                    // activate page elements
                    noAddress.activateNoAddress();
                }
            } else if (response.focus_on_type === "advocacy") {
                // populate required forms for advocacy mission signup for donate/gift/volunteer/endorse
                accountInfoBlock.append(signupButtonPartial({back_url: "/missions/" + missionId + "/" + slug + "/", terms_and_conditions_url: "/help/terms/"}));

                // activate page elements
                noAddress.activateNoAddress();
            }
        });
}

/**
 * Post Load
 */
export function postload() {
    //
    // Intercom Tracking
}