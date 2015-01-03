$( document ).ready(function() {
    $('.upload_images').on('click', function(){
        $("div#dropzone").dropzone({url: "/upload/images"});
    });
});

