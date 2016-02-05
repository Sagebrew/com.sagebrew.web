/* global Wistia */
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
    validators.accountValidator($("#account-info"));

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
    window.wistiaInit = function() {
        var wistiaVideo = Wistia.api('intro-video');
        wistiaVideo.bind('play', function () {
            vid.pause();
        });
    };

    //
    //Birthday input in signup form.
    $('#birthday').keyup(function (e) {
        birthdayInputManager(this, e);
    });
}