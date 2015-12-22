/**
 * @file
 */
var request = require('api').request,
    helpers = require('common/helpers');

/**
 * Meta.
 */
export const meta = {
    controller: "quest/quest-manage/general",
    match_method: "path",
    check: [
       "^quests\/[A-Za-z0-9.@_%+-]{1,36}\/manage\/general"
    ]
};


/**
 * Load.
 */
export function load() {

    var $app = $(".app-sb"),
        questID = helpers.args(1);
    $app
        .on('click', '#submit', function(event) {
            event.preventDefault();
            var data = helpers.getFormData(document.getElementById('socialForm'));
            request.patch({url: "/v1/quests/" + questID + "/",
                data: JSON.stringify(data)
            }).done(function (){
                $.notify({message: "Updated Settings Successfully"}, {type: "success"});
            });
        });
}