/**
 * @file
 * Dynamically load controllers and whatnot based on urls.
 */
var helpers = require('./common/helpers'),
    settings = require('./settings').settings;

/**
 * Gather all the controllers into an array.
 * This is some magical browserify plugin, you can't actually do this out of the box.
 */
var ctrlHash = require('./controller/*/controller.js', {mode: 'hash'});

//
// Define all the controllers.
var controller_map = [
    {
        controller: "global",
        match_method: true,
        check: true
    },
    {
        controller: "user-anon",
        match_method: "user",
        check: "anon"
    },
    {
        controller: "user-auth",
        match_method: "user",
        check: "auth"
    },
    {
        controller: "section-profile",
        match_method: "path",
        check: "^user"
    },
    {
        controller: "page-signup",
        match_method: "path",
        check: "^$"
    },
    {
        controller: "section-conversation-manage",
        match_method: "path",
        check: "^conversations\/questions\/([A-Za-z0-9.@_%+-]{36})\/edit"
    },
    {
        controller: "section-conversation-manage",
        match_method: "path",
        check: "^conversations/submit_question"
    },
    {
        controller: "section-conversation",
        match_method: "path",
        check: "^conversations\/([A-Za-z0-9.@_%+-]{36})\/"
    },
    {
        controller: "registration",
        match_method: "path",
        check: "^registration/interests"
    },
    {
        controller: "registration",
        match_method: "path",
        check: "^registration/profile_information"
    },
    {
        controller: "registration",
        match_method: "path",
        check: "^registration/profile_picture"
    }
];

/**
 * @param match_method
 * @param check
 */
function matchController(match_method, check) {
    var path = helpers.args().join("/");
    switch(match_method) {
        case true:
            return true;
        case 'user': //Need to output app settings in python for this.
            if(settings.user.type && settings.user.type === check) {
                return true;
            }
            return false;
        case 'path':
            var match = path.match(check);
            return match;

    }
}

function finder() {
    var load = [];
    for (var key in controller_map) {
        if (controller_map.hasOwnProperty(key)) {
            var controller = controller_map[key];
            if (matchController(controller.match_method, controller.check)) {
                load.push(controller.controller);
            }
        }
    }
    return load;
}

export function controllers() {
    var found = finder();
    var loaded = [];
    if (found.length) {
        loaded = found.map(function(key){
            return ctrlHash[key+"/controller"];
        });
    }
    return loaded;
}

