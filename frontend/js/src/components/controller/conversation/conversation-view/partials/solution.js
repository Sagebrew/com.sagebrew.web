/* global Autolinker */
var request = require('api').request,
    helpers = require('common/helpers'),
    Handlebars = require('handlebars'),
    settings = require('settings').settings,
    mediumEditor = require('common/mediumeditorhelper').createMediumEditor,
    solutionTemplate = require('../templates/solution.hbs');


export function load () {
    require('plugin/contentloader');
    var $app = $(".app-sb"),
        regExp = /\b((?:https?:(?:|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw))(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’])|(?:[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b(?!@)))/gi,
        editor = mediumEditor(".editable", "Type your Solution here");
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
                parentID = this.dataset.parent_id,
                $form = $(this),
                serialized = editor.serialize(),
                key = Object.keys(serialized)[0],
                regexMatches = serialized[key].value.match(regExp);
            $form.find('button').prop('disabled', true);
            if (settings.profile.privileges.indexOf("comment") > -1 || regexMatches) {

                request.post({
                    url: "/v1/questions/" + parentID + "/solutions/?expand=true",
                    data: JSON.stringify(solutionContent)
                })
                .done(function (data) {
                    var $container = $(".list-container"),
                        firstSolution = $(".first-solution");
                    if (firstSolution !== null) {
                        firstSolution.remove();
                    }
                    data = helpers.votableContentPrep([data])[0];
                    
                    // remove content of editor
                    editor.destroy();
                    $(".editable").val("");
                    editor = mediumEditor(".editable", "Type your Solution here");

                    $container.append(solutionTemplate(data));
                    helpers.disableFigcapEditing($('#js-conversation-solutions'));
                    $('[data-toggle="tooltip"]').tooltip();
                    $form.find('button').prop('disabled', false);
                }).fail(function () {
                    $form.find('button').prop('disabled', false);
                });
            } else {
                $.notify({message: "Please include at least 1 url linking to information to add context or support to your question"}, {type: "danger"});
                $form.find('button').prop('disabled', false);
            }

        })
        .on("sb:populate:solutions", function (event, parentData) {
            var $appSolutions = $(parentData.insertElement),
            $app = $(".app-sb");
            $appSolutions.sb_contentLoader({
                emptyDataMessage: ' ',
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
                        helpers.disableFigcapEditing($('#js-conversation-solutions'));
                        $('[data-toggle="tooltip"]').tooltip();
                        $app.trigger("sb:populate:comments", {
                            id: data.results[i].id,
                            type: data.results[i].type,
                            commentType: "base"
                        });
                    }
                }
            });
        });
}

