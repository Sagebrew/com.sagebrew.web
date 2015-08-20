/*global $, jQuery, guid, enableSinglePostFunctionality, errorDisplay, enableExpandPostImage*/
$(document).ready(function () {
    "use strict";
    var regExp = /\b((?:https?:(?:|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw))(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’])|(?:[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b(?!@)))/gi,
        finalURLs;
    $("#post_input_id").keyup(function () {
        var inputText = $(this).val(),
            regexMatches = inputText.match(regExp);
        if (regexMatches) {
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
                    }
                });
            });
        }
    });
    // This function hits the Post API and saves off a given post from a user
    $(".post-action").click(function (event) {
        $("#sb_btn_post").attr("disabled", "disabled");
        var jsImageWrapper = $("#js-image-wrapper"),
            images,
            imageIds = [],
            postInput = $("#post_input_id"),
            content = postInput.val();
        finalURLs = content.match(regExp);
        $.unique(finalURLs);
        event.preventDefault();
        console.log(finalURLs);
        if (!jsImageWrapper.is(':empty')) {
            images = jsImageWrapper.find('img');
            $.each(images, function (key, value) {
                imageIds.push($(value).data('object_uuid'));
            });
        }

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
