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
});