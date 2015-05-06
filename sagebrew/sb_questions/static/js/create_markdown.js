$(document).ready(function () {
    var question_pagedown = $("textarea#question_content_id").pagedownBootstrap({
        "sanatize": false,
        'editor_hooks': [
            {
                'event': 'insertImageDialog',
                'callback': function (callback) {
                    setTimeout(function () {
                        $('#fileModal').modal();
                        $("#insert_image_post").click(function (e) {
                            e.preventDefault();
                            $(".modal-footer").spin('small');
                            if ($("#upload_image").val().length > 1) {
                                var formdata = new FormData();
                                var file = $("#upload_image")[0].files[0];
                                formdata.append("file", file);
                                $.ajaxSetup({
                                    beforeSend: function (xhr, settings) {
                                        ajaxSecurity(xhr, settings);
                                    }
                                });
                                $.ajax({
                                    xhrFields: {withCredentials: true},
                                    type: "POST",
                                    url: "/v1/upload/?markdown=true",
                                    contentType: false,
                                    processData: false,
                                    dataType: "json",
                                    data: formdata,
                                    success: function (data) {
                                        callback(data.url);
                                        $(".modal-footer").spin(false);
                                        $("#fileModal").modal('hide');
                                        enable_post_functionality();
                                    },
                                    error: function (XMLHttpRequest, textStatus, errorThrown) {
                                        if (XMLHttpRequest.status === 500) {
                                            $("#server_error").show();
                                        }
                                    }
                                });
                            } else {
                                var image = $("#img-url").val();
                                callback(image);
                                $("#fileModal").modal('hide');
                            }
                        });
                    }, 0);
                    return true;
                }
            }
        ]
    });
    var solution_pagedown = $("textarea#solution_content_id").pagedownBootstrap();
});
