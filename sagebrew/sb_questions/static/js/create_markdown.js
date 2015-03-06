$(document).ready(function () {
	var question_pagedown = $("textarea#question_content_id").pagedownBootstrap({
        "sanatize": false,
        'editor_hooks': [
                {
                    'event': 'insertImageDialog',
                    'callback': function (callback) {
                        alert("Please click okay to start scanning your brain...");
                        setTimeout(function () {
                            var prompt = "We have detected that you like cats. Do you want to insert an image of a cat?";
                            if (confirm(prompt))
                                callback("http://icanhascheezburger.files.wordpress.com/2007/06/schrodingers-lolcat1.jpg")
                            else
                                callback(null);
                        }, 2000);
                        return true; // tell the editor that we'll take care of getting the image url
                    }
                }
            ]
    });
    var solution_pagedown = $("textarea#answer_content_id").pagedownBootstrap();
});
