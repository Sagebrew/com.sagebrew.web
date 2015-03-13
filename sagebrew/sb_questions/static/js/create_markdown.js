$(document).ready(function () {
	var question_pagedown = $("textarea#question_content_id").pagedownBootstrap({
        "sanatize": false,
        'editor_hooks': [
                {
                    'event': 'insertImageDialog',
                    'callback': function (callback) {
                        setTimeout(function ()
                        {
                            $('#fileModal').modal();
                            $("#insert_image_post").click(function(e) {
                                e.preventDefault();
                                if ($("#upload_image").val().length > 1) {
                                    var formdata = new FormData();
                                    var file = $("#upload_image")[0].files[0];
                                    formdata.append("myFile", file);
                                    $.ajaxSetup({
                                        beforeSend: function (xhr, settings) {
                                            ajax_security(xhr, settings)
                                        }
                                    });
                                    $.ajax({
                                        xhrFields: {withCredentials: true},
                                        type: "POST",
                                        url: "/upload/images/",
                                        contentType: false,
                                        processData: false,
                                        dataType: "json",
                                        data: formdata,
                                        success: function (data) {
                                            console.log(data['urls']);
                                            callback(data['urls'][0]);
                                            $("#fileModal").modal('hide');
                                            enable_post_functionality();
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
    var solution_pagedown = $("textarea#answer_content_id").pagedownBootstrap();
});
