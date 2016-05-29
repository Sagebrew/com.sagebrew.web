 /*global Intercom*/
/**
 * @file
 */
var request = require('api').request,
    helpers = require('common/helpers');

/**
 * Meta.
 */
export const meta = {
    controller: "mission/registration/onboarding",
    match_method: "path",
    check: [
       "^quests\/[A-Za-z0-9.@_%+-]{1,36}",
        "^missions\/[A-Za-z0-9.@_%+-]{36}\/"
    ],
    does_not_include: ['advocate', 'public_office', 'select', 'account']
};


/**
 * Load.
 */
export function load() {
    var greyPage = document.getElementById('sb-greyout-page'),
        $app = $(".app-sb"),
        missionID = helpers.args(1);
    $('[data-toggle="tooltip"]').tooltip();
    $app
        .on('click', '#take-live-mission', function () {
            event.preventDefault();
            greyPage.classList.remove('sb_hidden');
            Intercom('trackEvent', 'took-mission-live');
            request.patch({
                url: "/v1/missions/" + missionID + "/",
                data: JSON.stringify({
                    active: true
                })
            }).done(function () {
                window.location.reload();
            }).fail(function () {
                greyPage.classList.add('sb_hidden');
            });
        })
        .on('mouseenter', ".js-hover-overlay-activate", function (event) {
            event.preventDefault();
            var $this = $(this),
                overlay = $this.parent().parent().find(".sb-overlay");
            overlay.height($this.height());
            overlay.fadeIn('fast');
        })
        //
        // Remove overlay when mouse leaves card region
        .on('mouseleave', '.sb-overlay', function (event) {
            event.preventDefault();
            $(this).fadeOut('fast');
            $(".sb-profile-not-friend-element-image").removeClass("active");
        })
        .on('click', '#js-close-onboarding', function () {
            event.preventDefault();
            document.getElementById('onboarding').classList.add('sb_hidden');
            return false;
        })
        .on('click', '#js-onboarding-show-all', function () {
            event.preventDefault();
            document.getElementById('js-all-tasks').classList.remove('sb_hidden');
            this.classList.add('sb_hidden');
            return false;
        });

}