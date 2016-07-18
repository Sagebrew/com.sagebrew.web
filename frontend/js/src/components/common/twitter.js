var requests = require('api').request;


export function sharing(updateURL) {
    requests.patch({
        url: updateURL,
        data: JSON.stringify({shared_on_twitter: true})
    })
    .done(function() {
       location.reload();
    });
}
