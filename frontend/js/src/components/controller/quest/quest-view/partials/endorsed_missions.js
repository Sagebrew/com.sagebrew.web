var helpers = require('common/helpers'),
    missions = require('common/missions'),
    missionSummaryTemplate = require('controller/quest/quest-view/templates/mission_summary.hbs');

export function load() {
    var questId = helpers.args(1);
    missions.populateEndorsements($("#js-endrorsed-list"), questId, missionSummaryTemplate,
        '<div class="block"><div class="block-content" style="padding-bottom: 5px;"><p>' +
        'Check Back Later For New Endorsements</p></div></div>', 'quests');
}