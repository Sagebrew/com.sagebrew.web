/*var request = require('api').request,
    radioSelector = require('common/radioimage').radioSelector,
    helpers = require('common/helpers'),
    validators = require('common/validators'),
    addresses = require('common/addresses'),
    */
var settings = require('settings').settings,
    request = require('api').request,
    amazon = require('amazon-product-api'),
    individualGiftTemplate = require('../../mission/templates/mission_gift_single.hbs'),
    individualSelectedGiftTemplate = require('../../mission/templates/mission_gift_selected.hbs');

export function search(container, selectedContainer) {
    var client = amazon.createClient({
        awsId: "AKIAI5PAWWJNUQPPXL3Q",
        awsSecret: "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",
        awsTag: "sagebrew-20" //associate tag id
    });
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
    request.get({url: 'https://webservices.amazon.com/onca/xml?AWSAccessKeyId=AKIAI5PAWWJNUQPPXL3Q&Actor=Samuel%20L.%20Jackson&AssociateTag=sagebrew-20&AudienceRating=R&Condition=All&Director=Quentin%20Tarantino&ItemPage=1&Keywords=&Operation=ItemSearch&ResponseGroup=ItemAttributes%2COffers%2CImages&SearchIndex=DVD&Service=AWSECommerceService&Timestamp=2016-07-16T22%3A21%3A33.035Z&Version=2013-08-01&Signature=xc5eGJ1XVxblDim4QdtrMXqGm5PPjX6QSDnVhMv9JiM%3D'})
        .done(function(res, that) {
            console.log(res);
            console.log(that);
            console.log('here');
        });

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