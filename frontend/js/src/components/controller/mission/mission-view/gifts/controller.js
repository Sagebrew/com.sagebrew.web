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
    var giftContainer = $("#js-gift-container"),
        selectedGiftContainer = $("#js-selected-gift-container"),
        missionId = args(1),
        app = $(".app-sb");

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
                };
            selectedGiftContainer.append(
                individualSelectedGiftTemplate({"product": productDetails}));
            $this.closest(".product-container").remove();
        })
        .on('click', '.js-remove', function() {
            var $this = $(this),
                productDetails = {
                    "asin": $this.data("product_id"),
                    "image": $this.data("product_image"),
                    "title": $this.data("product_description"),
                    "price" : $this.data("product_price")
                };
            giftContainer.append(
                individualGiftTemplate({"product": productDetails}));
            $this.closest(".selected-product-container").remove();
        });
}

/**
 * Post Load
 */
export function postload() {
    //
    // Intercom Tracking
}