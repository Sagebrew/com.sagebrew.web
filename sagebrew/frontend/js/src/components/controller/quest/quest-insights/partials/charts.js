/*global $*/
var request = require('api').request,
    highcharts = require('highcharts');

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

export function getCharts(missionID) {
    request.get({url: "/v1/missions/" + missionID + "/donations/"})
        .done(function (data) {
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
        });
    request.get({url: "/v1/missions/" + missionID + "/pledged_votes_per_day/"})
        .done(function (data) {
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
        });
    request.get({url: "/v1/missions/" + missionID + "/"})
        .done(function (data) {
            var totalDonation = $("#js-total_donation_amount"),
                totalPledge = $("#js-total_pledge_vote_amount"),
                donationAmount = data.total_donation_amount,
                pledgeAmount = data.total_pledge_vote_amount;
            totalDonation.empty();
            totalPledge.empty();
            if (typeof donationAmount === "undefined") {
                donationAmount = 0;
            } else {
                donationAmount = donationAmount / 100;
            }
            if (typeof pledgeAmount === "undefined") {
                pledgeAmount = 0;
            }
            totalDonation.append("Total Donations<h2>$" + donationAmount + "</h2>");
            totalPledge.append("Total Pledge Votes<h2>" + pledgeAmount + "</h2>");
        });
}