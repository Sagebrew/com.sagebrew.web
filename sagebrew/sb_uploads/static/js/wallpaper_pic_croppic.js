$(document).ready(function(){
    var file_name = guid();
    var initial_image = $("#wallpaper_pic").attr('src');
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            ajaxSecurity(xhr, settings)
        }
    });
    var croppicContainerEyecandyOptions = {
        uploadUrl: '/v1/upload/?croppic=true&object_uuid=' + file_name,
        cropUrl:'/v1/upload/' + file_name + '/crop/?resize=true&croppic=true',
        imgEyecandy:false,
        rotateControls: false,
        doubleZoomControls: false,
        zoomFactor: 100,
        onAfterImgCrop: function(arg1){
            var image_url = arg1.url;
            $.ajax({
                xhrFields: {withCredentials: true},
                type: "PATCH",
                url: "/v1/me/",
                data: JSON.stringify({
                    "wallpaper_pic": image_url
                }),
                cache: false,
                contentType: 'application/json',
                processData: false,
                success: function(data){
                    $("#wallpaper_pic").attr("src", image_url);
                    initial_image = image_url;
                },
                error: function(XMLHttpRequest, textStatus, errorThrown) {
                    $('.alert-dismissible').show();
                }
            });
        },
        onError: function(errormsg) {
            var file_size_error = errormsg.responseJSON.file_size;
            var file_format_error = errormsg.responseJSON.file_format;
            if (typeof file_format_error === "undefined" || file_format_error === null) {
                file_format_error = "";
            }
            if (typeof file_size_error === "undefined" || file_size_error === null) {
                file_size_error = "";
            }
            alert(file_size_error + "\n" + file_format_error);
            cropContainerEyecandy.reset();
        },
        onReset: function() {
            $.ajax({
                xhrFields: {withCredentials: true},
                type: "DELETE",
                url: "/v1/upload/" + file_name + "/",
                cache: false,
                processData: false,
                error: function(XMLHttpRequest, textStatus, errorThrown) {
                    $('.alert-dismissible').show();
                }
            });
            $.ajax({
                xhrFields: {withCredentials: true},
                type: "GET",
                url: "/v1/me/",
                cache: false,
                processData: false,
                success: function(data) {
                    $("#cropWallpaperPictureEyecandy").append('<img id="wallpaper_pic" class="wallpaper_profile" src="' + data.wallpaper_pic + '">');
                },
                error: function(XMLHttpRequest, textStatus, errorThrown) {
                    $('.alert-dismissible').show();
                }
            });

        },
        loaderHtml:'<div class="loader bubblingG"><span id="bubblingG_1"></span><span id="bubblingG_2"></span><span id="bubblingG_3"></span></div> '
    };
    var cropContainerEyecandy = new Croppic('cropWallpaperPictureEyecandy', croppicContainerEyecandyOptions);
});
