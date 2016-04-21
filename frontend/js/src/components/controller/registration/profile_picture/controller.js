 /*global Intercom, Croppic*/
var request = require('api').request,
    settings = require('settings').settings,
    helpers = require('common/helpers');

export const meta = {
    controller: "registration/profile_picture",
    match_method: "path",
    check: [
       "^registration/profile_picture"
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
    var fileName = helpers.generateUuid(),
        greyPage = document.getElementById('sb-greyout-page');
    $(".app-sb")
        .on('click', '#skip-step', function () {
            greyPage.classList.remove('sb_hidden');
            Intercom('trackEvent', 'skip-profile-picture-setup');
            if(settings.profile.mission_signup !== null && settings.profile.mission_signup !== undefined && settings.profile.mission_signup !== "undefined"){
                if(settings.profile.quest !== null){
                    greyPage.classList.add('sb_hidden');
                    window.location.href = "/missions/" + settings.profile.mission_signup +"/";
                } else {
                    request.post({url: "/v1/quests/", data: JSON.stringify({tos_acceptance: true})})
                        .done(function () {
                            greyPage.classList.add('sb_hidden');
                            window.location.href = "/missions/" + settings.profile.mission_signup +"/";
                        });
                }
            } else {
                greyPage.classList.add('sb_hidden');
                window.location.href = "/user/newsfeed/";
            }
        });

    var croppicContainerEyecandyOptions = {
        uploadUrl: '/v1/upload/?croppic=true&random=' + fileName,
        cropUrl: '/v1/upload/' + fileName + '/crop/?resize=true&croppic=true',
        imgEyecandy: false,
        rotateControls: false,
        doubleZoomControls: false,
        zoomFactor: 100,
        onAfterImgCrop: function (arg1) {
            greyPage.classList.remove('sb_hidden');
            request.patch({
                url: "/v1/me/",
                data: JSON.stringify({"profile_pic": arg1.url}),
                cache: false,
                processData: false
            }).done(function (data) {
                var metadata = {
                    profile_picture: data.profile_pic,
                    saved_url: arg1.url
                };
                Intercom('trackEvent', 'save-profile-picture', metadata);
                if(data.mission_signup !== null && settings.profile.mission_signup !== undefined){
                    if(data.quest !== null){
                        greyPage.classList.add('sb_hidden');
                        window.location.href = "/missions/" + data.mission_signup +"/";
                    } else {
                        request.post({url: "/v1/quests/", data: JSON.stringify({})})
                            .done(function () {
                                greyPage.classList.add('sb_hidden');
                                window.location.href = "/missions/" + data.mission_signup +"/";
                            });
                    }
                } else {
                    greyPage.classList.add('sb_hidden');
                    window.location.href = "/user/newsfeed/";
                }
            });
            cropContainerEyecandy.reset();
        },
        onError: function (errorMsg) {
            request.errorDisplay(errorMsg);
        },
        onReset: function () {
            request.remove({
                url: "/v1/upload/" + fileName + "/",
                cache: false,
                processData: false
            });
        },
        loaderHtml: '<div class="loader croppic-loader"></div> '
    };
    var cropContainerEyecandy = new Croppic('cropProfilePictureEyecandy', croppicContainerEyecandyOptions);
}

/**
 * Post Load
 */
export function postload() {
    //
    // Intercom Tracking
}