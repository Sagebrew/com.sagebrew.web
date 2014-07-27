$( document ).ready(function() {

    $( "#image_uploaded" ).on("mouseenter", "img", function() {
        $("img").Jcrop({
           aspectRatio: 150/150,
           bgColor: '#26424a',
           bgOpacity: 0.4,

        });

    });

   $("input#profile_pic_upload").change(function () {
        $('#myModal').modal('show');
    });

});
