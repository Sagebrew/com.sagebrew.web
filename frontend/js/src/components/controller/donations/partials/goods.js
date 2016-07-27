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
    var input = $("#js-search-input"),
        saveButton = $("#js-save-list"),
        greyPage = $("#sb-greyout-page");
    console.log(greyPage);
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
                    var results = res.results;
                    for (var product in results) {
                        if (res.results.hasOwnProperty(product)){
                            container.append(individualGiftTemplate({"product": results[product]}));
                            activateSearchReturned(results[product].asin, selectedContainer);
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
    saveButton
        .on("click", function(e) {
            e.preventDefault();
            greyPage.removeClass("sb_hidden");
            greyPage.addClass("sb_hidden");
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
                "asin": $this.data("product_id"),
                "image": $this.data("product_image"),
                "title": $this.data("product_description"),
                "price" : $this.data("product_price")
            };
        selectedContainer.append(individualSelectedGiftTemplate({"product": productDetails}));
        activateSelected(productID);
        $this.closest(".product-container").remove();
    });
}