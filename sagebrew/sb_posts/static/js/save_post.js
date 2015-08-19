/*global $, jQuery, guid, enableSinglePostFunctionality, errorDisplay, enableExpandPostImage*/
$(document).ready(function () {
    "use strict";
    // This function hits the Post API and saves off a given post from a user
    $(".post-action").click(function (event) {
        $("#sb_btn_post").attr("disabled", "disabled");
        var jsImageWrapper = $("#js-image-wrapper"),
            images,
            imageIds = [],
            postInput = $("#post_input_id"),
            content = postInput.val(),
            regExp = /\b((?:[a-z][\w-]+:(?:|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4})(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))/gi,
            regexMatches = content.match(regExp);
        console.log(regexMatches);
        event.preventDefault();
        if (!jsImageWrapper.is(':empty')) {
            images = jsImageWrapper.find('img');
            $.each(images, function (key, value) {
                imageIds.push($(value).data('object_uuid'));
            });
        }
        $.each(regexMatches, function (key, value) {
            $.ajax({
                xhrFields: {withCredentials: true},
                type: "POST",
                url: "/v1/urlcontent/",
                data: JSON.stringify({
                    'object_uuid': guid(),
                    'url': value
                }),
                contentType: "application/json; charset=utf-8",
                dataType: "json",
                success: function (data) {
                    console.log(data);
                },
                error: function (XMLHttpRequest) {
                    $("#sb_btn_post").removeAttr("disabled");
                    errorDisplay(XMLHttpRequest);
                }
            });
        });
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "POST",
            url: "/v1/profiles/" + $('#user_info').data('page_user_username') + "/wall/?html=true",
            data: JSON.stringify({
                'content': $('textarea#post_input_id').val(),
                'images': imageIds
            }),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (data) {
                enableExpandPostImage();
                jsImageWrapper.empty();
                jsImageWrapper.hide();
                postInput.css('margin-bottom', 0);
                $('textarea#post_input_id').val("");
                $("#wall_app").prepend(data.html);
                $("#sb_btn_post").removeAttr("disabled");
                enableSinglePostFunctionality(data.ids);
                var placeHolder = $("#js-wall_temp_message");
                if (placeHolder !== undefined) {
                    placeHolder.remove();
                }
            },
            error: function (XMLHttpRequest) {
                $("#sb_btn_post").removeAttr("disabled");
                errorDisplay(XMLHttpRequest);
            }
        });
    });
});
