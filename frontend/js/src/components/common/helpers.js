/**
 * @file
 * Helper functions that aren't global.
 */

var settings = require('./../settings').settings,
    moment = require('moment'),
    requests = require('api').request,
    errorDisplay = require('common/resourcemethods').errorDisplay;

/**
 * Get cookie based by name.
 * @param name
 * @returns {*}
 */
export function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i += 1) {
            var cookie = $.trim(cookies[i]);
            // Does this cookie string begin with the name we want?

            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

export function birthdayInputManager(jsElement, event) {
    var temp;
    if (event.keyCode !== 193 && event.keyCode !== 111) {
        if (event.keyCode !== 8) {
            if ($(jsElement).val().length === 2) {
                $(jsElement).val($(jsElement).val() + "/");
            } else if ($(jsElement).val().length === 5) {
                $(jsElement).val($(jsElement).val() + "/");
            }
        } else {
            temp = $(jsElement).val();
            if ($(jsElement).val().length === 5) {
                $(jsElement).val(temp.substring(0, 4));
            } else if ($(jsElement).val().length === 2) {
                $(jsElement).val(temp.substring(0, 1));
            }
        }
    } else {
        temp = $(jsElement).val();
        var tam = $(jsElement).val().length;
        $(jsElement).val(temp.substring(0, tam-1));
    }
}

/**
 * Check if HTTP method requires CSRF.
 * @param method
 * @returns {boolean}
 */
export function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}


/**
 * Parse URL args.
 * if no arg key is passed, return all the args.
 */
export function args(arg) {
    var select;

    if(typeof arg === 'undefined'){
        select = false;
    } else {
        select = arg;
    }

    var elements = window.location.pathname.split("/");

    for (var item in elements) {
        if (elements.hasOwnProperty(item)) {
            if (!elements[item]) {
                elements.splice(item, 1);
            }
        }
    }
    if ((select || select === 0) && elements[select]) {
        return elements[select];
    }
    else {
        return elements;
    }

}

export function getOrdinal(n) {
   var s=["th","st","nd","rd"],
       v=n%100;
   return n+(s[(v-20)%10]||s[v]||s[0]);
}


/**
 * Get URL Query Paramereters
 * If no url is passed, use current url
 * If no parameter is found return null
 * @returns {string}
 */
export function getQueryParam(paramKey, url) {
    var href = url ? url : window.location.href,
        regex = new RegExp('[?&]' + paramKey + '=([^&#]*)', 'i'),
        string = regex.exec(href);
    return string ? string[1] : null;

}

/**
 * Generate a uuid
 */
export function generateUuid() {
  function s4() {
        return Math.floor((1 + Math.random()) * 0x10000)
            .toString(16)
            .substring(1);
  }

  return s4() + s4() + '-' + s4() + '-' + s4() + '-' +
        s4() + '-' + s4() + s4() + s4();
}

/**
 * Find the first parent element containing a given class of the provided element.
 * Something like:
 * this.closest('.block-container-radio').getElementsByClassName('radio-image-selector');
 * would result in an equivalent output but is not supported by IE
 * @param el - child element
 * @param cls - class we're looking parents for
 * @returns {*}
 */
export function findAncestor (el, cls) {
    // Forcing JSHint to ignore this line as it throws a warning which we
    // cannot resolve: "Expected '{' and instaed saw ';'."
    while ((el = el.parentElement) && !el.classList.contains(cls));  // jshint ignore:line
    return el;
}


export function loadMap(callbackFxn, libraries = "places") {
    "use strict";
    var s = document.createElement("script");
    s.type = "text/javascript";
    s.src  = "https://maps.googleapis.com/maps/api/js?key=" +
        settings.google_maps + "&libraries=" +
        libraries + "&callback=setupAutoSearchMaps";
    window.setupAutoSearchMaps = function(){
        callbackFxn();
    };
    $("head").append(s);
}

export function determineZoom(affectedArea){
    "use strict";
    var zoomLevel = 12;
    if(affectedArea !== null) {
        if((affectedArea.match(/,/g) || []).length === 0){
            zoomLevel = 3;
        } else if ((affectedArea.match(/,/g) || []).length === 1) {
            zoomLevel = 5;
        } else if ((affectedArea.match(/,/g) || []).length === 2) {
            zoomLevel = 12;
        } else if ((affectedArea.match(/,/g) || []).length === 3) {
            zoomLevel = 14;
        } else if ((affectedArea.match(/,/g) || []).length >= 4) {
            zoomLevel = 14;
        }
    }

    return zoomLevel;
}


