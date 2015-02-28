$(document).ready(function(){
    $("#betaSignupForm").bootstrapValidator({
        framework: 'bootstrap',
        err: {
            container: '#fname_errors'
        },
        feedbackIcons: {
            valid: 'glyphicon glyphicon-ok',
            validating: 'glyphicon glyphicon-refresh'
        },
        live: 'enabled',
        submitButtons: '#beta_email_submit',
        fields: {
            content: {
                group: 'email_class',
                validators: {
                    notEmpty: {
                        message: "Content is required"
                    },
                    stringLength: {
                        min: 15,
                        message: "Content must be greater than 15 characters"
                    }
                }
            }
        }
    })
});
