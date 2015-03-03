$(document).ready(function(){
    $("#answerSubmitForm").bootstrapValidator({
        framework: 'bootstrap',
        err: {
            container: '#fname_errors'
        },
        feedbackIcons: {
            valid: 'glyphicon glyphicon-ok',
            validating: 'glyphicon glyphicon-refresh'
        },
        live: 'enabled',
        submitButtons: '#submit_answer',
        fields: {
            answer_content: {
                group: 'sb_answer_input',
                validators: {
                    notEmpty: {
                        message: "Content is required"
                    },
                    stringLength: {
                        min: 15,
                        message: "Content must be at least 15 characters long"
                    }
                }
            }
        }
    })
});