/**
 * Gather all of the form data associated with the given form. This will build
 * a dictionary using the name associated with the input field as the key and
 * the value provided by the user as the value.
 * @param form
 * @returns {{}}
 */
export function getFormData(form) {
    var data = {};
    for (var i = 0, ii = form.length; i < ii; ++i) {
        var input = form[i];
        // Don't check the value because if the use has entered a value
        // we prepopulate it. So if they remove it we want to set it to
        // an empty string in the backend.
        if (input.name) {
            data[input.name] = input.value;
        }
    }
    return data;
}

/**
 * Gather all of the form data for inputs that have successfully been verified.
 * This function requires that you use a formValidation validator on the form
 * or manage adding has-success manually.
 * @param form
 * @returns {{}}
 */
export function getSuccessFormData(form) {
    var data = {}, parent, input;
    for (var i = 0, ii = form.length; i < ii; ++i) {
        input = form[i];
        // Don't check the value because if the use has entered a value
        // we prepopulate it. So if they remove it we want to set it to
        // an empty string in the backend.
        parent = findAncestor(input, "form-group");
        if (input.name && parent.classList.contains('has-success')) {
          data[input.name] = input.value;
        }
    }
    return data;
}

/**
 * Determine if all the forms in a given array have been filled out
 * successfully.
 * This function requires that you use a formValidation validator on the form
 * or manage adding has-success to validated fields manually. If all forms are
 * fully validated it returns true and if they are not it returns false.
 * @param forms
 * @returns {boolean}
 */
export function verifyContinue(forms) {
    var formData;
    for(var i = 0; i < forms.length; i++){
        formData = getSuccessFormData(forms[i]);
        // Subtract one because for some reason the form length is one longer
        // than the actual amount of inputs.
        if (Object.keys(formData).length !== forms[i].length - 1) {
            return false;
        }
    }
    return true;
}


export function selectAllFields(wrapperDivID) {
    /**
     * This is the function that selects all the fields and deselects all the
     * fields. It works even if fields are already selected or unselected.
     * It also assigns the value to the checkbox of true or false with the
     * end dot notation of .val(!ch).
     */
    $('.toggle-all :checkbox').on('click', function () {
        var $this = $(this);
        var ch = $this.prop('checked');
        $(wrapperDivID).find(':checkbox').radiocheck(!ch ? 'uncheck' : 'check');
    });
    $('[data-toggle="checkbox"]').radiocheck();

    /**
     * Does individual checkboxes and when they are clicked assigns the value
     * associated with the checkbox input to either true or false since
     * it appears bootstrap/flat ui rely on the class of the label to change
     * between checked and a blank string rather then the actual value of the
     * input. This is needed for Django to understand what was selected not
     * for the actual view of the interface. The actual checkbox population in
     * the interface is done automatically by flat ui's js files.
     */
    $('.checkbox-toggle input').each(function (ind, item) {
        $(item).change(function () {
            var label = $("label[for='" + $(item).attr('id') + "']")[1];
            var label_class = $(label).attr('class');
            var label_last = label_class.substr(label_class.lastIndexOf(' ') + 1);

            if (label_last === "checked") {
                $(item).val(true);
            } else {
                $(item).val(false);
            }
        });
    });
}


// Pass the checkbox name to the function
export function getCheckedBoxes(chkboxName) {
    var checkboxes = document.getElementsByName(chkboxName);
    var checkboxesChecked = [];
    // loop over them all
    for (var i=0; i < checkboxes.length; i++) {
        // And stick the checked ones onto an array...
        if (checkboxes[i].checked) {
            checkboxesChecked.push(checkboxes[i].id);
        }
    }
    // Return the array if it is non-empty, or null
    return checkboxesChecked.length > 0 ? checkboxesChecked : [];
}

export function replaceAll(search, replacement) {
    var target = this;
    return target.replace(new RegExp(search, 'g'), replacement);
}


export function humanizeString(toBeHumanized) {
    var fragments = toBeHumanized.split('_');
    for (var i = 0; i < fragments.length; i++) {
        fragments[i] = fragments[i].charAt(0).toUpperCase() + fragments[i].slice(1);
    }
    return fragments.join(' ');
}


/**
 * Convert vote_type into a handlebars usable format since handlebars treats
 * False and None as the same thing. And update the time format to be readable
 * by humans.
 * @param contentList
 * @returns {*}
 */
