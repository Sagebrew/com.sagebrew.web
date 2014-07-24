$( document ).ready(function() {

    $( "#image_uploaded" ).on("mouseenter", "img", function() {
        $("img").Jcrop();
    });

   $("input#profile_pic_upload").change(function () {
        $('#myModal').modal('show');
    });
});
