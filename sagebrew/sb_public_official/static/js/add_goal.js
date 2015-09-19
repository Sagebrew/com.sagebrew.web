$( document ).ready(function() {
    $(".add_goal").click(function (event) {
        event.preventDefault();

        $.ajax({
            xhrFields: {withCredentials: true},
            type: "GET",
            url: "/reps/goals/",
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function(data){
                $("#goal_added_form").append(data['rendered']);
                enable_post_functionality();
                $(".add_goal").attr('disabled', 'disabled');
            }
        });
    });
});