/*global $, jQuery, ajaxSecurity, errorDisplay*/
$(document).ready(function(){
    $("#epicSubmitForm").formValidation({
        framework: 'bootstrap',
        icon: {
            valid: 'glyphicon glyphicon-ok',
            validating: 'glyphicon glyphicon-refresh'
        },
        live: 'enabled',
        button: {
            selector: '#submit_epic'
        },
        fields: {
            epic_content: {
                row: 'sb_epic_input',
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