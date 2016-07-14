/*var request = require('api').request,
    radioSelector = require('common/radioimage').radioSelector,
    helpers = require('common/helpers'),
    validators = require('common/validators'),
    addresses = require('common/addresses'),
    */
var settings = require('settings').settings,
    amazon = require('amazon-product-api'),
    individualGiftTemplate = require('../../mission/templates/mission_gift_single.hbs'),
    individualSelectedGiftTemplate = require('../../mission/templates/mission_gift_selected.hbs');

export function search(container, selectedContainer) {
    /*
    var client = amazon.createClient({
        awsId: "AKIAJMKAKDDVVIMLTK7Q",
        awsSecret: "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",
        awsTag: "mytag-20" //associate tag id
    });
    console.log(settings);
    console.log('here');
    client.itemSearch({
        director: 'Quentin Tarantino',
        actor: 'Samuel L. Jackson',
        searchIndex: 'DVD',
        audienceRating: 'R',
        responseGroup: 'ItemAttributes,Offers,Images'
    }, function (err, results, response) {
        if (err) {
            console.log(err);
        } else {
            console.log(results);
            console.log(response);
        }
    });
    */
    console.log(settings);
    console.log(amazon);
    var testProducts = [
        {
            "id": 1,
            "image": "https://ekit.co.uk/GalleryEntries/eCommerce_solutions_and_services/MedRes_Product-presentation-2.jpg?q=27012012153123",
            "description": "Rubik's Cube 2x2",
            "price": "$19.99"
        },
        {
            "id": 2,
            "image": "https://encrypted-tbn2.gstatic.com/images?q=tbn:ANd9GcRsFHhZonEY0b0WDB5jybUyX7f-0mEPucuEMLS6crbv81ejmikY",
            "description": "Nikon Camera",
            "price": "$499.99"
        },
        {
            "id": 3,
            "image": "http://www.sammobile.com/wp-content/uploads/2012/08/Samsung-ATIV-Tab-Product-Image-4.jpg",
            "description": "Samsung Tablet",
            "price": "$799.99"
        },
        {
            "id": 4,
            "image": "https://encrypted-tbn3.gstatic.com/images?q=tbn:ANd9GcSjiD8piWBqf3qpL1aWHolPlEsufiMTw2IDtjnBh2q6sxLtVPJtQQ",
            "description": "Watch",
            "price": "$49.99"
        }
    ];
    for (var product in testProducts) {
        if (testProducts.hasOwnProperty(product)){
            container.append(individualGiftTemplate({"product": testProducts[product]}));
            activateSearchReturned(testProducts[product].id, selectedContainer);
        }
    }
    for (var selectedProduct in testProducts) {
        if (testProducts.hasOwnProperty(selectedProduct)){
            selectedContainer.append(individualSelectedGiftTemplate({"product": testProducts[selectedProduct]}));
            activateSelected(testProducts[selectedProduct].id);
        }

    }
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
                "description": $this.data("product_description"),
                "price" : $this.data("product_price")
            };
        selectedContainer.append(individualSelectedGiftTemplate({"product": productDetails}));
        activateSelected(productID);
        $this.closest(".product-container").remove();
    });
}