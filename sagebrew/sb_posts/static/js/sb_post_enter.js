$( document ).ready(function() {

    $("#post_input_id").click(function (){
        $("#sb_post_container").css("height","auto");
        $("#post_input_id").css("height", "100px").css("max-height", "100px");
        $("#sb_post_menu").show();
    });
});