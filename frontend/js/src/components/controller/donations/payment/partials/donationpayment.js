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
            location.reload(true);
        }).fail(function () {
            greyPage.classList.add('sb_hidden');
            $form.find('button').prop('disabled', false);
        });
}


export function donationCancelRedirect() {
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
        paymentMethodKey = "selectedPaymentMethod";
    greyPage.classList.remove('sb_hidden');
    request.post({url: "/v1/" + donationType + "/" + donationToID + "/donations/", data: JSON.stringify({
        amount: localStorage.getItem(contributionKey),
        payment_method: paymentID || null,
        subscription: localStorage.getItem(subscriptionKey) === "monthly-subscription"
    })})
        .done(function () {
            localStorage.removeItem(contributionKey);
            localStorage.removeItem(subscriptionKey);
            localStorage.removeItem(paymentMethodKey);
            window.location.href = "/" + donationType + "/" + donationToID + "/";
        });
}
