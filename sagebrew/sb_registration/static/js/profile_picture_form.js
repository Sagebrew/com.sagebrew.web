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
        var jcrop = $("img").Jcrop({
           allowResize: false,
           allowSelect:false,
           onSelect: getCoords,
           aspectRatio: 200/200,
           bgColor: '#26424a',
           bgOpacity: 0.4,
           setSelect: [ 0, 0, 200, 200 ]
        });
    });
    $("#sb_btn_save").click(function(){
        event.preventDefault();
		$.ajaxSetup({
		    beforeSend: function (xhr, settings) {
                ajax_security(xhr, settings)
            }
		});
	   	$.ajax({
			xhrFields: {withCredentials: true},
			type: "POST",
			url: "/registration/edit_answer_api/",
			data: JSON.stringify({
               'content': $('textarea#' + $(this).data('answer_uuid')).val(),
			   'answer_uuid': $(this).data('answer_uuid'),
               'current_pleb':$(this).data('current_pleb')
			}),
			contentType: "application/json; charset=utf-8",
			dataType: "json",
            success: function (data) {
                alert(data['detail']);
            }
		});
    });
});
function getCoords (c){
    $('#image_x').val(c.x);
    $('#image_x2').val(c.x2);
    $('#image_y').val(c.y);
    $('#image_y2').val(c.y2);
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

    $("input#profile_pic_upload").on("mouseenter",function(){
        event.preventDefault();
        $("#sb_modal_content").empty();
        });
        */