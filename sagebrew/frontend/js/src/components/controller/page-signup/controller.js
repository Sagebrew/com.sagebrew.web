/* global wistiaJQuery */
/**
 * @file
 * Signup Page... This is actually the homepage for anon users.
 */
var requests = require('api').request,
    birthdayInputManager = require('common/helpers').birthdayInputManager,
    validators = require('common/validators'),
    moment = require('moment'),
    helpers = require('common/helpers');

/**
 * Meta.
 */
export const meta = {
    controller: "page-signup",
    match_method: "path",
    check: "^$"
};


function signupFormValidation() {
    validators.accountValidator($("#account-info"));
}

function submitSignup() {
    var submitButton = $("#submit_signup"),
        accountForm = document.getElementById('account-info');
    submitButton.attr("disabled", "disabled");
    var accountData = helpers.getSuccessFormData(accountForm);
    delete accountData.password2;
    accountData.date_of_birth = moment(accountData.date_of_birth, "MM/DD/YYYY").format();
    requests.post({url: "/v1/profiles/", data: JSON.stringify(accountData)})
        .done(function () {
            window.location.href = "/registration/signup/confirm/";
        })
        .fail(function () {
            $("#submit_signup").removeAttr("disabled");
        });
}

/**
 * Init.
 */
export function init() {

}

/**
 * Load
 */
export function load() {

    //
    // Form Validation
    signupFormValidation();

    //
    // Actual signup form.
    $("#submit_signup").on('click', function (event) {
        event.preventDefault();
        submitSignup();
    });

    $('#signupForm input').keypress(function (e) {
        if (e.which === 10 || e.which === 13) {
            e.preventDefault();
            submitSignup();
        }
    });

    //
    // Background Video
    var vid = document.getElementById("bgvid");
    function vidFade() {
        vid.classList.add("stopfade");
    }

    vid.addEventListener('ended', function () {
        // only functional if "loop" is removed
        vid.pause();
        // to capture IE10
        vidFade();
    });
    wistiaJQuery(document).bind("wistia-popover", function(event, iframe) {
        vid.pause();
        iframe.wistiaApi.time(0).play();
    });
    wistiaJQuery(document).bind("wistia-popover-close", function() {
        vid.play();
    });

    //
    //Birthday input in signup form.
    $('#birthday').keyup(function (e) {
        birthdayInputManager(this, e);
    });
}