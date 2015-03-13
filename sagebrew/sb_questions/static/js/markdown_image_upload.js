$(document).ready(function () {
    editor.hooks.set("insertImageDialog", function (callback) {
        setTimeout(function ()
        {
               $('#fileModal').modal();
               $("#insert_image_post").click(function(e) {
                  e.preventDefault();
                  if($(".upload-photo").length>0)
                 {
                    var images;
                    $(".upload-photo").each(function(){
                    images = "" + ($(this).filter("[src]").attr("src"));
                  });
                 callback(images);
               //$('#upload_photo').fileupload();
                }
               else {
                  var image=$("#img-url").val();
                  callback(image);
                }
              $("#fileModal").modal('hide');
            });
         }, 0);
         return true; // tell the editor that we'll take care of getting the image url
         });
    editor.run();
});