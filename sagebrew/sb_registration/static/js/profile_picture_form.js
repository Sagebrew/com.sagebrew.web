$( document ).ready(function() {


    function showCoords(c) {
        $('#x').val(c.x);
        $('#y').val(c.y);
        $('#x2').val(c.x2);
        $('#y2').val(c.y2);
        $('#w').val(c.w);
        $('#h').val(c.h);
    };

    $( "#sample_image" ).on("click", "img", function() {
        console.log("here");
        $("img").Jcrop();
    });
    // $('#image_preview_id').Jcrop();


    /*
     $("input#profile_pic_upload").change(function() {
         $('#image_preview_id').Jcrop({
         onSelect: showCoords,
         onChange: showCoords
         });
    });

   ("input#profile_pic_upload").change(function () {
        $('#myModal').modal('show');
    });
    */
});
