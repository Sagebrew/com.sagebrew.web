var request = require('api').request;

export const meta = {
    controller: "registration/confirm_email",
    match_method: "path",
    check: [
       "^registration/signup/confirm"
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
        .on('click', '#confirmation-email', function (event) {
            event.preventDefault();
            var greyOut = document.getElementById('sb-greyout-page');
            greyOut.classList.remove('sb_hidden');
            request.post({url: "/v1/me/resend_verification/"})
                .done(function() {
                    greyOut.classList.add('sb_hidden');
                    document.getElementById('confirmation-email').classList.add('sb_hidden');
                    var sentEmail = document.getElementsByClassName('confirmation-email-sent');
                    sentEmail[0].classList.remove('sb_hidden');
                    sentEmail[1].classList.remove('sb_hidden');
                });
        });
}

/**
 * Post Load
 */
export function postload() {
    //
    // Intercom Tracking
}