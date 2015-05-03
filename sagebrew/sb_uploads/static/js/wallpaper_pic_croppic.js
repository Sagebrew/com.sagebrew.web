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
        onAfterImgCrop: function(arg1){
            $.ajax({
                xhrFields: {withCredentials: true},
                type: "PATCH",
                url: "/v1/me/",
                data: JSON.stringify({
                    "wallpaper_pic": arg1.url
                }),
                cache: false,
                contentType: 'application/json',
                processData: false,
                success: function(data){
                    window.location.href = data.url;
                },
                error: function(XMLHttpRequest, textStatus, errorThrown) {
                    $('.alert-dismissible').show();
                }
            });
        },
        onError: function(errormsg) {
            alert(errormsg);
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
            $("#cropWallpaperPictureEyecandy").append('<img id="wallpaper_pic" class="wallpaper_profile" src="' + initial_image + '">');
        },
        loaderHtml:'<div class="loader bubblingG"><span id="bubblingG_1"></span><span id="bubblingG_2"></span><span id="bubblingG_3"></span></div> '
    };
    var cropContainerEyecandy = new Croppic('cropWallpaperPictureEyecandy', croppicContainerEyecandyOptions);
});
