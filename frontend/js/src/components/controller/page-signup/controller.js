 /*global Wistia */
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
    check: [
        "^$",
        "^political$",
        "^advocacy$"
    ]
};

function submitSignup() {
    var submitButton = $("#submit_signup"),
        greyPage = document.getElementById('sb-greyout-page'),
        accountForm = document.getElementById('account-info');
    submitButton.attr("disabled", "disabled");
    greyPage.classList.remove('sb_hidden');
    var accountData = helpers.getSuccessFormData(accountForm);
    delete accountData.password2;
    accountData.date_of_birth = moment(accountData.date_of_birth, "MM/DD/YYYY").format();
    // Convert the url args to what they are for the /missions/{{setup}} url
    // ex. /missions/advocate/
    if(helpers.args(0) === "political") {
        accountData.mission_signup = "public_office";
    } else if (helpers.args(0) === "advocacy") {
        accountData.mission_signup = "advocate";
    }
    requests.post({url: "/v1/profiles/", data: JSON.stringify(accountData)})
        .done(function () {
            greyPage.classList.add('sb_hidden');
            window.location.href = "/registration/signup/confirm/";
        })
        .fail(function () {
            greyPage.classList.add('sb_hidden');
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
    $('#sign-up-redirect').on('click', function () {
        var WH = $(window).height();
        var SH = $('body')[0].scrollHeight;
        $('html, body').stop().animate({scrollTop: SH-WH}, 1000);
    });

    //
    // Background Video
    var vid = document.getElementById("bgvid");
    if(vid !== null) {

        vid.addEventListener('ended', function () {
            // only functional if "loop" is removed
            vid.pause();
            // to capture IE10
            vidFade(vid);
        });
        window.wistiaInit = function() {
            var wistiaVideo = Wistia.api('intro-video');
            wistiaVideo.bind('play', function () {
                vid.pause();
            });
        };
    }


    //
    //Birthday input in signup form.
    $('#birthday').keyup(function (e) {
        birthdayInputManager(this, e);
    });
}

function vidFade(vid) {
    vid.classList.add("stopfade");
}