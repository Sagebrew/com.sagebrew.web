/*global $, jQuery, ajaxSecurity, errorDisplay, Stripe, StripeCheckout*/
$(document).ready(function () {
    var handler = StripeCheckout.configure({
        key: 'pk_test_4VQN9H9N2kXFGMIziWSa09ak',
        image: '/img/documentation/checkout/marketplace.png',
        token: function (token) {
            console.log(token);
        }
    });
    $(".donation-amount-selector").click(function (event) {
        event.preventDefault();
        handler.open({
            name: "Sagebrew LLC",
            description: "Quest Donation",
            amount: $(this).data("amount") * 100
        });
    });
    $("#custom-donation-btn").click(function (event) {
        event.preventDefault();
        handler.open({
            name: "Sagebrew LLC",
            description: "Quest Donation",
            amount: $("#custom-donation").val() * 100
        });
    });
    $(window).on('popstate', function () {
        handler.close();
    });
});