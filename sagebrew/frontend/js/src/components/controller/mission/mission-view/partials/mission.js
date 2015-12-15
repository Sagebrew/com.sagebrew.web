var request = require('api').request,
    templates = require('template_build/templates'),
    settings = require('settings').settings,
    helpers = require('common/helpers');


export function load() {
    var $app = $(".app-sb"),
        missionList = document.getElementById('js-mission-list'),
        pageUser = helpers.args(1);
}