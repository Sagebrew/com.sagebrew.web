var helpers = require('common/helpers'),
    request = require('api').request;

export function stripeResponseHandler(status, response) {
    var $form = $('#payment-form'),
        questID = helpers.args(1),
        greyPage = document.getElementById('sb-greyout-page');
    request.put({url: "/v1/quests/" + questID + "/", data: JSON.stringify({
        customer_token: response.id
    })})
        .done(function () {
            // If we were previously at the plan upgrade page and didn't have a
            // card on file we redirect here. If the user enters a card we then
            // update the account to paid and redirect to the quest billing page.
            if(localStorage.getItem('quest_account') === "upgrade"){
                localStorage.removeItem('quest_account');
                request.patch({url: "/v1/quests/" + questID + "/", data: JSON.stringify({
                    account_type: "paid"
                })}).done(function () {
                    window.location.href = "/quests/" + questID + "/manage/billing/";
                }).fail(function () {
                    greyPage.classList.add('sb_hidden');
                });
            } else {
                window.location.href = "/quests/" + questID + "/manage/billing/";
            }
        }).fail(function () {
            greyPage.classList.add('sb_hidden');
            $form.find('button').prop('disabled', false);
        });
}

export function questCancelRedirect() {
    window.history.back();
}