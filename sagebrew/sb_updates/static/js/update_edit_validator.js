/**
 * Created by tylerwiersing on 7/2/15.
 */
$(document).ready(function () {
    $("#updateForm").formValidation({
        framework: 'bootstrap',
        icon: {
            valid: 'glyphicon glyphicon-ok',
            validating: 'glyphicon glyphicon-refresh'
        },
        live: 'enabled',
        button: {
            selector: '#edit-update'
        },
        err: {
            container: '#validation_errors'
        },
        fields: {
            title: {
                row: 'title_input',
                validators: {
                    notEmpty: {
                        message: "Title is required"
                    },
                    stringLength: {
                        min: 5,
                        max: 140,
                        message: "Title must be between 5 and 140 characters long"
                    }
                }
            },
            content: {
                row: 'update_content_input',
                validators: {
                    notEmpty: {
                        message: "Content is required"
                    }
                }
            }
        }
    });
});