var request = require('./../../../api').request;

export function load() {
    var $app = $(".app-sb");
    $app
        .on('click', '#volunteering', function () {
            $("#affiliation-js").show();
        })
        .on('click', '#attend-events', function() {
            $("#affiliation-js").show();
        })
        .on('click', '#submit-js', function(event) {
            event.preventDefault();
            var parties = [],
                interests = [],
                addParties = null,
                addInterests = null;

            if ($("#independent").is(':checked')) { parties.push("independent_party"); }
            if ($("#not-listed").is(':checked')) { parties.push("other"); }
            if ($("#democratic-party").is(':checked')) { parties.push("democratic_party"); }
            if ($("#republican-party").is(':checked')) { parties.push("republican_party"); }
            if ($("#libertarian-party").is(':checked')) { parties.push("libertarian_party"); }
            if ($("#green-party").is(':checked')) { parties.push("green_party"); }
            if ($("#constitution-party").is(':checked')) { parties.push("constitution_party"); }
            if ($("#volunteering").is(':checked')) { interests.push("volunteering"); }
            if ($("#attend-events").is(':checked')) { interests.push("attending_events"); }

            var interestData = JSON.stringify({
                "interests": interests
            });
            var affiliations = JSON.stringify({
               "names": parties
            });
            if(parties.length > 0){
                addParties = request.post({
                    url: "/v1/me/add_parties/",
                    data: affiliations
                });
            }
            if(interestData.length > 0){
                addInterests = request.post({
                    url: "/v1/me/add_interests/",
                    data: interestData
                });
            }
            $.when(addParties, addInterests).done(function () {
                document.interstForm.submit();
            });

        });
}
