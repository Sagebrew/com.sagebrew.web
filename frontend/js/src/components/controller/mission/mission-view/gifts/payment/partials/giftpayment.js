var helpers = require('common/helpers'),
    request = require('api').request;


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
