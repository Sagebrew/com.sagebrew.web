/**
 * @file
 * Helper functions that aren't global.
 */

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
        if (!elements[item]) {
            elements.splice(item, 1);
        }
    }

    if (select && elements[select]) {
        return elements[select];
    }
    else {
        return elements;
    }

}
