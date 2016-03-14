/**
 * @file
 * For post creation. Giving this a dedicated file since it's on multiple pages.
 *
 */
var request = require('api').request,
    helpers = require('common/helpers'),
    settings = require('settings').settings,
    content = require('common/content'),
    postNewsTemplate = require('../templates/post_news.hbs');



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


/**
 * These should really be called load or something.
 */
export function init () {
    var profile_page_user = helpers.args(1);
    // Newsroom doesn't have username in the url.
    if (profile_page_user === "newsfeed") {
        profile_page_user = settings.user.username;
    }

    //
    // Show full post creation UI when the user clicks on the post input.
    var $appPostCreate = $(".app-post-create");
    $appPostCreate.on('click', '#post_input_id', function () {
        $(".app-post-create").css("height", "auto");
        $("#post_input_id").css("height", "100px").css("max-height", "800px").css("resize", "vertical");
        $("#sb_post_menu").show();
    });

    //
    // Submit post for url expansion.
    $appPostCreate.on('keyup paste', "#post_input_id", function (event) {
        if (event.type === "paste" ||
            (event.type === "keyup" && (event.which === 32 || event.which === 13))) {
            var inputtext = $(this).val();
            setTimeout(function () {
                content.expandContent(inputtext);
            }, 100);

        }
    });

    //
    // Save the post.
    $appPostCreate.on('submit', '.post-create-form', function () {
        var $form = $(this),
            $preview = $(".post-image-preview-container", $(this)),
            $input = $("#post_input_id", $(this));

        $("button", $form).prop("disabled", true);
        $("#sb_btn_post").append($('<div class="loader post-loader"></div>'));

        var parsedText = content.expandContent($input.val()),
            images,
            imageIds = [],
            finalURLs = content.extractUrls($input.val());

        if (!$preview.is(':empty')) {
            images = $preview.find('img');
            $.each(images, function (key, value) {
                imageIds.push($(value).data('object_uuid'));
            });
        }
        parsedText.always(function () {
            request.post({
                url: "/v1/profiles/" + profile_page_user + "/wall/?expand=true",
                data: JSON.stringify({
                    'content': $input.val(),
                    'images': imageIds,
                    'included_urls': finalURLs
                })
            }).done(function (data) {
                $preview.empty();
                $preview.hide();
                $input.css('margin-bottom', 0);
                $input.val("");
                $("#wall_app").prepend(postNewsTemplate(helpers.votableContentPrep([data])[0]));
                var placeHolder = $(".list-empty");
                if (placeHolder !== undefined) {
                    placeHolder.remove();
                }
            }).always(function () {
                $("button", $form).prop("disabled", false);
                $(".loader").remove();
                $("button", $form).removeClass("disabled");
            });
        });
        return false;
    });

    //
    // Form validation
    $(".post-create-form").formValidation({
        framework: 'bootstrap',
        err: {
            container: '#fname_errors'
        },
        icon: {
            valid: 'glyphicon glyphicon-ok',
            validating: 'glyphicon glyphicon-refresh'
        },
        live: 'enabled',
        button: {
            selector: '#sb_btn_post'
        },
        fields: {
            post_input: {
                row: 'post_input_class',
                validators: {
                    notEmpty: {
                        message: "Content is required"
                    }
                }
            }
        }
    }).on('success.form.fv', function(e) {
        e.preventDefault();
    });

    //
    // Handle uploads. TODO: Refactor.
    $("#upload_image").on("change", function () {
        var files = $(this).val(),
            postImageButtom = $(".post-image-btn"),
            buttonSelector = $("#sb_btn_post"),
            jsImageWrapper = $("#js-image-wrapper"),
            postInput = $("#post_input_id");
        jsImageWrapper.show();
        postInput.css('margin-bottom', jsImageWrapper.css('height'));
        buttonSelector.prop('disabled', true);
        jsImageWrapper.append($('<div class="loader post-image-loader"></div>'));
        if (files.length > 1) {
            postImageButtom.prop('disabled', true);
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
                    postImageButtom.prop('disabled', false);
                    $("#sb_btn_post").attr("disabled", "");
                    if (!postInput.val()) {
                        postInput.val(" ");
                    }
                    jsImageWrapper.remove(".loader");
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
                error: function () {
                    jsImageWrapper.remove(".loader");
                }
            });
        }
    });
}


export function load () {
    var $app = $(".app-sb");
    $app
        .on('click', '.js-edit-post', function () {
            $("#js-post-" + this.dataset.id).hide();
            $('#js-edit-container-' + this.dataset.id).show();
        })
        .on('submit', '.js-edit-post-form', function(event) {
            event.preventDefault();
            var update = helpers.getFormData(this),
                objectID = this.dataset.id;
            var $form = $(this);
            $form.find('button').prop('disabled', true);

            request.patch({
                url: "/v1/posts/" + this.dataset.id + "/",
                data: JSON.stringify(update)
            }).done(function (data) {
                $form.find('button').prop('disabled', false);
                document.getElementById("js-post-" + data.id).innerHTML = "<p>" + data.html_content + "</p>";
                $('#js-edit-container-' + objectID).hide();
                $("#js-post-" + objectID).show();
            }).fail(function () {
                $form.find('button').prop('disabled', false);
                $('#js-edit-container-' + objectID).hide();
                $("#js-post-" + objectID).show();
            });
        })
        .on('click', '.js-delete-post', function() {
            var objectID = this.dataset.id;
            request.remove({
                url: "/v1/posts/" + this.dataset.id + "/"
            }).done(function () {
                document.getElementById("post-block-" + objectID).remove();
            });
        });
}