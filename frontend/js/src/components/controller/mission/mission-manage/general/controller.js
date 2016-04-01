var request = require('api').request,
    helpers = require('common/helpers'),
    validators = require('common/validators'),
    garlic = require('drmonty-garlicjs');

export const meta = {
    controller: "mission/mission-manage/general",
    match_method: "path",
    check: [
        "^missions\/[A-Za-z0-9.@_%+-]{36}\/[A-Za-z0-9.@_%+-]{1,140}\/manage\/general"
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
    var $app = $(".app-sb"),
        missionId = window.location.pathname.match("([A-Za-z0-9.@_%+-]{36})")[0],
        socialForm = $("#socialForm"),
        $about = $("#about"),
        $title = $("#title"),
        $titleRemaining = $("#js-title-char-count"),
        $remaining = $("#js-about-char-count"),
        aboutCharLimit = 255,
        titleCharLimit = 240,
        $imageForm = $("#js-image-upload-form"),
        $previewContainer = $('#js-image-preview'),
        $saveProfilePicButton = $("#js-submit-profile-picture");
    validators.missionManageValidator(socialForm, aboutCharLimit);
    socialForm.garlic();
    helpers.characterCountRemaining(aboutCharLimit, $about, $remaining);
    // Handle title not being present in the case of a mission not being focused on a position
    if ($title.length) {
        helpers.characterCountRemaining(titleCharLimit, $title, $titleRemaining);
    }
    $app
        .on('click', '#submit', function(event) {
            event.preventDefault();
            var data = helpers.getFormData(document.getElementById('socialForm'));
            request.patch({url: "/v1/missions/" + missionId + "/",
                data: JSON.stringify(data)
            }).done(function (){
                $.notify({message: "Updated Settings Successfully"}, {type: "success"});
            });
        })
        .on('keyup', '#about', function(){
            helpers.characterCountRemaining(aboutCharLimit, $about, $remaining);
        })
        .on('keyup', '#title', function(){
            helpers.characterCountRemaining(titleCharLimit, $title, $titleRemaining);
        })
        .on('dragover', '#drop', function (event) {
            event.preventDefault();
        })
        .on('click', '#js-submit-profile-picture', function(event) {
            event.preventDefault();
            request.patch({url: "/v1/missions/" + missionId + "/",
                data: JSON.stringify({"wallpaper_pic": $previewContainer.attr('src')})
            }).done(function (){
                $.notify({message: "Successfully Updated Profile Picture"}, {type: "success"});
            });
        });
    helpers.setupImageUpload($app, $imageForm, $previewContainer, $saveProfilePicButton, 600, 600);

}

/**
 * Post Load
 */
export function postload() {
    //
    // Intercom Tracking
}