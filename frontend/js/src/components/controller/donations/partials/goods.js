var request = require('api').request,
    args = require('common/helpers').args,
    settings = require('settings').settings,
    currencyRound = require('common/helpers').currencyRoundUp,
    moment = require('moment'),
    individualGiftTemplate = require('../../mission/templates/mission_gift.hbs'),
    individualSelectedGiftTemplate = require('../../mission/templates/mission_gift_selected.hbs'),
    individualCheckoutGiftTemplate = require('../../mission/templates/mission_gift_checkout.hbs');


export function search(container, selectedContainer) {
    var input = $("#js-search-input"),
        greyPage = $("#sb-greyout-page"),
        app = $(".app-sb"),
        missionId = args(1);
    input
        .on("submit", function() {
            var $this = $(this),
                value = $this.val();
            greyPage.removeClass("sb_hidden");
            if (value) {
                request.get({
                    url: "/v1/product_search/?query=" + value
                }).done(function(res) {
                    container.empty();
                    var results = res.results,
                    // the time format here will format in this style: "5:46 pm"
                        time = moment().format("h:mm a");
                    for (var product in results) {
                        if (res.results.hasOwnProperty(product)){
                            results[product].time = time;
                            container.append(individualGiftTemplate({"product": results[product]}));
                        }
                    }
                    greyPage.addClass("sb_hidden");
                });
            } else {
                greyPage.addClass("sb_hidden");
            }

        })
        .on("keypress", function(e) {
            if (e.which === 13) {
                input.submit();
                return false;
            }
        });
    app
        .on("click", ".js-add", function() {
            var $this = $(this),
                productDetails = {
                    "asin": $this.data("product_id"),
                    "image": $this.data("product_image"),
                    "title": $this.data("product_description"),
                    "price": $this.data("product_price"),
                    "time": moment().format("h:mm a")
                };
            selectedContainer.prepend(individualSelectedGiftTemplate({"product": productDetails}));
            $this.closest(".product-container").remove();

            // auto save when product is added to giftlist
            greyPage.removeClass("sb_hidden");
            var productIds = [];
            $(".selected-product-container").each(function(i, obj) {
                productIds.push($(obj).data("vendor_id"));
            });
            request.patch({
                url: "/v1/missions/" + missionId + "/giftlist/",
                data: JSON.stringify({
                    product_ids: productIds
                })
            }).done(function(){
                greyPage.addClass("sb_hidden");
            });
        })
        .on("click", ".js-remove", function() {
            $(this).closest(".selected-product-container").remove();

            // auto save when product is added to giftlist
            greyPage.removeClass("sb_hidden");
            var productIds = [];
            $(".selected-product-container").each(function(i, obj) {
                productIds.push($(obj).data("vendor_id"));
            });
            request.patch({
                url: "/v1/missions/" + missionId + "/giftlist/",
                data: JSON.stringify({
                    product_ids: productIds
                })
            }).done(function(){
                greyPage.addClass("sb_hidden");
            });
        });
}


export function populateSelected(missionId, selectedContainer) {
    selectedContainer.append('<div class="loader"></div>');
    request.get({url: "/v1/missions/" + missionId + "/giftlist/?expand=true"})
        .done(function(response) {
            var results = response.products,
                time = moment().format("h:mm a");
            for (var product in results) {
                if (results.hasOwnProperty(product)) {
                    results[product].information.time = time;
                    selectedContainer.append(
                        individualSelectedGiftTemplate(
                            {"product": results[product].information}));
                }
            }
            selectedContainer.find(".loader").remove();
        });
}


export function calculateTotals(missionRate) {
    /**
     * Calculate order totals
     * @type {number}
     */
    var itemTotal = 0.00,
        sbCharge,
        orderTotal,
        objectPrice;
    // loop through all elements which hold price data for each object in the
    // selected list
    $(".js-remove").each(function(index, obj) {
        var $this = $(obj);
        objectPrice = $this.data("product_price");
        itemTotal += objectPrice;
    });

    // make calculations
    sbCharge = (itemTotal) * missionRate;
    orderTotal = itemTotal + sbCharge;

    // .toFixed(2) formats float values to x.xx for cash
    return {
        itemTotal: currencyRound(itemTotal).toFixed(2),
        sbCharge: currencyRound(sbCharge).toFixed(2),
        orderTotal: currencyRound(orderTotal).toFixed(2)
    };
}


export function populateCheckout(missionId, productContainer) {
    var orderId = localStorage.getItem(missionId + "_OrderId"),
        itemPrice = $("#js-items-price"),
        orderTotalContainer = $("#js-order-total"),
        sbPrice = $("#js-sb-charge-price");
    request.get({url: "/v1/orders/" + orderId + "/?expand=true"})
        .done(function(response) {
            var results = response.products,
                time = moment().format("h:mm a"),
                orderTotalKey = missionId + "orderTotal",
                total = response.total;
            orderTotalContainer.text(total / 100.0);
            for (var product in results) {
                if (results.hasOwnProperty(product)) {
                    results[product].information.time = time;
                    results[product].information.object_uuid = results[product].id;
                    productContainer.append(
                        individualCheckoutGiftTemplate(
                            {"product": results[product].information}));
                }
            }
            request.get({url: "/v1/missions/" + missionId + "/"})
                .done(function(response) {
                    var missionRate = response.quest.application_fee + settings.api.stripe_transaction_fee,
                        calculated = calculateTotals(missionRate);
                    itemPrice.text(calculated.itemTotal);
                    orderTotalContainer.text(calculated.orderTotal);
                    sbPrice.text(calculated.sbCharge);
                });
            localStorage.setItem(orderTotalKey, results.total);
            productContainer.find(".loader").remove();
        });
}