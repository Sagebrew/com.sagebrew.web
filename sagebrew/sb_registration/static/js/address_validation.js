$( document ).ready(function() {
    var liveaddress = $.LiveAddress({
        key: "2343579486386328520",
        addresses: [
            {
                street: "#sb_primary",
                street2: "#sb_secondary",
                city: "#sb_city",
                state: "#sb_state",
                zipcode: "#sb_zip"
            }
        ]
    });
    liveaddress.activate();
    liveaddress.on("AddressWasValid", function(event, data, previousHandler){
        $("#id_valid").val("valid");
        $("#id_congressional_district").val(data.response.raw[0].metadata.congressional_district);
        $("#id_latitude").val(data.response.raw[0].metadata.latitude);
        $("#id_longitude").val(data.response.raw[0].metadata.longitude);
        previousHandler(event, data);
    });
    liveaddress.on("AddressWasAmbiguous", function(event, data, previousHandler){
        $("#id_valid").val("ambiguous");
        previousHandler(event, data);
    });
    liveaddress.on("AddressWasInvalid", function(event, data, previousHandler){
        $("#id_valid").val("invalid");
        previousHandler(event, data);
    });
    liveaddress.on("OriginalInputSelected", function(event, data, previousHandler){
        var valid = $("#id_valid").val();
        if (valid === "invalid") {
            $("#id_original_selected").val(true);
        }
        previousHandler(event, data);
    });
});