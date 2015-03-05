$(document).ready(function () {
	var question_pagedown = $("textarea#question_content_id").pagedownBootstrap();
    var solution_pagedown = $("textarea#answer_content_id").pagedownBootstrap();
    var converter = new Markdown.Converter();
    var editor = new Markdown.Editor(converter);
    console.log(editor);
    editor.hooks.set("insertImageDialog", function(callback){
        setTimeout(function(){
            $("#fileModal").modal();
            $("insert_image_post").click(function(e){
                e.preventDefault();
                if($(".upload-photo").length>0) {
                    var images;
                    $(".upload-photo").each(function () {
                        var images = "" + ($(this).filter("[src]").attr("src"));
                    });
                    callback(images);
                    //$("#upload_photo").fileupload();
                }
                else {
                    var image=$("#img-url").val();
                    callback(image);
                }
                $("#fileModal").modal("hide");
            });
        }, 0);
        return true;
    });
    console.log(editor);
    editor.run();
    console.log(editor);
});
