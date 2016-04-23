var request = require('api').request;

export const meta = {
    controller: "registration/reset_password",
    match_method: "path",
    check: [
       "^password_reset"
    ]
};


/**
 * Init
 */
export function init() {

}

/**
 * Load
 */
export function load() {
    $(".app-sb")
        .on('click', '#js-reset-password', function (event) {
            event.preventDefault();
            var emailAddress = document.getElementById('id_email').value,
                resetBtn = document.getElementById('js-reset-password');
            resetPassword(emailAddress, resetBtn);
            return false;
        })
        .on('keypress', '#id_email', function (event) {
            var emailAddress = document.getElementById('id_email').value,
                resetBtn = document.getElementById('js-reset-password');
            if (event.which === 13 || event.which === 10) {
                resetPassword(emailAddress, resetBtn);
                return false; // handles event.preventDefault(), event.stopPropagation() and returnValue for IE8 and earlier
            }
        });
}

/**
 * Post Load
 */
export function postload() {
    //
    // Intercom Tracking
}


function resetPassword (emailAddress, btn) {
    btn.disabled = true;
    request.post(
        {url: "/v1/reset_password/", data: JSON.stringify({'email': emailAddress})}
    ).done(function () {
            window.location.href = "/password_reset/done/";
    }).fail(function () {
            btn.disabled = false;
    });
}