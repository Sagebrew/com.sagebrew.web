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
            selector: '#submit_update'
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
                        min: 15,
                        message: "Title must be at least 15 Characters long"
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