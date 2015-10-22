/**
 * @file
 * For post creation. Giving this a dedicated file since it's on multiple pages.
 *
 */
var request = require('./../../../api').request,
    helpers = require('./../../../common/helpers'),
    settings = require('./../../../settings').settings,
    content = require('./../../../common/content');



/**
 * These should really be called load or something.
 */
export function init () {
    var profile_page_user = helpers.args(1);

    //
    // Show full post creation UI when the user clicks on the post input.
    var $appPostCreate = $(".app-post-create");
    $appPostCreate.on('click', '#post_input_id', function (event) {
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
    $appPostCreate.on('submit', '.post-create-form', function (event) {
        var $form = $(this),
            $preview = $(".post-image-preview-container", $(this)),
            $input = $("#post_input_id", $(this));

        $("button", $form).prop("disabled", true);

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
                url: "/v1/profiles/" + profile_page_user + "/wall/?html=true",
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
                $("#wall_app").prepend(data.html);
                enableSinglePostFunctionality(data.ids);
                //
                // We need to update this.
                var placeHolder = $(".list-empty");
                if (placeHolder !== undefined) {
                    placeHolder.remove();
                }
            }).always(function () {
                $("button", $form).prop("disabled", false);
            });
        });
        return false;
    });
}