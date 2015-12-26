var addCroppic = require('common/uploadimage').addCroppic,
    helpers = require('common/helpers');
function afterImgUploadCallback(){
    var wrapperElement = document.getElementById("js-croppic-wrapper-div-id");
    wrapperElement.classList.add('mission-wallpaper-cropping');
}

function afterAfterImgCropCallback(){
    var wrapperElement = document.getElementById("js-croppic-wrapper-div-id");
    wrapperElement.classList.remove('mission-wallpaper-cropping');
}


export function load() {
    var missionID = helpers.args(1),
        croppicContainerOptions = {
            wrapperDivID: "js-croppic-wrapper-div-id",
            imageID: "js-croppic-img-id",
            interfaceUrl: "/v1/missions/" + missionID + "/",
            uploadProperty: "wallpaper_pic",
            imageClassList: "wallpaper mission-wallpaper",
            afterImgUploadCallback: afterImgUploadCallback,
            loaderHTML: '<div class="loader quest-wallpaper-loader"></div>',
            afterAfterImgCropCallback: afterAfterImgCropCallback
        };
    var croppicContainer = addCroppic(croppicContainerOptions);
}