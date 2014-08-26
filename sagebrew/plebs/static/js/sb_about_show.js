$( document ).ready(function(){
    $("#sb_btn_about").click(function(){
        $(".sb_about").show();
        $(".sb_home").hide();
    });
    $("sb_btn_home").click(function(){
       $(".sb_about").hide();
    });
});