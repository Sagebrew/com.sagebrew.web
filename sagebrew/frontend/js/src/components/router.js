/**
 * @file
 * Dynamically load controllers and whatnot based on urls.
 */
var helpers = require('common/helpers'),
    settings = require('settings').settings;

/**
 * Gather all the controllers into an array.
 * This is some magical browserify plugin, you can't actually do this out of the box.
 */
var ctrlHash = require('./controller/**/controller.js', {mode: 'hash'});

/**
 * Gather all the controller meta info.
 */
function controllerMetaInfo() {
    var meta = [];
    for (var ctrl_key in ctrlHash) {
        if (ctrlHash.hasOwnProperty(ctrl_key)) {
            if (ctrlHash[ctrl_key].hasOwnProperty('meta')) {
                meta.push(ctrlHash[ctrl_key].meta);
            }
        }

    }
    return meta;
}
/**
 * @param match_method
 * @param checks
 * TODO: Fix bug:
 *  -- The path generated strips out the trailing slash.
 */
function matchController(match_method, checks) {
    // Support multiple checks.
    if (!(checks instanceof Array)) {
        checks = [checks];
    }

    var path = helpers.args().join("/");
    for (var check_key in checks) {
        if (checks.hasOwnProperty(check_key)) {
            var value = checks[check_key];
            switch(match_method) {
                case true:
                    return true;
                case 'user': //Need to output app settings in python for this.
                    if(settings.user.type && settings.user.type === value) {
                        return true;
                    }
                    break;
                case 'path':
                    var match = path.match(value);
                    if (match !== null) {
                        return true;
                    }
                    break;
            }
        }
    }
    return false;
}

/**
 * Determines if the controllers should be loaded or not.
 * @returns {Array}
 */
function finder() {
    var meta = controllerMetaInfo();
    var load = [];
    for (var key in meta) {
        if (meta.hasOwnProperty(key)) {
            var controller = meta[key];
            if (matchController(controller.match_method, controller.check)) {
                load.push(controller.controller);
            }
        }
    }
    return load;
}

/**
 * Returns all the controllers that should be loaded.
 * @returns {Array}
 */
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