$(document).ready(function(){
    $(".sb_vote_div").hide();
    $(".sb_btn_vote_icon").click(function(){
        $(".sb_vote_div").slideDown("2000", function(){

        });
    });
});