var request = require('api').request,
    uncompletedOrderTemplate = require('controller/council/templates/order.hbs'),
    moment = require('moment');


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
                    var total = data.results[product].total.toString();
                    data.results[product].total = (total.slice(0, total.length-2) +
                        "." + total.slice(total.length - 2));
                }
            }
            orderWrapper.append(
                uncompletedOrderTemplate(
                    {
                        order: data.results,
                        pending_completion: true
                    }));
            $(".order-created").each(function(){
                var $this = $(this),
                    momentTime = moment($this.html()).format("dddd, MMMM Do YYYY, h:mm a");
                $this.html(momentTime);
            });
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