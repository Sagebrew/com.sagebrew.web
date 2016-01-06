export function exportContributions() {
    $("#js-get_donation_csv").click(function (event) {
        event.preventDefault();
        var missionSelector = document.getElementById("mission-select");
        window.location.href = "/v1/missions/" + missionSelector.options[missionSelector.selectedIndex].value + "/donation_data/";
    });
}
