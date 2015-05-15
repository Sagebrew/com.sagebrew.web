$(document).ready(function(){
    $("#questionInputForm").formValidation({
        framework: 'bootstrap',
        err: {
            container: '#validation_errors'
        },
        icon: {
            valid: 'glyphicon glyphicon-ok',
            validating: 'glyphicon glyphicon-refresh'
        },
        live: 'enabled',
        button: {
            selector: '.submit_question-action'
        },
        fields: {
            title: {
                row: 'title_input',
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
                row: 'question_content_input',
                validators: {
                    notEmpty: {
                        message: "Content is required"
                    },
                    stringLength: {
                        min: 15,
                        message: "Content must be at least 15 characters long"
                    }
                }
            },
            tag_box: {
                row: 'twitter-typeahead',
                validators: {
                    notEmpty: {
                        message: "Tags are required"
                    }
                }
            }
        }
    });
});
