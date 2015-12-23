/*global Stripe, Card*/
var templates = require('template_build/templates'),
    helpers = require('common/helpers'),
    settings = require('settings').settings,
    request = require('api').request;

/**
 * Load
 */
export function load() {
    var $app = $(".app-sb"),
        paymentForm = document.getElementById('js-add-payment-form'),
        greyPage = document.getElementById('sb-greyout-page'),
        templateContext = {};
    Stripe.setPublishableKey(settings.api.stripe);
    if(localStorage.getItem("quest_account") === "upgrade"){
        templateContext = {
            warningMsg: "Please add a credit card to upgrade to a Pro account",
            addWarning: true
        };
    }
    paymentForm.innerHTML = templates.add_payment(templateContext);

    new Card({
        form: 'form',
        container: '.card',
        formSelectors: {
            numberInput: 'input#cc-number',
            expiryInput: 'input#cc-exp',
            cvcInput: 'input#cc-cvc',
            nameInput: 'input#name'
        },
        formatting: true,
        messages: {
            validDate: 'valid\ndate',
            monthYear: 'mm/yyyy'
        },

        // Default placeholders for rendered fields - optional
        placeholders: {
            number: '•••• •••• •••• ••••',
            name: 'Full Name',
            expiry: '••/••',
            cvc: '•••'
        },

        // if true, will log helpful messages for setting up Card
        debug: false // optional - default false
    });
    $app
        .on('submit', '#payment-form', function(event) {
            event.preventDefault();
            greyPage.classList.remove('sb_hidden');
            var $form = $(this);

            // Disable the submit button to prevent repeated clicks
            $form.find('button').prop('disabled', true);
            var expiration = $('#cc-exp').val().split("/");
            var exp_month = parseInt(expiration[0]),
                exp_year = parseInt(expiration[1]);
            Stripe.card.createToken({
                name: $('#name').val(),
                number: $('#cc-number').val(),
                cvc: $('#cc-cvc').val(),
                exp_month: exp_month,
                exp_year: exp_year
            }, stripeResponseHandler);

            // Prevent the form from submitting with the default action
            return false;
        })
        .on('click', '#js-cancel', function(event) {
            event.preventDefault();
            window.history.back();
        });
}


function stripeResponseHandler(status, response) {
    var $form = $('#payment-form'),
        questID = helpers.args(1),
        greyPage = document.getElementById('sb-greyout-page');
    if (response.error) {
        var errorMsg = response.error.message;
        if(response.error.message === "You must supply either a card, customer, or bank account to create a token.") {
            errorMsg = "You must supply card information prior to saving.";
        }
        greyPage.classList.add('sb_hidden');
        $form.find('.payment-errors').text(errorMsg);
        $form.find('.payment-errors').removeAttr('hidden');
        $form.find('button').prop('disabled', false);
    } else {
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
            });
    }
}