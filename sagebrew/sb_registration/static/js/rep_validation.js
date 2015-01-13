$(document).ready(function(){
    $("#regForm").bootstrapValidator({
        feedbackIcons: {
            valid: 'glyphicon glyphicon-ok',
            invalid: 'glyphicon glyphicon-remove',
            validating: 'glyphicon glyphicon-refresh'
        },
        live: 'enabled',
        submitButtons: 'button.submit_rep',
        fields: {
            ssn: {
                group: 'col-sm-4',
                validators: {
                    notEmpty: {
                        message: "SSN is required"
                    },
                    stringLength: {
                        max: 9,
                        message: "SSN must not be longer than 9 characters"
                    }
                }
            },
            bank_account: {
                group: 'col-sm-4',
                validators: {
                    notEmpty: {
                        message: "Bank Account must not be empty"
                    },
                    stringLength: {
                        max: 100,
                        message: "Bank Account must not be longer than 100 characters"
                    }
                }
            },
            credit_card: {
                group: 'col-sm-8',
                validators: {
                    creditCard: {
                        message: "Must be a valid credit card layout"
                    }
                }
            },
            cvv: {
                groupd: 'col-sm-8',
                validators: {
                    cvv: {
                        creditCardField: "credit_card",
                        message: "The CVV number is not valid"
                    }
                }
            },
            office: {
                group: 'col-sm-8',
                validators: {
                    notEmpty: {
                        message: "Office is required"
                    },
                    stringLength: {
                        max: 100,
                        message: "Office must not be longer than 100 characters"
                    }
                }
            },
            district: {
                group: 'col-sm-8',
                validators: {
                    stringLength: {
                        max: 3,
                        message: "District must not be longer than 3 characters"
                    }
                }
            },
            seat_number: {
                group: 'col-sm-8',
                validators: {
                    notEmpty: {
                        message: "Seat Number is required"
                    },
                    stringLength: {
                        max: 3,
                        message: "Seat Number must not be longer than 3 characters"
                    }
                }
            },
            gov_email: {
                group: 'col-sm-8',
                validators: {
                    notEmpty: {
                        message: "Gov Email is required"
                    },
                    stringLength: {
                        max: 200,
                        message: "Gov Email must not be longer than 200 characters"
                    }
                }
            }
        }
    })
    .on('success.field.fv', function(e, data) {
        if (data.field === 'credit_card') {
            var $icon = data.element.data('fv.icon');
            switch (data.result.type) {
                case 'AMERICAN_EXPRESS':
                    $icon.removeClass().addClass('form-control-feedback fa fa-cc-amex');
                    break;

                case 'DISCOVER':
                    $icon.removeClass().addClass('form-control-feedback fa fa-cc-discover');
                    break;

                case 'MASTERCARD':
                    $icon.removeClass().addClass('form-control-feedback fa fa-cc-mastercard');
                    break;

                case 'VISA':
                    $icon.removeClass().addClass('form-control-feedback fa fa-cc-visa');
                    break;

                default:
                    $icon.removeClass().addClass('form-control-feedback fa fa-credit-card');
                    break;
            }
        }
    })
    .on('err.field.fv', function(e, data) {
        if (data.field === 'credit_card') {
            var $icon = data.element.data('fv.icon');
            $icon.removeClass().addClass('form-control-feedback fa fa-times');
        }
    });
});