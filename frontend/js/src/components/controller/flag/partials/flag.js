var Handlebars = require('handlebars'),
    createFlagTemplate = require('../templates/create_flag.hbs');


export function load() {
    Handlebars.registerPartial('create_flag', createFlagTemplate);
}