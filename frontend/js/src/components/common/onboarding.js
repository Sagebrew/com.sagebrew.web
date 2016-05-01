var settings = require('settings').settings;

export function routeMissionSetupToEpic(data) {
    // Positioned here instead of the backend because we have the current
    // mission's id and slug. So rather than requerying the db for the same
    // data we'll just redirect here.
    localStorage.setItem("recent_mission_id", data.id);
    localStorage.setItem("recent_mission_slug", data.slug)
    if(settings.profile.quest.account_verified !== "unverified") {
        // TODO this needs to be swapped out with actual location of one pager
        window.location.href = "/missions/" + data.id + "/" + data.slug + "/manage/epic/";
    } else {
        window.location.href = "/missions/account/";
    }
}