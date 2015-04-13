$( document ).ready(function() {
    $("#update_wallpaper_pic").click(function(event){
        event.preventDefault();
        $("#myWallpaperModal").modal("show");
    });
    $("input#wallpaper_image_uploaded").change(function() {
        $("#sb_wallpaper_btn_save").show();
    });
    $("#sb_modal_close").click(function(){
        $("#sb_menu").appendTo("#sb_photo_parent");
        $("#sb_btn_upload").show();
        $(".sb_btn_skip").ccs("margin-top","15px");
        $("#sb_btn_change").hide();
    });
    $("#sb_btn_remove").click(function(){
        $("#sb_menu").appendTo("#sb_photo_parent");
        $("#sb_btn_upload").show();
        $("#sb_btn_change").hide();
        //$("#sb_modal_content").replaceWith('<div id="sb_modal_test"></div>');
        $(".fileinput .fileinput-exists").replaceWith('')
    });
    $( "#wallpaper_image_uploaded" ).on("mouseenter", "img", function() {
        var image_test = $("#wallpaper_image_uploaded").children('img');
        var true_height = image_test.get(0).naturalHeight;
        var true_width = image_test.get(0).naturalWidth;
        /*
        image_test.cropper({
            resizable: false,
            zoomable: false,
            mouseWheelZoom: false,
            touchDragZoom: false,
            rotatable: false,
            dragCrop: false,
            built: function() {
                image_test.cropper('setCropBoxData',
                    {top:0, left:0, width:200, height:200});
            },
            dragend: function() {
                var coords = image_test.cropper('getData');
                console.log(coords);
                console.log(coords.x);
                getCoords(coords);
            }
        });
        */
        var jcrop = image_test.Jcrop({
           trueSize: [true_width, true_height],
           allowResize: false,
           allowSelect: false,
           onSelect: getCoords,
           aspectRatio: 3,
           bgColor: '#26424a',
           bgOpacity: 0.4,
           setSelect: [ 0, 0, 750, 250]
        });
    });
    $("#sb_wallpaper_btn_save").click(function(e){
        e.preventDefault();
        var form = new FormData($('#wallpaperUploadForm')[0]);
        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                ajax_security(xhr, settings)
            }
        });
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "POST",
            url: "/registration/wallpaper_picture_api/",
            data: form,
            cache: false,
            contentType: false,
            processData: false,
            success: function(data){
                $("#myWallpaperModal").modal('hide');
                $("img#wallpaper_pic").attr("src", data['pic_url'])
            }
        });
    });
    function getCoords (c){
        $('#wallpaper_image_x1').val(c.x);
        $('#wallpaper_image_x2').val(c.w);
        $('#wallpaper_image_y1').val(c.y);
        $('#wallpaper_image_y2').val(c.h);
    }
});

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

    $("input#profile_pic_upload").on("mouseenter",function(){
        event.preventDefault();
        $("#sb_modal_content").empty();
        });
        */