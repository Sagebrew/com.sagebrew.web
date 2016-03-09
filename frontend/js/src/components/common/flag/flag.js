var Handlebars = require('handlebars'),
    createFlagTemplate = require('./templates/create_flag.hbs');


export function flag() {
    Handlebars.registerPartial('create_flag', createFlagTemplate);
    var $app = $(".app-sb");
    $app
        .on('initialize', '.js-comment-load', function (event) {
            console.log('here')
            var parentId = this.dataset.parent_id;
            console.log(parentId);
        })
}