export function votableContentPrep(contentList) {
    for (var i = 0; i < contentList.length; i ++) {
        if(contentList[i].vote_type === true){
            contentList[i].upvote = true;
        } else if (contentList[i].vote_type === false){
            contentList[i].downvote = true;
        }
        contentList[i].created = moment(contentList[i].created).format("dddd, MMMM Do YYYY, h:mm a");
    }
    return contentList;
}

/**
 * Convert a string into title case.
 */
export function toTitleCase(str)
{
    return str.replace(/\w\S*/g, function(txt){return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();});
}


/**
 * Get remaining character count and display it
 */
export function characterCountRemaining(characterLimit, $selector, $remainingSelector) {
    $remainingSelector.text((characterLimit - $selector.val().length) + " Characters Remaining");
}

/**
 * Setup a file upload area using jquery-file-upload
 */
export function setupImageUpload($app, $formSelector, $previewContainer, $submitButton, imageMinWidth, imageMinHeight, thumbnail){
    var dropArea = $formSelector.children("#drop"),
        $fileInput = $formSelector.children("input#js-file-input"),
        $fileInputButton = $formSelector.children("a#js-file-input-button"),
        $greyOut = $("#sb-greyout-page");

    // This allows for proper styling of a browse files button
    $fileInputButton.on('click', function(event){
        event.preventDefault();
        $fileInput.value = '';
        $previewContainer.attr('src', "");
        $previewContainer.addClass('hidden');
        dropArea.show();

        $fileInput.click();
    });
    // Simulate a click when drag and drop is clicked on
    dropArea.click(function(){
        $fileInput.click();
    });

    $formSelector.fileupload({// This element will accept file drag/drop uploading
        dropZone: dropArea,
        imageMinWidth: imageMinWidth,
        imageMinHeight: imageMinHeight,
        replaceFileInput: false,
        // This function is called when a file is added
        // either via the browse button, or via drag/drop
        add: function (e, data) {
            var img = new Image(),
                allowSubmit = true,
                    uploadFile = data.files[0];
            if (!(/\.(gif|jpg|jpeg|png)$/i).test(uploadFile.name)) {
                $.notify({message: "You must upload an image file. Supported types are jpg, jpeg, png and gif."}, {type: "danger"});
                $greyOut.addClass('sb_hidden');
                return;
            }
            window.URL = window.URL || window.webkitURL;
            $greyOut.removeClass("sb_hidden");
            $previewContainer.addClass('hidden');
            img.onload = function() {
                var widthError = false,
                    heightError = false;
                if (img.naturalWidth < imageMinWidth) {
                    widthError = true;
                }
                if (img.naturalHeight < imageMinHeight) {
                    heightError = true;
                }
                if (widthError) {
                    $.notify({message: "Your image is not wide enough, it must be at least " + imageMinWidth + " pixels wide"}, {type: "danger"});
                    allowSubmit = false;
                }
                if (heightError) {
                    $.notify({message: "Your image is not tall enough, it must be at least " + imageMinHeight + " pixels tall"}, {type: "danger"});
                    allowSubmit = false;
                }
                window.URL.revokeObjectURL(img.src);
                if (allowSubmit) {
                    data.submit();
                } else {
                    $submitButton.addClass('disabled');
                    $submitButton.prop('disabled', true);
                    $greyOut.addClass('sb_hidden');
                }
            };
            img.src = window.URL.createObjectURL(data.files[0]);
        },
        done: function(e, data) {
            var result = data._response.result;
            if (result.height > result.width && thumbnail) {
                requests.post({
                    url: "/v1/upload/" + result.id + "/thumbnail/",
                    data: JSON.stringify({
                        thumbnail_width: imageMinWidth,
                        thumbnail_height: imageMinHeight})
                }).done(function(data) {
                    $("#js-current-image").hide();
                    $previewContainer.attr('src', data.url);
                    $previewContainer.removeClass('hidden');
                    $submitButton.removeClass('disabled');
                    $submitButton.prop('disabled', false);
                    $greyOut.addClass('sb_hidden');
                    dropArea.hide();
                });
            } else {
                $("#js-current-image").hide();
                $previewContainer.attr('src', result.url);
                $previewContainer.removeClass('hidden');
                $submitButton.removeClass('disabled');
                $submitButton.prop('disabled', false);
                $greyOut.addClass('sb_hidden');
                dropArea.hide();
            }

        },
        fail: function(e, data){
            errorDisplay(data.jqXHR);
            $greyOut.addClass('sb_hidden');
        }
    });
}

