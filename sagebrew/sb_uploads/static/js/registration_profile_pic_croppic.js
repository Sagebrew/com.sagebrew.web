/*global $, jQuery, ajaxSecurity, guid, Croppic*/
$(document).ready(function () {
    "use strict";
    var fileName = guid();
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            ajaxSecurity(xhr, settings);
        }
    });
    var croppicContainerEyecandyOptions = {
        uploadUrl: '/v1/upload/?croppic=true&object_uuid=' + fileName,
        cropUrl: '/v1/upload/' + fileName + '/crop/?resize=true&croppic=true',
        imgEyecandy: false,
        rotateControls: false,
        doubleZoomControls: false,
        zoomFactor: 100,
        onAfterImgCrop: function (arg1) {
            $.ajax({
                xhrFields: {withCredentials: true},
                type: "PATCH",
                url: "/v1/me/",
                data: JSON.stringify({
                    "profile_pic": arg1.url
                }),
                cache: false,
                contentType: 'application/json',
                processData: false,
                success: function (data) {
                    window.location.href = data.url;
                },
                error: function () {
                    $('.alert-dismissible').show();
                }
            });
            cropContainerEyecandy.reset();
        },
        onError: function (errormsg) {
            var fileSizeError = errormsg.responseJSON.file_size;
            var fileFormatError = errormsg.responseJSON.file_format;
            // Reasoning behind using typeof comparison http://stackoverflow.com/questions/2778901/javascript-undefined-compare
            if (typeof fileFormatError === "undefined" || fileFormatError === null) {
                fileFormatError = "";
            }
            if (typeof fileSizeError === "undefined" || fileSizeError === null) {
                fileSizeError = "";
            }
            alert(fileSizeError + "\n" + fileFormatError);
        },
        onReset: function () {
            $.ajax({
                xhrFields: {withCredentials: true},
                type: "DELETE",
                url: "/v1/upload/" + fileName + "/",
                cache: false,
                processData: false,
                error: function () {
                    $('.alert-dismissible').show();
                }
            });
        },
        loaderHtml: '<div class="loader bubblingG"><span id="bubblingG_1"></span><span id="bubblingG_2"></span><span id="bubblingG_3"></span></div> '
    };
    var cropContainerEyecandy = new Croppic('cropProfilePictureEyecandy', croppicContainerEyecandyOptions);
});
