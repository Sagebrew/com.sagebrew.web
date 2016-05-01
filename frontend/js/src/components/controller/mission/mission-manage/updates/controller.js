/* global AutoList */
var request = require('api').request,
    markdown = require('common/markdown').addMarkdown,
    validators = require('common/validators'),
    moment = require('moment'),
    updateNewsTemplate = require('controller/section-profile/templates/update_news.hbs'),
    mediumEditor = require('medium-editor');

export const meta = {
    controller: "mission/mission-manage/updates",
    match_method: "path",
    check: [
        "^missions\/[A-Za-z0-9.@_%+-]{36}\/[A-Za-z0-9.@_%+-]{1,140}\/manage\/updates$"
    ]
};


/**
 * Init
 */
export function init() {

}

/**
 * Load
 */
export function load() {
    require('plugin/contentloader');
    require('medium-editor-insert-plugin');
    var $app = $(".app-sb"),
        missionId = window.location.pathname.match("([A-Za-z0-9.@_%+-]{36})")[0],
        $updateWrapper = $("#js-update-wrapper"),
        autolist = new AutoList(),
        editor = new mediumEditor(".editable", {
            buttonLabels: true,
            autoLink: true,
            extensions: {
                'autolist': autolist
            }
        }),
        $title = $("#js-title");
    // Uploading images here via fileUploadOptions because submitting the
    // binary data directly causes browsers to crash if the images are
    // too large/there are too many images
    $(".editable").mediumInsert({
        editor: editor,
        addons: {
            images: {
                fileUploadOptions: {
                    url: "/v1/upload/?editor=true",
                    acceptFileTypes: /(.|\/)(gif|jpe?g|png)$/i,
                    paramName: "file_object"
                }
            },
            embeds: {
                oembedProxy: null
            }
        }
    });
    //markdown($("textarea.markdown-input"));
    $app
        .on('click', '#submit', function(event) {
            event.preventDefault();
            var serialized = editor.serialize(),
                key = Object.keys(serialized);
            request.post({url: "/v1/missions/" + missionId + "/updates/",
                data: JSON.stringify(
                    {
                        'content': serialized[key].value,
                        'title': $title.val(),
                        'about_type': 'mission',
                        'about_id': missionId})
            }).done(function (){
                window.location.reload();
            });

        });
    validators.updateValidator($("#updateForm"));
    if ($updateWrapper !== undefined && $updateWrapper !== null){
        $updateWrapper.sb_contentLoader({
            emptyDataMessage: '',
            url: '/v1/missions/' + missionId + '/updates/',
            params: {
                expand: 'true',
                about_type: 'mission'
            },
            dataCallback: function(base_url, params) {
                var urlParams = $.param(params);
                var url;
                if (urlParams) {
                    url = base_url + "?" + urlParams;
                }
                else {
                    url = base_url;
                }
                return request.get({url:url});

            },
            renderCallback: function($container, data) {
                for (var i = 0; i < data.count; i++) {
                    data.results[i].created = moment(data.results[i].created).format("dddd, MMMM Do YYYY, h:mm a");
                    $container.append(updateNewsTemplate(data.results[i]));
                }
            }
        });
    }
}

/**
 * Post Load
 */
export function postload() {
    //
    // Intercom Tracking
}