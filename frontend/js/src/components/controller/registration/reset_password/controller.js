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
            resetBtn.disabled = true;
            request.post(
                {url: "/v1/reset_password/", data: JSON.stringify({'email': emailAddress})}
            )
                .done(function () {
                    window.location.href = "/password_reset/done/";
                })
                .fail(function () {
                    resetBtn.disabled = false;
                });
            return false;
        });
}

/**
 * Post Load
 */
export function postload() {
    //
    // Intercom Tracking
}