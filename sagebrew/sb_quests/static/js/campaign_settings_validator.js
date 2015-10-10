/*global $, ajaxSecurity, errorDisplay*/
$(document).ready(function () {
    $("#socialForm").formValidation({
        framework: 'bootstrap',
        icon: {
            valid: 'glyphicon glyphicon-ok',
            validating: 'glyphicon glyphicon-refresh'
        },
        live: 'enabled',
        button: {
            selector: '#submit_settings'
        },
        err: {
            container: "#validation-errors"
        },
        fields: {
            facebook: {
                row: 'epic-content',
                validators: {
                    stringLength: {
                        max: 50,
                        message: "Facebook usernames must not be longer than 50 characters"
                    }
                }
            },
            twitter: {
                row: 'twitter-row',
                validators: {
                    stringLength: {
                        max: 15,
                        message: "Twitter usernames must not be longer than 15 characters"
                    }
                }
            }
        }
    });
});