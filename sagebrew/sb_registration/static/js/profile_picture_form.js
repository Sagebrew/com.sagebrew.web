$( document ).ready(function() {


    function showCoords(c)
    {
        $('#x').val(c.x);
        $('#y').val(c.y);
        $('#x2').val(c.x2);
        $('#y2').val(c.y2);
        $('#w').val(c.w);
        $('#h').val(c.h);
    };
   // $('#image_preview_id').Jcrop();
   $("#sample_image").on((function() {
       $('#image_preview_id').Jcrop({
           onSelect: showCoords,
           onChange: showCoords
       });
    });

   /* $("input#profile_pic_upload").change(function () {
        $('#myModal').modal('show');
    });
    */
});