/*
 * Attempt to go back one step in the browser history, if unable redirect to passed url
 */
export function historyBackFallback(fallbackUrl) {
    fallbackUrl = fallbackUrl || '/';
    var prevPage = window.location.href;

    window.history.go(-1);
    setTimeout(function(){
        if (window.location.href === prevPage)
            {
                window.location.href = fallbackUrl;
            }
    }, 500);
}

/*
 * Set all figcaptions to contenteditable="false"
 */
export function disableFigcapEditing($container) {
    $container.find("figcaption").each(function() {
        var $this = $(this);
        $this.attr('contenteditable', 'false');
    });
}

/*
 * Determine if the browser is currently in private browsing mode
 * Currently we only know about this being an issue in Safari
 */
export function testPrivateBrowsing() {
    var storageTestKey = "storageTest";
    try {
        localStorage.setItem(storageTestKey, true);
        localStorage.removeItem(storageTestKey);
    } catch (e) {
        // Forcing JSHint to ignore this line as it throws a warning we
        // cannot currently resolve: "'DOMException' is not defined."
        if (e.code === DOMException.QUOTA_EXCEEDED_ERR && localStorage.length === 0) {  // jshint ignore:line
            $.notify(
                {message: "We noticed you're browsing in Private Mode, " +
                "some features of the site may not function properly"},
                {type: "warning"});
        }
    }
}

/*
 * When a user clicks off the selection box after typing a location into the
 * Mission creation page, display an error telling them to select
 * something from the dropdown.
 */
export function allowClickErrorMessage(pacInput, clickMessageKey, locationKey, placeChangedKey) {
    function removeBlurMessage() {
        pacInput.off("blur");
    }

    $("body").on('mousedown', function(e) {
        var targetClass = $(e.target).attr('class');
        // Check for class of clicked item to ensure it is not an item in the
        // dropdown menu aka a valid location selection
        if (!targetClass) {
            localStorage.setItem(clickMessageKey, true);
            pacInput.on("blur", function () {
                var inputValue = pacInput.val(),
                    displayClickMessage = localStorage.getItem(clickMessageKey);
                if (inputValue && displayClickMessage && !localStorage.getItem(locationKey) && !localStorage.getItem(placeChangedKey)) {
                    $.notify({message: "Sorry, we couldn't find that location. Please select one from the dropdown menu that appears while typing."},
                        {type: "danger"});
                    localStorage.setItem(clickMessageKey, false);
                }
            });
            window.setTimeout(removeBlurMessage, 100);
        } else if ((targetClass.indexOf("pac-item") === -1 && targetClass.indexOf("pac-icon") === -1)) {
            localStorage.setItem(clickMessageKey, true);
            pacInput.on("blur", function() {
                var inputValue = pacInput.val(),
                    displayClickMessage = localStorage.getItem(clickMessageKey);
                if (inputValue && displayClickMessage && !localStorage.getItem(locationKey) && !localStorage.getItem(placeChangedKey)) {
                    $.notify({message: "Sorry, we couldn't find that location. Please select one from the dropdown menu that appears while typing."},
                        {type: "danger"});
                    localStorage.setItem(clickMessageKey, false);
                }
            });
            window.setTimeout(removeBlurMessage, 100);
        }
    });
}

/*
 * Allow users to hit tab to select the first suggested location in
 * Mission signup instead of only enter.
 */
export function allowTabLocationSelection(input) {
    (function pacSelectFrist(input) {
        var _addEventListener = (input.addEventListener) ? input.addEventListener : input.attachEvent;
        function addEventListenerWrapper(type, listener) {
            if (type === "keydown") {
                var origListener = listener;
                listener = function(event) {
                    var suggestionSelected = $(".pac-item-selected").length > 0;
                    if ((event.which === 13 || event.which === 9) && !suggestionSelected) {
                        var simulatedDownArrow = $.Event("keydown", {keyCode: 40, which: 40});
                        origListener.apply(input, [simulatedDownArrow]);
                    }
                    origListener.apply(input, [event]);
                };
            }
            _addEventListener.apply(input, [type, listener]);
        }

        if (input.addEventListener) {
            input.addEventListener = addEventListenerWrapper;
        }
        else if (input.attachEvent){
            input.attachEvent = addEventListenerWrapper;
        }

    })(input);
}


/*
 * Round up a float value with the format of x.xx
 * This is done in places handling currency amounts so as to avoid losing money
 */
export function currencyRoundUp(cashValue) {
    return Math.ceil(cashValue * 100) / 100;
}