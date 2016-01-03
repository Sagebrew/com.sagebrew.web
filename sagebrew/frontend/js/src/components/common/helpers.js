/**
 * @file
 * Helper functions that aren't global.
 */

var settings = require('./../settings').settings;

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
    while ((el = el.parentElement) && !el.classList.contains(cls));
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
