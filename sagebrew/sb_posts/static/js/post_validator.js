$(document).ready(function(){
    $("#postInputForm").formValidation({
        framework: 'bootstrap',
        err: {
            container: '#fname_errors'
        },
        icon: {
            valid: 'glyphicon glyphicon-ok',
            validating: 'glyphicon glyphicon-refresh'
        },
        live: 'enabled',
        button: {
            selector: '#sb_btn_post'
        },
        fields: {
            post_input: {
                row: 'post_input_class',
                validators: {
                    notEmpty: {
                        message: "Content is required"
                    }
                }
            }
        }
    })
});
