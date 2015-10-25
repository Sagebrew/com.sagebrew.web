/*global $, guid, Croppic, alert, highcharts*/
function prepareDonationData(donationData) {
    var parsedData = [],
        lifetimeTotalData = [],
        tempTotal = 0,
        startYear,
        parsedShortData = [];
    if (donationData.length > 0) {
        startYear = new Date(donationData[0].created.toLocaleString()).getFullYear();
        $.each(donationData, function (index, value) {
            tempTotal += (value.amount / 100);
            lifetimeTotalData.push(tempTotal);
            var tempDate = new Date(value.created.toLocaleString());
            parsedData.push([Date.UTC(tempDate.getFullYear(), tempDate.getMonth(), tempDate.getDate(), tempDate.getHours(), tempDate.getMinutes(), tempDate.getSeconds()), value.amount / 100]);
            parsedShortData.push([Date.UTC(tempDate.getFullYear(), tempDate.getMonth(), tempDate.getDate()), value.amount / 100]);
        });
    }
    return {
        'individualDonationData': parsedData,
        'lifetimeTotalData': {
            'totalAmount': lifetimeTotalData,
            'startYear': startYear
        },
        'lifetimeTotalDataDateWise': parsedShortData
    };
}

function preparePledgedVoteData(voteData) {
    var parsedVoteData = [],
        myKey,
        tempDate;
    for (myKey in voteData) {
        if (voteData.hasOwnProperty(myKey)) {
            tempDate = new Date(myKey);
            parsedVoteData.push([Date.UTC(tempDate.getFullYear(), tempDate.getMonth(), tempDate.getDate()), voteData[myKey]]);
        }
    }
    return parsedVoteData.reverse();
}

$(document).ready(function () {
    var campaignId = $("#campaign_id").data('object_uuid');
    $.ajax({
        xhrFields: {withCredentials: true},
        type: "GET",
        url: "/v1/campaigns/" + campaignId + "/donations/",
        cache: false,
        processData: false,
        success: function (data) {
            var preparedData = prepareDonationData(data.results);
            // Create a scatter plot showing each donation received as a point
            $("#js-individual_donation_chart").highcharts({
                chart: {
                    type: 'scatter',
                    zoomType: 'xy'
                },
                title: {
                    text: 'Individual Donations Over Time'
                },
                xAxis: {
                    type: 'datetime',
                    dateTimeLabelFormats: { // don't display the dummy year
                        month: '%e. %b',
                        year: '%b'
                    },
                    title: {
                        text: 'Date'
                    }
                },
                yAxis: {
                    title: {
                        text: 'Donation Amount (in $)'
                    },
                    min: 0
                },
                tooltip: {
                    headerFormat: '<b>Donation</b><br>',
                    pointFormat: '{point.x:%e. %b}: ${point.y}'
                },
                plotOptions: {
                    spline: {
                        marker: {
                            enabled: true
                        }
                    }
                },
                series: [
                    {
                        name: 'Lifetime Donations',
                        data: preparedData.individualDonationData
                    }]
            });
        },
        error: function (XMLHttpRequest) {
            errorDisplay(XMLHttpRequest);
        }
    });
    $.ajax({
        xhrFields: {withCredentials: true},
        type: "GET",
        url: "/v1/campaigns/" + campaignId + "/pledged_votes/",
        cache: false,
        processData: false,
        success: function (data) {
            var preparedData = preparePledgedVoteData(data);
            // Create a column chart which shows daily pledge vote amount
            $("#js-pledged_vote_daily_chart").highcharts({
                chart: {
                    type: "column"
                },
                title: {
                    text: "Pledged Votes Over Time"
                },
                xAxis: {
                    type: 'datetime',
                    dateTimeLabelFormats: { // don't display the dummy year
                        month: '%e. %b',
                        year: '%b'
                    },
                    title: {
                        text: 'Date'
                    },
                    minTickInterval: 86400000
                },
                yAxis: {
                    title: {
                        text: 'Pledged Vote Amount'
                    },
                    min: 0,
                    allowDecimals: false
                },
                tooltip: {
                    headerFormat: '<b>Pledge Amount</b><br>',
                    pointFormat: '{point.y} Pledge Vote(s)'
                },
                series: [
                    {
                        name: 'Lifetime Pledged Votes',
                        data: preparedData
                    }]
            });
        },
        error: function (XMLHttpRequest) {
            errorDisplay(XMLHttpRequest);
        }
    });
    $.ajax({
        xhrFields: {withCredentials: true},
        type: "GET",
        url: "/v1/campaigns/" + campaignId + "/",
        cache: false,
        processData: false,
        success: function (data) {
            $("#js-total_donation_amount").append("<h2>$" + data.total_donation_amount / 100 + "</h2>");
            $("#js-total_pledge_vote_amount").append("<h2>" + data.total_pledge_vote_amount + "</h2>");
            var moneyReq = (data.target_goal_donation_requirement - data.total_donation_amount) / 100,
                pledgeReq = data.target_goal_pledge_vote_requirement - data.total_pledge_vote_amount,
                donationPercentage = data.total_donation_amount / data.target_goal_donation_requirement * 100,
                pledgePercentage = data.total_pledge_vote_amount / data.target_goal_pledge_vote_requirement * 100;
            if (moneyReq < 0) {
                moneyReq = 0;
            }
            if (pledgeReq < 0) {
                pledgeReq = 0;
            }
            if (donationPercentage > 100) {
                donationPercentage = 100;
            }
            if (pledgePercentage > 100) {
                pledgePercentage = 100;
            }
            $("#js-required_for_goal").append('<small>Pledges</small><div class="progress sb_progress" style="margin-bottom: 0;"><div class="progress-bar sb_progress_bar" style="width: ' + pledgePercentage + '%"></div></div>');
            $("#js-required_for_goal").append('<small>Donations</small><div class="progress sb_progress" style="margin-bottom: 0;"><div class="progress-bar sb_progress_bar" style="width: ' + donationPercentage + '%;"></div></div>');
        },
        error: function (XMLHttpRequest) {
            errorDisplay(XMLHttpRequest);
        }
    });
});