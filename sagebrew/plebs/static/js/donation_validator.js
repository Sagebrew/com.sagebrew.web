/*global $, jQuery, ajaxSecurity, errorDisplay*/
$(document).ready(function () {
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