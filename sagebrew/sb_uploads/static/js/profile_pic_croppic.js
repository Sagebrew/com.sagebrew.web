$(document).ready(function(){
    var initial_image = $("#profile_pic").attr('src');
    var file_name = guid();
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
                    "profile_pic": image_url
                }),
                cache: false,
                contentType: 'application/json',
                processData: false,
                success: function(data){
                    $("#profile_pic").attr("src", image_url);
                    initial_image = image_url;
                },
                error: function(XMLHttpRequest, textStatus, errorThrown) {
                    $('.alert-dismissible').show();
                }
            });
        },
        onError: function(errormsg) {
            alert(errormsg.responseJSON.file_size+ "\n" + errormsg.responseJSON.file_format);
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
                    $("#cropProfilePageEyecandy").append('<img id="profile_pic" src="' + data.profile_pic + '">');
                },
                error: function(XMLHttpRequest, textStatus, errorThrown) {
                    $('.alert-dismissible').show();
                }
            });

        },
        loaderHtml:'<div class="loader bubblingG"><span id="bubblingG_1"></span><span id="bubblingG_2"></span><span id="bubblingG_3"></span></div> '
    };
    var cropContainerEyecandy = new Croppic('cropProfilePageEyecandy', croppicContainerEyecandyOptions);
});
