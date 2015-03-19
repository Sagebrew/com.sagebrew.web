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
                group: 'ssn_wrapper',
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
                group: 'bank_account_wrapper',
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
            account_name :{
                group: 'account_name_wrapper',
                validators: {
                    notEmpty: {
                        message: "Account Name must not be empty"
                    },
                    stringLength: {
                        max: 200,
                        message: "Account Name must not be longer than 200 characters"
                    }
                }
            },
            routing_number: {
                group: 'routing_number_wrapper',
                validators: {
                    notEmpty: {
                        message: "Routing Number must not be empty"
                    },
                    stringLength: {
                        max: 100,
                        message: "Routing number must not be longer than 100 characters"
                    }
                }
            },
            credit_card: {
                group: 'credit_card_wrapper',
                validators: {
                    creditCard: {
                        message: "Must be a valid credit card layout"
                    }
                }
            },
            cvv: {
                groupd: 'cvv_wrapper',
                validators: {
                    cvv: {
                        creditCardField: "credit_card",
                        message: "The CVV number is not valid"
                    }
                }
            },
            office: {
                group: 'office_wrapper',
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
                group: 'district_wrapper',
                validators: {
                    stringLength: {
                        max: 3,
                        message: "District must not be longer than 3 characters"
                    }
                }
            },
            seat_number: {
                group: 'seat_number_wrapper',
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
                group: 'gov_email_wrapper',
                validators: {
                    notEmpty: {
                        message: "Gov Email is required"
                    },
                    stringLength: {
                        max: 200,
                        message: "Gov Email must not be longer than 200 characters"
                    }
                }
            },
            gov_phone: {
                group: 'gov_phone_wrapper',
                validators: {
                    notEmpty: {
                        message: "Gov Phone is required"
                    },
                    stringLength: {
                        max: 15,
                        message: "Gov Phone must not be longer than 15 characters"
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