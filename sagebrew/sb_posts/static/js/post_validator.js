$(document).ready(function(){
    $("#postInputForm").bootstrapValidator({
        framework: 'bootstrap',
        err: {
            container: '#fname_errors'
        },
        feedbackIcons: {
            valid: 'glyphicon glyphicon-ok',
            validating: 'glyphicon glyphicon-refresh'
        },
        live: 'enabled',
        submitButtons: '#sb_btn_post',
        fields: {
            post_input: {
                group: 'post_input_class',
                validators: {
                    notEmpty: {
                        message: "Content is required"
                    }
                }
            }
        }
    })
});
