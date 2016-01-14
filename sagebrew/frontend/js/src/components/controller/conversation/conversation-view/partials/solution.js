var addMarkdown = require('common/markdown').addMarkdown;

export function load () {
    addMarkdown($('#solution_content_id'));
}