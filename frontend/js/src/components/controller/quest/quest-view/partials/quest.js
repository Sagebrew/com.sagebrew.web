var missions = require('common/missions'),
    helpers = require('common/helpers'),
    addCroppic = require('common/uploadimage').addCroppic;

export function load() {
    var $app = $(".app-sb"),
        pageUser = helpers.args(1);

    missions.populateMissions($('#js-mission-list'), pageUser, null,
        '<div class="block"><div class="block-content five-padding-bottom"><p>' +
        'Check Back Later For New Missions</p></div></div>', null, null, null, null, "View");
    $app
        .on('click', '.js-position', function (event) {
            event.preventDefault();
            if(this.id === "js-add-mission"){
                window.location.href = "/missions/select/";
            } else {
                window.location.href = "/missions/" + this.dataset.id + "/";
            }
        });
    var croppicContainerOptions = {
        wrapperDivID: "js-croppic-wrapper-div-id",
        imageID: "js-croppic-img-id",
        interfaceUrl: "/v1/quests/" + pageUser + "/",
        uploadProperty: "wallpaper_pic",
        imageClassList: "wallpaper quest-wallpaper",
        afterImgUploadCallback: afterImgUploadCallback,
        afterAfterImgCropCallback: afterAfterImgCropCallback
    };
    addCroppic(croppicContainerOptions);
    $('[data-toggle="tooltip"]').tooltip();
}


function afterImgUploadCallback(){
    var wrapperElement = document.getElementById("js-croppic-wrapper-div-id");
    wrapperElement.classList.add('quest-wallpaper-cropping');
}



function afterAfterImgCropCallback(){
    var wrapperElement = document.getElementById("js-croppic-wrapper-div-id");
    wrapperElement.classList.remove('quest-wallpaper-cropping');
}