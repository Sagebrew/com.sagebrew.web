/*global $, jQuery, ajaxSecurity, guid, errorDisplay*/
function getStyle(width, height) {
    var style;
    if (height > width) {
        style = 'style="width:auto; max-width:100%; height:auto;" ';
    } else {
        style = 'style="width:auto; max-height:100%; height:auto;" ';
    }
    return style;
}

$(document).ready(function () {
    $("#upload_image").on("change", function () {
        var files = $(this).val(),
            buttonSelector = $("#sb_btn_post"),
            jsImageWrapper = $("#js-image-wrapper"),
            postInput = $("#post_input_id");
        jsImageWrapper.show();
        postInput.css('margin-bottom', jsImageWrapper.css('height'));
        jsImageWrapper.css("width", postInput.css("width"));
        console.log(postInput.css('margin-bottom'));
        buttonSelector.prop('disabled', true);
        buttonSelector.spin('small');
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
                    console.log(data);
                    buttonSelector.spin(false);
                    buttonSelector.prop('disabled', false);
                    jsImageWrapper = $("#js-image-wrapper");
                    $("#upload_image").val("");
                    var styleUpdate = getStyle(data.width, data.height);
                    jsImageWrapper.append('<div class="post-image-preview"><img id="preview_image" ' + styleUpdate + 'src="' + data.url + '" data-object_uuid="' + data.id + '"></div>');
                },
                error: function (XMLHttpRequest) {
                    errorDisplay(XMLHttpRequest);
                }
            });
        }
    });
});

