/*global $, jQuery, ajaxSecurity, guid, errorDisplay, enableExpandPostImage*/
function getStyle(width, height) {
    var style;
    if (width > height) {
        style = 'style="width:auto; max-height:100%; height:auto;" ';
    } else {
        style = 'style="width:auto; max-width:100%; height:auto;" ';
    }
    return style;
}

function fixDisplay(width, height) {
    var newTop, newLeft;
    if (height > width) {
        newTop = -height + (height / 2) + 49;
        newLeft = 0;
    } else if (width > height) {
        newLeft = -width + (width / 2) + 49;
        newTop = 0;
    } else {
        newLeft = 0;
        newTop = 0;
    }
    return {
        "newLeft": newLeft,
        "newTop": newTop
    };
}

$(document).ready(function () {
    enableExpandPostImage();
    $("#upload_image").on("change", function () {
        var files = $(this).val(),
            buttonSelector = $("#sb_btn_post"),
            jsImageWrapper = $("#js-image-wrapper"),
            postInput = $("#post_input_id");
        jsImageWrapper.show();
        postInput.css('margin-bottom', jsImageWrapper.css('height'));
        buttonSelector.prop('disabled', true);
        jsImageWrapper.spin('small');
        if (files.length > 1) {
            var formdata = new FormData(),
                file = $("#upload_image")[0].files[0];
            formdata.append("file", file);
            $.ajax({
                xhrFields: {withCredentials: true},
                type: "POST",
                url: "/v1/upload/",
                contentType: false,
                processData: false,
                dataType: "json",
                data: formdata,
                success: function (data) {
                    $("#sb_btn_post").attr("disabled", "");
                    if (!postInput.val()) {
                        postInput.val(" ");
                    }
                    jsImageWrapper.spin(false);
                    jsImageWrapper.empty();
                    buttonSelector.prop('disabled', false);
                    jsImageWrapper = $("#js-image-wrapper");
                    $("#upload_image").val("");
                    var styleUpdate = getStyle(data.width, data.height),
                        newImage,
                        styleAddition;
                    jsImageWrapper.append('<div class="post-image-preview"><button class="sb-remove-image-upload js-remove-image" tabindex="-1"><span class="fa fa-times sb-remove-image-icon"></span></button><img id="preview_image' + data.id + '" ' + styleUpdate + 'src="' + data.url + '" data-object_uuid="' + data.id + '"></div>');
                    $(".js-remove-image").off().on('click', function (event) {
                        event.preventDefault();
                        var parentDiv = $(this).parent();
                        parentDiv.remove();
                        if (jsImageWrapper.is(":empty")) {
                            jsImageWrapper.hide();
                            postInput.css('margin-bottom', 0);
                        }
                    });
                    newImage = $("img#preview_image" + data.id);
                    newImage.on('load', function () {
                        styleAddition = fixDisplay($(this).width(), $(this).height());
                        newImage.css({top: styleAddition.newTop, left: styleAddition.newLeft, position: 'absolute'});
                    });
                },
                error: function (XMLHttpRequest) {
                    errorDisplay(XMLHttpRequest);
                }
            });
        }
    });

});

