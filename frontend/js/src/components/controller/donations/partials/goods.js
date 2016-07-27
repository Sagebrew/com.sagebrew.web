/*var request = require('api').request,
    radioSelector = require('common/radioimage').radioSelector,
    helpers = require('common/helpers'),
    validators = require('common/validators'),
    addresses = require('common/addresses'),
    */
var settings = require('settings').settings,
    request = require('api').request,
    individualGiftTemplate = require('../../mission/templates/mission_gift_single.hbs'),
    individualSelectedGiftTemplate = require('../../mission/templates/mission_gift_selected.hbs');

export function search(container, selectedContainer) {
    request.get({
        url: "/v1/product_search/?query=water"
    })
        .done(function(response){
            var results = response.results;
            for (var product in results) {
                if (response.results.hasOwnProperty(product)){
                    container.append(individualGiftTemplate({"product": results[product]}));
                    activateSearchReturned(results[product].asin, selectedContainer);
                }
            }
        });
}

function activateSelected(productID) {
    $(".app-sb").on("click", "#" + productID + "-remove", function() {
        $(this).closest(".selected-product-container").remove();
    });
}

function activateSearchReturned(productID, selectedContainer) {
    $(".app-sb").on("click", "#" + productID + "-add", function() {
        var $this = $(this),
            productDetails = {
                "id": $this.data("product_id"),
                "image": $this.data("product_image"),
                "title": $this.data("product_description"),
                "price" : $this.data("product_price")
            };
        selectedContainer.append(individualSelectedGiftTemplate({"product": productDetails}));
        activateSelected(productID);
        $this.closest(".product-container").remove();
    });
}