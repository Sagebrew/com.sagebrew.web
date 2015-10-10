/*global $, ajaxSecurity, errorDisplay*/
$(document).ready(function(){
    $("#epicForm").formValidation({
        framework: 'bootstrap',
        icon: {
            valid: 'glyphicon glyphicon-ok',
            validating: 'glyphicon glyphicon-refresh'
        },
        live: 'enabled',
        button: {
            selector: '#submit_epic'
        },
        err: {
            container: "#validation-errors"
        },
        fields: {
            epic_content: {
                row: 'epic-content',
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
    });
});