$( document ).ready(function() {
    // This function populates the input field for a post when a user clicks
    // on it. That way it can look like a simple input area and then be expanded
    // to be a textarea for more room to input information.
    $("#post_input_id").click(function (){
        $("#sb_post_container").css("height","auto");
        $("#post_input_id").css("height", "100px").css("max-height", "800px").css("resize", "vertical");
        $("#sb_post_menu").show();
    });
});