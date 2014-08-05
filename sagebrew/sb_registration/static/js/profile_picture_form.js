$( document ).ready(function() {
    var existingdiv1 = document.getElementById( "sb_profile_photo" );
    $("input#profile_pic_upload").change(function() {
        $("#myModal").modal("show");
        $("#sb_modal_content").append(existingdiv1);
        $("#sb_btn_save").show();
    });
    $("#sb_modal_close").click(function(){
        $("#sb_menu").appendTo("#sb_photo_parent");
        $("#sb_btn_upload").show();
        $("#sb_btn_change").hide();
    });
    $("#sb_btn_remove").click(function(){
        $("#sb_menu").appendTo("#sb_photo_parent");
        $("#sb_btn_upload").show();
        $("#sb_btn_change").hide();
        //$("#sb_modal_content").replaceWith('<div id="sb_modal_test"></div>');
        $(".fileinput .fileinput-exists").replaceWith('')
    });
    $( "#image_uploaded" ).on("mouseenter", "img", function() {
        $("img").Jcrop({
           onSelect: getCoords,
           aspectRatio: 150/150,
           bgColor: '#26424a',
           bgOpacity: 0.4,
           setSelect: [ 60, 70, 540, 330 ],
        });
    });
});
function getCoords (c){
    console.log(c.x);
    console.log(c.y);
    console.log(c.w);
    console.log(c.h);
}
/*
    $("#close").change(function () {
        var existingdiv2 = document.getElementById( "sb_photo_parent" );
        $("#sb_profile_photo").append(existingdiv2);
    });
    $("#sb_close").change(function () {
        var existingdiv2 = document.getElementById( "sb_photo_parent" );
        $("#sb_modal_content").append(existingdiv2);
        $("sb_profile_photo").show();
    });
        $("#sb_close").click(function(){
        $("#sb_menu").appendTo("#sb_photo_parent");
    })
*/