$( document ).ready(function() {

    $( "#image_uploaded" ).on("mouseenter", "img", function() {
        $("img").Jcrop({
           aspectRatio: 150/150,
           bgColor: 'white',
           bgOpacity: 0.5,

        });

    });

   $("input#profile_pic_upload").change(function () {
        $('#myModal').modal('show');
    });

});
