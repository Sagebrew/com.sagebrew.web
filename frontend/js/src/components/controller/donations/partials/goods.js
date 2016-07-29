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
                    var results = res.results;
                    for (var product in results) {
                        if (res.results.hasOwnProperty(product)){
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
            }).done(function(response){
                greyPage.addClass("sb_hidden");
                $.notify({message: "Succesfully Save Selected Gift List!"}, {type: "success"});
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