var shareButton = require('share-button');


export function load() {
    console.log('here');
    var shareButtonOptions = {
            networks: {
                facebook: {
                    appId: "abc123"
                }
            }
        };
    new shareButton(shareButtonOptions);
}