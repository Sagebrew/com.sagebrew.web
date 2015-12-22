var request = require('api').request;

export function addMarkdown(markdownObj, sanatize) {
    var modalFooter = $(".modal-footer"),
        imgURL = $("#img-url"),
        imgUpload = $("#upload_image");
    sanatize = typeof sanatize !== 'undefined' ? sanatize : false;
    markdownObj.pagedownBootstrap({
        "sanatize": sanatize,
        'editor_hooks': [
            {
                'event': 'insertImageDialog',
                'callback': function (callback) {
                    setTimeout(function () {
                        $('#fileModal').modal();
                        $("#insert_image_post").click(function (e) {
                            e.preventDefault();
                            modalFooter.spin('small');
                            if (imgUpload.val().length > 1) {
                                var formdata = new FormData(),
                                    file = $("#upload_image")[0].files[0];
                                formdata.append("file", file);
                                request.post({url: "/v1/upload/", data: formdata,
                                    processData: false, contentType: false})
                                    .done(function (data) {
                                        callback(data.url);
                                        $(".modal-footer").spin(false);
                                        imgUpload.val("");
                                        $("#fileModal").modal('hide');
                                    })
                                    .fail(function () {
                                        callback(null);
                                        modalFooter.spin(false);
                                        imgUpload.val("");
                                        $("#fileModal").modal('hide');
                                        request.errorDisplay(XMLHttpRequest);
                                    });
                            } else {
                                var image = imgURL.val();
                                $(".modal-footer").spin(false);
                                callback(image);
                                imgURL.val("");
                                $("#fileModal").modal('hide');
                            }
                        });
                    }, 0);
                    return true;
                }
            }
        ]
    });
}