var request = require('api').request;


export function load() {
    var $app = $(".app-sb"),
        missionId = window.location.pathname.match("([A-Za-z0-9.@_%+-]{36})")[0];
    $app.on('click', '#js-endorse-pleb', function(event) {
        event.preventDefault();
        var $this = $(this);
        $this.disabled = true;
        if ($this.text().indexOf("Cancel") > -1){
            request.post({url: "/v1/missions/" + missionId + "/unendorse/", data:JSON.stringify({"endorse_as": "pleb"})})
                .done(function(data){
                    console.log('here');
                    $this.text("Endorse as Me");
                    $this.disabled = false;
                });
        } else {
            request.post({url: "/v1/missions/" + missionId + "/endorse/", data:JSON.stringify({"endorse_as": "pleb"})})
                .done(function(data){
                    console.log('there');
                    $this.text("Cancel My Endorsement");
                    $this.disabled = false;
                });
        }
    });
    $app.on('click', '#js-endorse-quest', function(event) {
        event.preventDefault();
        var $this = $(this);
        $this.disabled = true;
        if ($this.text().indexOf("Cancel") > -1){
            request.post({url: "/v1/missions/" + missionId + "/unendorse/", data:JSON.stringify({"endorse_as": "quest"})})
                .done(function(data){
                    console.log('everywhere');
                    $this.text("Endorse as My Quest");
                    $this.disabled = false;
                });
        } else {
            request.post({url: "/v1/missions/" + missionId + "/endorse/", data:JSON.stringify({"endorse_as": "quest"})})
                .done(function(data){
                    console.log('nowhere');
                    $this.text("Cancel My Quest's Endorsement");
                    $this.disabled = false;
                });
        }
    });
}