$(document).ready(function () {
	var question_pagedown = $("textarea#question_content_id").pagedownBootstrap({
        "sanatize": false,
        'editor_hooks': [
                {
                    'event': 'insertImageDialog',
                    'callback': function (callback) {
                        console.log("here");
                        console.log($("#fileModal"));
                        setTimeout(function(){
                            $('#fileModal').modal();
                            $("#insert_image_post").click(function(e){
                                e.preventDefault();
                                if($(".upload-photo").length>0){
                                    var images;
                                    $(".upload-photo").each(function(){
                                        images = ""+($(this).filter("[src]").attr("src"));
                                    });
                                    callback(images);
                                    //$("#upload_photo").fileupload();
                                } else {
                                    var image=$("#img-url").val();
                                    callback(image);
                                }
                            })
                        }, 0);
                        console.log("after");
                        return true; // tell the editor that we'll take care of getting the image url
                    }
                }
            ]
    });
    var solution_pagedown = $("textarea#answer_content_id").pagedownBootstrap();
});
