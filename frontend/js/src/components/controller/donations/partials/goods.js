var settings = require('settings').settings,
    request = require('api').request,
    args = require('common/helpers').args,
    individualGiftTemplate = require('../../mission/templates/mission_gift_single.hbs'),
    individualSelectedGiftTemplate = require('../../mission/templates/mission_gift_selected.hbs');

export function search(container, selectedContainer) {
    var input = $("#js-search-input"),
        saveButton = $("#js-save-list"),
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
                        now = new Date($.now()),
                        time = now.getHours() + ":" + now.getMinutes() +
                            ' GMT - <a href="#" onclick="return false;" ' +
                            'data-toggle="tooltip" title="Product prices and ' +
                            'availability are accurate as of the date/time ' +
                            'indicated and are subject to change. Any price and ' +
                            'availability information displayed on relevant Amazon ' +
                            'Site(s), as applicable at the time of purchase will ' +
                            'apply to the purchase of this product.">Details</a>';
                    for (var product in results) {
                        if (res.results.hasOwnProperty(product)){
                            results[product].time = time;
                            container.append(individualGiftTemplate({"product": results[product]}));
                        }
                    }
                    $('[data-toggle="tooltip"]').tooltip();
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
    saveButton
        .on("click", function(e) {
            e.preventDefault();
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
                $.notify({message: "Successfully Saved Gift List!"}, {type: "success"});
            });

        });
    app
        .on("click", ".js-add", function() {
            var $this = $(this),
                productDetails = {
                    "asin": $this.data("product_id"),
                    "image": $this.data("product_image"),
                    "title": $this.data("product_description"),
                    "price" : $this.data("product_price")
                };
            selectedContainer.append(individualSelectedGiftTemplate({"product": productDetails}));
            $this.closest(".product-container").remove();
        })
        .on("click", ".js-remove", function() {
            $(this).closest(".selected-product-container").remove();
        });
}

export function populateSelected(missionId, selectedContainer) {
    selectedContainer.append('<div class="loader"></div>');
    request.get({url: "/v1/missions/" + missionId + "/giftlist/?expand=true"})
        .done(function(response) {
            var results = response.products;
            for (var product in results) {
                if (results.hasOwnProperty(product)) {
                    selectedContainer.append(
                        individualSelectedGiftTemplate(
                            {"product": results[product].information}));
                }
            }
            selectedContainer.find(".loader").remove();
        });
}

export function calculateTotals(missionRate) {
    var itemTotal = 0.00,
        shipping = 0.00,
        estimatedTax,
        beforeSb,
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
    console.log(settings);
    estimatedTax = itemTotal * 0.06;
    beforeSb = itemTotal + estimatedTax + shipping;
    sbCharge = (itemTotal) * missionRate;
    orderTotal = itemTotal + estimatedTax + sbCharge + shipping;

    // .toFixed(2) formats float values to x.xx for cash
    return {
        itemTotal: itemTotal.toFixed(2),
        estimatedTax: estimatedTax.toFixed(2),
        shipping: shipping.toFixed(2),
        beforeSb: beforeSb.toFixed(2),
        sbCharge: sbCharge.toFixed(2),
        orderTotal: orderTotal.toFixed(2)
    };
}