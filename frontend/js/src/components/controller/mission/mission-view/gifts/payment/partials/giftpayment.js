var helpers = require('common/helpers'),
    request = require('api').request,
    getPaymentMethods = require('common/payment').getPaymentMethods;

export function stripeResponseHandler(status, response) {
    var greyPage = document.getElementById('sb-greyout-page'),
        $form = $('#payment-form');

    request.patch({url: "/v1/me/", data: JSON.stringify({
        customer_token: response.id
    })})
        .done(function () {
            request.get({url: "/v1/me/payment_methods/"})
                .done(function () {
                    getPaymentMethods(true, function () {
                        document.getElementById('js-add-payment-form').innerHTML = "";
                    });
                });
        }).fail(function () {
            greyPage.classList.add('sb_hidden');
            $form.find('button').prop('disabled', false);
        });
}


export function giftCancelRedirect() {
    var paymentMethods = document.getElementById('js-list-payment-methods'),
        paymentForm = document.getElementById('js-add-payment-form');
    paymentMethods.classList.remove('sb_hidden');
    paymentForm.innerHTML = "";
}

export function usePaymentCallback(paymentID) {
    var donationToID = helpers.args(1),
        donationType = helpers.args(0),
        greyPage = document.getElementById('sb-greyout-page'),
        contributionKey = donationToID + 'contributionAmount',
        subscriptionKey = donationToID + 'subscriptionType',
        paymentMethodKey = "selectedPaymentMethod",
        orderId = localStorage.getItem(donationToID + "_OrderId");
    greyPage.classList.remove('sb_hidden');
    request.put({url: "/v1/orders/" + orderId + "/", data: JSON.stringify({
        payment_method: paymentID || null,
        mission: donationToID
    })})
        .done(function () {
            localStorage.removeItem(contributionKey);
            localStorage.removeItem(subscriptionKey);
            localStorage.removeItem(paymentMethodKey);
            localStorage.removeItem(donationToID + "_OrderId");
            window.location.href = "/" + donationType + "/" + donationToID + "/";
        });
}
