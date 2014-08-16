$( document ).ready(function() {
    $(".sb_post_menu").hide();
    $("#post_input_id").click(function (){
        $(".sb_post_container").css("height","auto");;
        $(".sb_post").css("max-height", "100px");
        $("#post_input_id").css("height", "100px");
        $(".sb_post_menu").show();
    });
    $(".sb_post_container").mouseleave(function(){
        $(".sb_post_menu").hide();
        $(".sb_post").css("height", "50px");
        $(".sb_post_container").css("padding-bottom","10px")
    })
});