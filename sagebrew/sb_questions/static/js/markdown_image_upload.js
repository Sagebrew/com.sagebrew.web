/*global $, jQuery, ajaxSecurity*/
$(document).ready(function () {
    "use strict";
    editor.hooks.set("insertImageDialog", function (callback) {
        setTimeout(function () {
            $('#fileModal').modal();
            $("#insert_image_post").click(function (e) {
                e.preventDefault();
                var image = $("#img-url").val();
                callback(image);
                $("#fileModal").modal('hide');
            });
        }, 0);
        return true; // tell the editor that we'll take care of getting the image url
    });
    editor.run();
});