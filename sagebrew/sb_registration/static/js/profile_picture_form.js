$( document ).ready(function() {

    $("input#profile_pic_upload").change(function () {
        $("#myModal").modal("show");
        var existingdiv1 = document.getElementById( "sb_profile_photo" );
        $("#sb_modal_content").append(existingdiv1);
        $("#sb_save").show();
        console.log(existingdiv1);
        });

    $( "#image_uploaded" ).on("mouseenter", "img", function() {
        $("img").Jcrop({
           aspectRatio: 150/150,
           bgColor: '#26424a',
           bgOpacity: 0.4,
        });
    });
});

/*
    $("#close").change(function () {
        var existingdiv2 = document.getElementById( "sb_photo_parent" );
        $("#sb_profile_photo").append(existingdiv2);
    });
*/