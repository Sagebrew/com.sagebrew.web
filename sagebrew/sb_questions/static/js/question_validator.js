$(document).ready(function(){
    $("#questionInputForm").bootstrapValidator({
        framework: 'bootstrap',
        err: {
            container: '#fname_errors'
        },
        feedbackIcons: {
            valid: 'glyphicon glyphicon-ok',
            validating: 'glyphicon glyphicon-refresh'
        },
        live: 'enabled',
        submitButtons: '.submit_question-action',
        fields: {
            title: {
                group: 'title_input',
                validators: {
                    notEmpty: {
                        message: "Title is required"
                    },
                    stringLength: {
                        min: 15,
                        max: 140,
                        message: "Title must be between 15 and 140 characters long"
                    }
                }
            },
            question_content: {
                group: 'question_content_input',
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
