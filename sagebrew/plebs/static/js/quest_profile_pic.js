/*global $, jQuery, guid, Croppic, alert*/
$(document).ready(function () {
    "use strict";
    var fileName = guid(),
        campaignId = $("#campaign_id").data("object_uuid");
    var croppicContainerEyecandyOptions = {
        uploadUrl: '/v1/upload/?croppic=true&object_uuid=' + fileName,
        cropUrl: '/v1/upload/' + fileName + '/crop/?resize=true&croppic=true',
        imgEyecandy: false,
        rotateControls: false,
        doubleZoomControls: false,
        zoomFactor: 100,
        onAfterImgCrop: function (arg1) {
            var imageUrl = arg1.url;
            $.ajax({
                xhrFields: {withCredentials: true},
                type: "PATCH",
                url: "/v1/campaigns/" + campaignId,
                data: JSON.stringify({
                    "profile_pic": imageUrl
                }),
                cache: false,
                contentType: 'application/json',
                processData: false,
                success: function () {
                    cropContainerEyecandy.reset();
                },
                error: function (XMLHttpRequest) {
                    errorDisplay(XMLHttpRequest);
                }
            });
        },
        onError: function (errormsg) {
            var fileSizeError = errormsg.responseJSON.file_size,
                fileFormatError = errormsg.responseJSON.file_format;
            // Reasoning behind using typeof comparison http://stackoverflow.com/questions/2778901/javascript-undefined-compare
            if (typeof fileFormatError === "undefined" || fileFormatError === null) {
                fileFormatError = "";
            }
            if (typeof fileSizeError === "undefined" || fileSizeError === null) {
                fileSizeError = "";
            }
            $.notify({message: fileSizeError + "\n" + fileFormatError},
                {type: 'danger'});
        },
        onReset: function () {
            $.ajax({
                xhrFields: {withCredentials: true},
                type: "DELETE",
                url: "/v1/upload/" + fileName + "/",
                cache: false,
                processData: false,
                error: function (XMLHttpRequest) {
                    errorDisplay(XMLHttpRequest);
                }
            });
            $.ajax({
                xhrFields: {withCredentials: true},
                type: "GET",
                url: "/v1/campaigns/" + campaignId,
                cache: false,
                processData: false,
                success: function (data) {
                    var profileImg = $("#profile_pic");
                    if (profileImg.length === 0) {
                        $(".croppedImg").remove();
                        $("#cropQuestProfilePictureEyecandy").append('<img id="profile_pic" src="' + data.profile_pic + "?" + new Date().getTime() + '">');
                    } else {
                        profileImg.attr('src', data.profile_pic);
                    }
                },
                error: function (XMLHttpRequest) {
                    errorDisplay(XMLHttpRequest);
                }
            });

        },
        loaderHtml: '<div class="loader bubblingG"><span id="bubblingG_1"></span><span id="bubblingG_2"></span><span id="bubblingG_3"></span></div> '
    };
    var cropContainerEyecandy = new Croppic('cropQuestProfilePictureEyecandy', croppicContainerEyecandyOptions);
});