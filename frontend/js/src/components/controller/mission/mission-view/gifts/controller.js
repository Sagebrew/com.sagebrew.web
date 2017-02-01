/* global $ */
var request = require('api').request,
    settings = require('settings').settings,
    args = require('common/helpers').args,
    moment = require('moment'),
    goods = require('../../../donations/partials/goods'),
    individualGiftTemplate = require('../../templates/mission_gift.hbs'),
    individualSelectedGiftTemplate = require('../../templates/mission_gift_selected.hbs'),
    completeSelect = require('./payment/partials/select').completeSelect,
    validators = require('common/validators'),
    addresses = require('common/addresses');

export const meta = {
    controller: "mission/mission-view/gifts",
    match_method: "path",
    check: [
        "^missions\/[A-Za-z0-9.@_%+-]{36}\/[A-Za-z0-9.@_%+-]{1,70}\/gifts\/donate$"
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
    var app = $(".app-sb"),
        giftContainer = $("#js-gift-container"),
        selectedGiftContainer = $("#js-selected-gift-container"),
        missionId = args(1),
        noSelectedGifts = $("#js-no-selected-gifts"),
        itemTotalContainer = $("#js-items-price"),
        sbChargeContainer = $("#js-sb-charge-price"),
        orderTotalContainer = $("#js-order-total-price"),
        campaignFinanceValidationForm,
        campaignFinanceForm = document.getElementById('campaign-finance'),
        addressForm = document.getElementById('address'),
        addressValidationForm = addresses.setupAddress(function callback() {}),
        missionRate = 0.07;
    $(':checkbox').radiocheck();
    request.get({url: "/v1/missions/" + missionId + "/"})
        .done(function(response) {
            missionRate = response.quest.application_fee +
                settings.api.stripe_transaction_fee;
        });
    if(campaignFinanceForm !== undefined && campaignFinanceForm !== null) {
        campaignFinanceValidationForm = $(campaignFinanceForm);
        validators.campaignFinanceValidator(campaignFinanceValidationForm);
    }
    giftContainer.append('<div class="loader"></div>');
    request.get({url: "/v1/missions/" + missionId + "/giftlist/?expand=true"})
        .done(function(response) {
            var results = response.products,
                time = moment().format("h:mm a");
            if (results !== []) {
                for (var product in results) {
                    if (results.hasOwnProperty(product)) {
                        results[product].information.time = time;
                        results[product].information.object_uuid = results[product].id;
                        if (results[product].information.has_reviews) {
                            results[product].information.iframe = results[product].information.iframe.replace(/^http:\/\//i, 'https://');
                        }
                        giftContainer.append(
                            individualGiftTemplate(
                                {
                                    "product": results[product].information,
                                    "list_setup": false
                                }));
                    }
                }
            } else {
                $("#js-place-order").remove();
                $("#js-disclaimer").text("Sorry this Mission has not setup their Giftlist yet!");
            }

            giftContainer.find(".loader").remove();
        });
    app
        .on('click', '.js-add', function(){
            var $this = $(this),
                productDetails = {
                    "asin": $this.data("product_id"),
                    "image": $this.data("product_image"),
                    "title": $this.data("product_description"),
                    "price" : $this.data("product_price"),
                    "object_uuid": $this.data("object_uuid"),
                    "time": moment().format("h:mm a")
                },
                calculatedTotals;
            selectedGiftContainer.append(
                individualSelectedGiftTemplate({"product": productDetails}));
            $this.closest(".product-container").remove();
            calculatedTotals = goods.calculateTotals(missionRate);
            
            // Display calculated totals in order info box
            itemTotalContainer.text(calculatedTotals.itemTotal);
            sbChargeContainer.text(calculatedTotals.sbCharge);
            orderTotalContainer.text(calculatedTotals.orderTotal);
            if (!noSelectedGifts.hasClass("sb_hidden")) {
                noSelectedGifts.addClass("sb_hidden");
            }
        })
        .on('click', '.js-remove', function() {
            var $this = $(this),
                productDetails = {
                    "asin": $this.data("product_id"),
                    "image": $this.data("product_image"),
                    "title": $this.data("product_description"),
                    "price" : $this.data("product_price"),
                    "object_uuid": $this.data("object_uuid")
                },
                calculatedTotals;
            giftContainer.append(
                individualGiftTemplate({"product": productDetails}));
            $this.closest(".selected-product-container").remove();

            calculatedTotals = goods.calculateTotals(missionRate);

            // Display calculated totals in order info box
            itemTotalContainer.text(calculatedTotals.itemTotal);
            sbChargeContainer.text(calculatedTotals.sbCharge);
            orderTotalContainer.text(calculatedTotals.orderTotal);
            if (!$(".selected-product-container").length) {
                noSelectedGifts.removeClass("sb_hidden");
            }
        })
        .on('click', '#js-place-order', function(e) {
            e.preventDefault();
            completeSelect(missionId, campaignFinanceValidationForm, 
                addressForm, addressValidationForm);
        })
        .on('click', '#retired-or-not-employed', function () {
            if(campaignFinanceValidationForm !== null && campaignFinanceValidationForm !== undefined) {
                campaignFinanceValidationForm.formValidation('revalidateField', 'campaignFinanceForm');
                campaignFinanceValidationForm.formValidation('revalidateField', 'onlyOneSelector');
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