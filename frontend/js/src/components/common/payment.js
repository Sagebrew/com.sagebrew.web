/*global Stripe, Card*/
var paymentMethodTemplate = require('common/templates/payment_methods.hbs'),
    addPaymentMethodTemplate = require('common/templates/add_payment.hbs'),
    settings = require('settings').settings,
    request = require('api').request,
    paymentMethodKey = "selectedPaymentMethod",
    maxFreeMissionKey = "max_free_missions",
    questAccountKey = "quest_account";


export function listPaymentMethods(endpoint, usePaymentCallback,
                                   responseHandler, cancelRedirect) {
    var $app = $(".app-sb"),
        paymentMethods = document.getElementById('js-list-payment-methods'),
        greyPage = document.getElementById('sb-greyout-page');
    getPaymentMethods(true);
    $app
        .on('click', '#js-add-payment-method', function () {
            paymentMethods.classList.add('sb_hidden');
            addPayment(responseHandler, cancelRedirect);
        })
        .on('click', '#js-use-payment-method', function () {
            usePaymentCallback(localStorage.getItem(paymentMethodKey));
        })
        .on('click', '.js-select-payment', function () {
            greyPage.classList.remove('sb_hidden');
            request.patch({url: endpoint, data: JSON.stringify({
                stripe_default_card_id: this.id
            })})
                .done(function () {
                    getPaymentMethods(true);
                });
        })
        .on('click', '.js-payment-method-option', function (){
            localStorage.setItem(paymentMethodKey, this.id);
        });
}

export function getPaymentMethods(submitPayment, callback) {
    var paymentMethods = document.getElementById('js-list-payment-methods'),
        greyPage = document.getElementById('sb-greyout-page');
    request.get({url: "/v1/me/payment_methods/"})
        .done(function (data) {
            paymentMethods.innerHTML = paymentMethodTemplate({
                cards: data.results,
                submit_payment: submitPayment === true
            });
            $(':radio').radiocheck();
            for(var i=0; i < data.results.length; i++) {
                if (data.results[i].default === true){
                    localStorage.setItem(paymentMethodKey, data.results[i].id);
                }
            }

            paymentMethods.classList.remove('sb_hidden');
            greyPage.classList.add('sb_hidden');
            if(callback !== undefined){
                callback();
            }
        });
}

/**
 * addPayment creates and manages the interface for adding a new form of credit
 * card payment.
 */
export function addPayment(responseHandler, cancelRedirect) {
    var $app = $(".app-sb"),
        paymentForm = document.getElementById('js-add-payment-form'),
        greyPage = document.getElementById('sb-greyout-page'),
        templateContext = {};
    Stripe.setPublishableKey(settings.api.stripe);
    if(localStorage.getItem(questAccountKey) === "upgrade"){
        templateContext = {
            warningMsg: "Please add a credit card to upgrade to a Pro account",
            addWarning: true
        };
    }

    if (localStorage.getItem(maxFreeMissionKey)) {
        templateContext.maxFreeMissions = true;
    }
    paymentForm.innerHTML = addPaymentMethodTemplate(templateContext);

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
            }, function(status, response) {
                var $form = $('#payment-form'),
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
                    responseHandler(status, response);
                }
            });

            // Prevent the form from submitting with the default action
            return false;
        })
        .on('click', '#js-cancel', function(event) {
            event.preventDefault();
            // Check if another function wants to handle where we should be going
            if(cancelRedirect !== undefined && cancelRedirect !== null){
                cancelRedirect();
            } else {
                window.history.back();
            }
        });
}
