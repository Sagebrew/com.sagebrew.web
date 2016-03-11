var request = require('api').request,
    helpers = require('common/helpers'),
    Handlebars = require('handlebars'),
    moment = require('moment'),
    solutionTemplate = require('../templates/solution.hbs');


export function load () {
    var $app = $(".app-sb");
    Handlebars.registerPartial('solution', solutionTemplate);
    $app
        .on('click', '.js-delete-solution', function() {
            var objectID = this.dataset.id;
            request.remove({
                url: "/v1/solutions/" + objectID + "/"
            }).done(function () {
                document.getElementById("solution-block-" + objectID).remove();
            });
        })
        .on('submit', '#solutionSubmitForm', function (event) {
            event.preventDefault();
            var solutionContent = helpers.getFormData(this),
                parentID = this.dataset.parent_id;
            var $form = $(this);
            $form.find('button').prop('disabled', true);
            request.post({
                url: "/v1/questions/" + parentID + "/solutions/?expand=true",
                data: JSON.stringify(solutionContent)
            }).done(function (data) {
                var $container = $(".list-container");
                data = helpers.votableContentPrep([data])[0];
                $container.append(Autolinker.link(solutionTemplate(data)));
                document.getElementById('wmd-input-0').value = '';
                document.getElementById('wmd-preview-0').innerHTML = '';
                $('[data-toggle="tooltip"]').tooltip();
                $form.find('button').prop('disabled', false);
            }).fail(function () {
                $form.find('button').prop('disabled', false);
            })
        })
        .on("sb:populate:solutions", function (event, parentData) {
            var $appSolutions = $(parentData.insertElement),
            $app = $(".app-sb");
            $appSolutions.sb_contentLoader({
                emptyDataMessage: '<div class="block"><div class="block-content">Be the first to provide a Solution!</div></div>',
                url: "/v1/questions/" + parentData.id + "/solutions/",
                params: {
                    expand: "true"
                },
                dataCallback: function (base_url, params) {
                    var urlParams = $.param(params);
                    var url;
                    if (urlParams) {
                        url = base_url + "?" + urlParams;
                    }
                    else {
                        url = base_url;
                    }
                    return request.get({url: url});
                },
                renderCallback: function ($container, data) {
                    data.results = helpers.votableContentPrep(data.results);
                    for (var i = 0; i < data.results.length; i++) {
                        $container.append(Autolinker.link(solutionTemplate(data.results[i])));
                        $('[data-toggle="tooltip"]').tooltip();
                        $app.trigger("sb:populate:comments", {
                            id: data.results[i].id,
                            type: data.results[i].type,
                            commentType: "base"
                        });
                    }
                }
            })
        });
}

