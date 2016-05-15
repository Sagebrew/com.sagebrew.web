/**
 * @file
 */
var request = require('api').request,
    helpers = require('common/helpers'),
    validation = require('common/validators');

/**
 * Meta.
 */
export const meta = {
    controller: "quest/quest-manage/general",
    match_method: "path",
    check: [
       "^quests\/[A-Za-z0-9.@_%+-]{1,36}\/manage\/general"
    ]
};


/**
 * Load.
 */
export function load() {
    var $app = $(".app-sb"),
        questID = helpers.args(1),
        $about = $("#about"),
        $title = $("#title"),
        $remaining = $("#js-about-char-count"),
        $titleRemaining = $("#js-title-char-count"),
        aboutCharLimit = 128,
        titleCharLimit = 240,
        $imageForm = $("#js-image-upload-form"),
        $previewContainer = $('#js-image-preview'),
        $saveProfilePicButton = $("#js-submit-profile-picture");
    validation.missionManageValidator($('#socialForm'), aboutCharLimit);
    helpers.characterCountRemaining(aboutCharLimit, $about, $remaining);
    helpers.characterCountRemaining(titleCharLimit, $title, $titleRemaining);
    $app
        .on('click', '#submit', function(event) {
            event.preventDefault();
            var data = helpers.getFormData(document.getElementById('socialForm'));
            request.patch({url: "/v1/quests/" + questID + "/",
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
            request.patch({url: "/v1/quests/" + questID + "/",
                data: JSON.stringify({"wallpaper_pic": $previewContainer.attr('src')})
            }).done(function (){
                $.notify({message: "Successfully Updated Wallpaper Picture"}, {type: "success"});
            });
        });
    helpers.setupImageUpload($app, $imageForm, $previewContainer, $saveProfilePicButton, 500, 500, true);
}