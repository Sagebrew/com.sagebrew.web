var request = require('api').request,
    individualCheckoutGiftTemplate = require('../../../mission/templates/mission_gift_checkout.hbs'),
    moment = require('moment'),
    args = require('common/helpers').args;


export const meta = {
    controller: "council/orders/complete",
    match_method: "path",
    check: [
        "^council\/orders\/[A-Za-z0-9.@_%+-]{36}\/complete$"
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
        orderId = args(2);
    request.get({url: "/v1/orders/" + orderId + "/?expand=true"})
        .done(function(response){
            var results = response.products,
                time = moment().format("h:mm a");
            for (var product in results) {
                if (results.hasOwnProperty(product)) {
                    results[product].information.object_uuid = results[product].id;
                    results[product].information.time = time;
                    giftContainer.append(
                        individualCheckoutGiftTemplate(
                            {"product": results[product].information}));
                }
            }
        });
    $("#js-submit-completed").on("click", function(e){
        e.preventDefault();
        var orderId = args(2);
        request.post({
            url: "/v1/orders/" + orderId + "/complete_order/",
            data: JSON.stringify({tracking_url: $("#js-tracking-url").val()})
        })
            .done(function(response) {
                console.log(response);
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