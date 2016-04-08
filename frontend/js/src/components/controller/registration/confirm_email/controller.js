var request = require('api').request,
    helpers = require('common/helpers');

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
            document.getElementById('confirmation-email').classList.add('sb_hidden');
            var sentEmail = document.getElementsByClassName('confirmation-email-sent');
            sentEmail[0].classList.remove('sb_hidden');
            sentEmail[1].classList.remove('sb_hidden');
            request.get({url: "/registration/email_confirmation/resend/"});
        })
}

/**
 * Post Load
 */
export function postload() {
    //
    // Intercom Tracking
}