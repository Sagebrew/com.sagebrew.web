$( document ).ready(function() {
    $(".sb_btn_skip").on('click', function(){

    });
    var existingdiv1 = document.getElementById( "sb_profile_photo" );
    $("input#profile_pic_upload").change(function() {
        $("#myModal").modal("show");
        $("#sb_modal_content").append(existingdiv1);
        $("#sb_btn_save").show();
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
    $( "#image_uploaded" ).on("mouseenter", "img", function() {
        var image_test = $("img");
        console.log(image_test);
        var true_height = image_test.get(0).naturalHeight;
        var true_width = image_test.get(0).naturalWidth;
        var jcrop = $("img").Jcrop({
           trueSize: [true_width, true_height],
           allowResize: false,
           allowSelect: false,
           onSelect: getCoords,
           aspectRatio: 1,
           bgColor: '#26424a',
           bgOpacity: 0.4,
           setSelect: [ 0, 0, 200, 200 ]
        });
    });
    $("#sb_btn_save").click(function(e){
        e.preventDefault();
        $(".jcrop-holder").spin("small");
        var form = new FormData($('#uploadForm')[0]);

        $.ajax({
            xhrFields: {withCredentials: true},
            type: "POST",
            url: "/registration/profile_picture_api/",
            data: form,
            cache: false,
            contentType: false,
            processData: false,
            success: function(data){
                $(".jcrop-holder").spin(false);
                window.location.replace(data['url']);
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                $('.alert-dismissible').show();
                    jcrop.setSelect([ 0, 0, 200, 200 ])
            }
        });
    });
    function getCoords (c){
        $('#image_x1').val(c.x);
        $('#image_x2').val(c.w);
        $('#image_y1').val(c.y);
        $('#image_y2').val(c.h);
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