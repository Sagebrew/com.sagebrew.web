/*global $, jQuery, ajaxSecurity, errorDisplay, Stripe, StripeCheckout*/
$(document).ready(function () {
    var donationAmount = 0,
        handler = StripeCheckout.configure({
            key: 'pk_test_4VQN9H9N2kXFGMIziWSa09ak',
            image: $("#stripe_img").data('stripe_image'),
            token: function (token) {
                $.ajax({
                    xhrFields: {withCredentials: true},
                    type: "POST",
                    url: "/v1/donations/sagebrew_donations/",
                    data: JSON.stringify({
                        "amount": donationAmount,
                        "token": token.id
                    }),
                    contentType: "application/json; charset=utf-8",
                    dataType: "json",
                    success: function (data) {
                        $("#donationModal").modal("hide");
                        $.notify("Successfully Created Donation", {type: 'success'});

                    },
                    error: function (XMLHttpRequest, textStatus, errorThrown) {
                        $(this).removeAttr("disabled");
                        errorDisplay(XMLHttpRequest);
                    }
                });
            }
        });
    $(".donation-amount-selector").click(function (event) {
        event.preventDefault();
        donationAmount = $(this).data("amount") * 100;
        handler.open({
            name: "Sagebrew LLC",
            description: "Quest Donation",
            amount: $(this).data("amount") * 100,
            panelLabel: "Pledge {{amount}}"
        });
    });
    $("#custom-donation-btn").click(function (event) {
        event.preventDefault();
        donationAmount = $("#custom-donation").val() * 100;
        handler.open({
            name: "Sagebrew LLC",
            description: "Quest Donation",
            amount: $("#custom-donation").val() * 100,
            panelLabel: "Pledge {{amount}}"
        });
    });
    $(window).on('popstate', function () {
        handler.close();
    });
    $("#customDonation").formValidation({
        framework: 'bootstrap',
        icon: {
            valid: 'glyphicon glyphicon-ok',
            validating: 'glyphicon glyphicon-refresh'
        },
        live: 'enabled',
        button: {
            selector: '#custom-donation-btn'
        },
        fields: {
            donation_amount: {
                validators: {
                    notEmpty: {
                        message: "Donation amount is required"
                    },
                    integer: {
                        message: "Donation amount must be an integer"
                    }
                }
            }
        }
    });
});