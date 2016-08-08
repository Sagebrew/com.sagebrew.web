/* global $ */
var request = require('api').request,
    settings = require('settings').settings,
    args = require('common/helpers').args,
    moment = require('moment'),
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
        slug = args(2),
        noSelectedGifts = $("#js-no-selected-gifts"),
        itemTotalContainer = $("#js-items-price"),
        shippingHandlingContainer = $("#js-shipping-handling-price"),
        estimatedTaxContainer = $("#js-estimated-tax-price"),
        beforeSbContainer = $("#js-before-sb-price"),
        sbChargeContainer = $("#js-sb-charge-price"),
        orderTotalContainer = $("#js-order-total-price"),
        missionRate = 0.07;
    request.get({url: "/v1/missions/" + missionId + "/"})
        .done(function(response) {
            if (response.quest.account_type === "free") {
                missionRate = 0.07;
            } else if (response.quest.account_type === "paid") {
                missionRate = 0.05;
            }
        });
    giftContainer.append('<div class="loader"></div>');
    request.get({url: "/v1/missions/" + missionId + "/giftlist/?expand=true"})
        .done(function(response) {
            var results = response.products,
                time = moment().format("h:mm a");
            for (var product in results) {
                if (results.hasOwnProperty(product)) {
                    results[product].information.time = time;
                    results[product].information.object_uuid = results[product].id;
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
                    "price" : $this.data("product_price"),
                    "object_uuid": $this.data("object_uuid")
                },
                calculatedTotals,
                time = moment().format("h:mm a");
            productDetails.time = time;
            selectedGiftContainer.append(
                individualSelectedGiftTemplate({"product": productDetails}));
            $this.closest(".product-container").remove();
            calculatedTotals = goods.calculateTotals(missionRate);
            
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
            shippingHandlingContainer.text(calculatedTotals.shipping);
            estimatedTaxContainer.text(calculatedTotals.estimatedTax);
            beforeSbContainer.text(calculatedTotals.beforeSb);
            sbChargeContainer.text(calculatedTotals.sbCharge);
            orderTotalContainer.text(calculatedTotals.orderTotal);
            if (!$(".selected-product-container").length) {
                noSelectedGifts.removeClass("sb_hidden");
            }
        })
        .on('click', '#js-place-order', function(e) {
            e.preventDefault();
            var productIds = [],
                greyPage = $(".sb-greyout-page"),
                total = $("#js-order-total-price").text();
            greyPage.removeClass("sb_hidden");
            $(".selected-product-container").each(function(i, obj) {
                productIds.push($(obj).data("object_uuid"));
            });
            total = parseInt(parseFloat(total) * 100, 10);
            request.post({
                url: "/v1/orders/",
                data: JSON.stringify({
                    product_ids: productIds,
                    total: total,
                    mission: missionId
                })
            }).done(function(response){
                greyPage.addClass("sb_hidden");
                // TODO take to payment processing pages, if no default card 
                // have them input a card
                localStorage.setItem(missionId + "_OrderId", response.id);
                window.location.href = "/missions/" + missionId + "/" + slug + "/gifts/payment/";
            });
        });
}

/**
 * Post Load
 */
export function postload() {
    //
    // Intercom Tracking
}