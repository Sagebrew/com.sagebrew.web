/* global $ */
var request = require('api').request,
    args = require('common/helpers').args,
    goods = require('../../../donations/partials/goods'),
    individualGiftTemplate = require('../../templates/mission_gift_single.hbs'),
    individualSelectedGiftTemplate = require('../../templates/mission_gift_selected.hbs');

export const meta = {
    controller: "mission/mission-view/gifts",
    match_method: "path",
    check: [
        "^missions\/[A-Za-z0-9.@_%+-]{36}\/[A-Za-z0-9.@_%+-]{1,70}\/donate\/gifts$"
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
        shippingHandlingContainer = $("#js-shipping-handling-price"),
        estimatedTaxContainer = $("#js-estimated-tax-price"),
        beforeSbContainer = $("#js-before-sb-price"),
        sbChargeContainer = $("#js-sb-charge-price"),
        orderTotalContainer = $("#js-order-total-price");

    giftContainer.append('<div class="loader"></div>');
    request.get({url: "/v1/missions/" + missionId + "/giftlist/?expand=true"})
        .done(function(response) {
            var results = response.products;
            for (var product in results) {
                if (results.hasOwnProperty(product)) {
                    giftContainer.append(
                        individualGiftTemplate(
                            {"product": results[product].information}));
                }
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
                    "price" : $this.data("product_price")
                },
                calculatedTotals;
            selectedGiftContainer.append(
                individualSelectedGiftTemplate({"product": productDetails}));
            $this.closest(".product-container").remove();
            calculatedTotals = goods.calculateTotals(selectedGiftContainer);
            
            // Display calculated totals in order info box
            itemTotalContainer.text(calculatedTotals.itemTotal);
            shippingHandlingContainer.text(calculatedTotals.shipping);
            estimatedTaxContainer.text(calculatedTotals.estimatedTax);
            beforeSbContainer.text(calculatedTotals.beforeSb);
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
                    "price" : $this.data("product_price")
                },
                calculatedTotals;
            giftContainer.append(
                individualGiftTemplate({"product": productDetails}));
            $this.closest(".selected-product-container").remove();

            calculatedTotals = goods.calculateTotals(selectedGiftContainer);

            // Display calculated totals in order info box
            itemTotalContainer.text(calculatedTotals.itemTotal);
            shippingHandlingContainer.text(calculatedTotals.shipping);
            estimatedTaxContainer.text(calculatedTotals.estimatedTax);
            beforeSbContainer.text(calculatedTotals.beforeSb);
            sbChargeContainer.text(calculatedTotals.sbCharge);
            orderTotalContainer.text(calculatedTotals.orderTotal);
            console.log(selectedGiftContainer.length);
            if (!$(".selected-product-container").length) {
                noSelectedGifts.removeClass("sb_hidden");
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