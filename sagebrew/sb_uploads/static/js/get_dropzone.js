$( document ).ready(function() {
    $("#dropzone_wrapper").dropzone({
        url: "/upload/images/",
        autoProcessQueue: false
    });
});

