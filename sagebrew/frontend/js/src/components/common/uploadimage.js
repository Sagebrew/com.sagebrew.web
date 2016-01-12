/* global Croppic*/
var helpers = require('common/helpers'),
    requests = require('api').request;

function createUrl(uuid) {
    return '/v1/upload/?croppic=true&object_uuid=' + uuid;
}

function createCropUrl(uuid) {
    return '/v1/upload/' + uuid + '/crop/?resize=true&croppic=true';
}

function errorCallback(errormsg) {
    var fileSizeError = errormsg.responseJSON.file_size,
        fileFormatError = errormsg.responseJSON.file_format;
    // Reasoning behind using typeof comparison
    // http://stackoverflow.com/questions/2778901/javascript-undefined-compare
    if (typeof fileFormatError === "undefined" || fileFormatError === null) {
        fileFormatError = "";
    }
    if (typeof fileSizeError === "undefined" || fileSizeError === null) {
        fileSizeError = "";
    }
    $.notify({message: fileSizeError + "\n" + fileFormatError},
        {type: 'danger'});
}

function imgUploadCallback() {
    document.getElementById('sb-greyout-page').classList.add('sb_hidden');
}

function beforeImgCropCallback() {
    document.getElementById('sb-greyout-page').classList.remove('sb_hidden');
}

function imgCropCallback(arg1, cropContainer,
                                uploadProperty, interfaceUrl) {
    var uploadDict = {};
    uploadDict[uploadProperty] = arg1.url;
    requests.patch({
        url: interfaceUrl,
        cache: false, processData: false,
        data: JSON.stringify(uploadDict)
        }).done(function () {
            cropContainer.reset();
            document.getElementById('sb-greyout-page').classList.add('sb_hidden');
        }).fail(function () {
            document.getElementById('sb-greyout-page').classList.add('sb_hidden');
        });
}

function resetCallback(wrapperDivID, imageID, imageClassList, uploadProperty,
                        interfaceUrl, fileName) {
    requests.remove({url: "/v1/upload/" + fileName + "/",
        cache: false,
        processsData: false
    }).done(function () {
        requests.get({url: interfaceUrl, cache: false, processsData: false})
            .done(function (data) {
                var imageElement = $(imageID);
                if (imageElement.length === 0) {
                    // This currently isn't used anywhere since croppedImg doesn't exit
                    // in the templates...
                    // Todo may want to just pass a rendered template that manages this
                    // image logic and styling.
                    $(wrapperDivID).append('<img id="' + imageID +
                        '" class="' + imageClassList + '" src="' +
                        data[uploadProperty] + '">');
                } else {
                    imageElement.attr('src', data[uploadProperty]);
                }
            });
        });
    document.getElementById('sb-greyout-page').classList.add('sb_hidden');
}

function croppicOptions(wrapperDivID, imageID, interfaceUrl, uploadProperty,
                        imageClassList, beforeErrorCallback, afterErrorCallback,
                        beforeResetCallback, afterResetCallback, loaderHTML,
                        modal) {
    // uploadProperty is the property we should use to upload the image to the
    // server. Such as wallpaper_pic or profile_pic.
    var fileName = helpers.generateUuid();
    return {
        uploadUrl: createUrl(fileName),
        cropUrl: createCropUrl(fileName),
        imgEyecandy: false,
        rotateControls: false,
        doubleZoomControls: false,
        zoomFactor: 100,
        modal: modal,
        onError: function (errormsg) {
            if(beforeErrorCallback !== null){
                beforeErrorCallback(errormsg);
            }

            errorCallback(errormsg);

            if(afterErrorCallback !== null){
                afterErrorCallback(errormsg);
            }
        },
        onReset: function () {
            if(beforeResetCallback !== null){
                beforeResetCallback(wrapperDivID, imageID, imageClassList, uploadProperty,
                    interfaceUrl, fileName);
            }

            resetCallback(wrapperDivID, imageID, imageClassList, uploadProperty,
                    interfaceUrl, fileName);

            if(afterResetCallback !== null){
                afterResetCallback(wrapperDivID, imageID, imageClassList, uploadProperty,
                    interfaceUrl, fileName);
            }
        },
        onBeforeImgUpload: function () {
            document.getElementById('sb-greyout-page').classList.remove('sb_hidden');
        },
        loaderHtml: loaderHTML
    };
}

function baseOptions() {
    return {
        afterImgUploadCallback: null,
        beforeErrorCallback: null,
        afterErrorCallback: null,
        beforeResetCallback: null,
        afterResetCallback: null,
        beforeAfterImgCropCallback: null,
        afterAfterImgCropCallback: null,
        beforeImgUploadCallback: null,
        beforeBeforeImgCropCallback: null,
        afterBeforeImgCropCallback: null,
        modal: false
    };
}

export function addCroppic(croppicObj) {
    // Wrapper ID is the id associated wtih the div that wraps the image you're
    // adding croppic to.
    // Image ID is the id associated with the image you'd like to replace with
    // the uploaded image.
    var defaultOptions = baseOptions(),
        settings = $.extend({}, defaultOptions, croppicObj),
        croppic = new Croppic(settings.wrapperDivID, croppicOptions(settings.wrapperDivID,
            settings.imageID, settings.interfaceUrl, settings.uploadProperty,
            settings.imageClassList, settings.beforeErrorCallback, settings.afterErrorCallback,
            settings.beforeResetCallback, settings.afterResetCallback, settings.loaderHtml,
            settings.modal));

    if(settings.afterImgUploadCallback !== null) {
        croppic.options.onAfterImgUpload = settings.afterImgUploadCallback;
    }
    croppic.options.onAfterImgUpload = function() {
        if(settings.beforeImgUploadCallback !== null){
            settings.beforeImgUploadCallback();
        }
        imgUploadCallback();

        if(settings.afterImgUploadCallback !== null){
            settings.afterImgUploadCallback();
        }
    };

    croppic.options.onBeforeImgCrop = function() {
        if(settings.beforeBeforeImgCropCallback !== null){
            settings.beforeBeforeImgCropCallback();
        }

        beforeImgCropCallback();

        if(settings.afterBeforeImgCropCallback !== null){
            settings.afterBeforeImgCropCallback();
        }
    };

    croppic.options.onAfterImgCrop = function(arg1) {
        if(settings.beforeAfterImgCropCallback !== null){
            settings.beforeAfterImgCropCallback(arg1, croppic, settings.uploadProperty,
                settings.interfaceUrl, settings.loaderHTML, settings.modal);
        }
        imgCropCallback(arg1, croppic, settings.uploadProperty,
            settings.interfaceUrl);

        if(settings.afterAfterImgCropCallback !== null){
            settings.afterAfterImgCropCallback(arg1, croppic, settings.uploadProperty,
                settings.interfaceUrl);
        }
    };

    return croppic;
}
