$( document ).ready(function() {
    $("div#dropzone_wrapper").dropzone({
        url: "/upload/images",
        autoProcessQueue: false
    });
});

