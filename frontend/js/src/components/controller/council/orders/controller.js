var request = require('api').request,
    uncompletedOrderTemplate = require('controller/council/templates/order.hbs'),
    moment = require('moment'),
    args = require('common/helpers').args;


export const meta = {
    controller: "council/orders",
    match_method: "path",
    check: [
        "^council\/orders$"
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
    var orderWrapper = $("#js-order-completion-wrapper");
    request.get({url: "/v1/orders/"})
        .done(function(data){
            for (var product in data.results) {
                if (data.results.hasOwnProperty(product)) {
                    var total = data.results[product].total;
                    data.results[product].total = total / 100.0;
                    data.results[product].created = moment(data.results[product].created).format("dddd, MMMM Do YYYY, h:mm a");
                }
            }
            orderWrapper.append(
                uncompletedOrderTemplate(
                    {
                        order: data.results,
                        pending_completion: true
                    }));
            $('[data-toggle="tooltip"]').tooltip();
        });
    
}

/**
 * Post Load
 */
export function postload() {
    //
    // Intercom Tracking
}