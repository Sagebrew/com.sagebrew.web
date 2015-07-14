/*global $, jQuery, guid, Croppic, alert, highcharts*/
Number.prototype.format = function (n, x) {
    /*
    This function will format any given integer into a comma separated string,
    useful for converting integers to monetary representations
    e.g.
    1234..format();           // "1,234"
    12345..format(2);         // "12,345.00"
    123456.7.format(3, 2);    // "12,34,56.700"
    123456.789.format(2, 4);  // "12,3456.79"
     */
    var re = '\\d(?=(\\d{' + (x || 3) + '})+' + (n > 0 ? '\\.' : '$') + ')';
    return this.toFixed(Math.max(0, ~~n)).replace(new RegExp(re, 'g'), '$&,');
};

function prepareDonationData(donationData) {
    var parsedData = [],
        lifetimeTotalData = [],
        tempTotal = 0,
        startYear = new Date(donationData[0].created.toLocaleString()).getFullYear(),
        parsedShortData = [];

    $.each(donationData, function (index, value) {
        tempTotal += (value.amount / 100);
        lifetimeTotalData.push(tempTotal);
        var tempDate = new Date(value.created.toLocaleString());
        parsedData.push([Date.UTC(tempDate.getFullYear(), tempDate.getMonth(), tempDate.getDate(), tempDate.getHours(), tempDate.getMinutes(), tempDate.getSeconds()), value.amount / 100]);
        parsedShortData.push([Date.UTC(tempDate.getFullYear(), tempDate.getMonth(), tempDate.getDate()), value.amount / 100]);
    });
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
    var parsedVoteData = [];
    $.each(voteData, function (index, value) {
        var tempDate = new Date(value.created.toLocaleString()),
            voteValue;
        if (value.active) {
            voteValue = 1;
        } else {
            voteValue = 0;
        }
        parsedVoteData.push([Date.UTC(tempDate.getFullYear(), tempDate.getMonth(), tempDate.getDate()), voteValue]);
    });
    return {
        'dailyVoteTotal': parsedVoteData
    };
}

$(document).ready(function () {
    $.ajax({
        xhrFields: {withCredentials: true},
        type: "GET",
        url: "/v1/campaigns/" + "tyler_wiersing" + "/donations/",
        cache: false,
        processData: false,
        success: function (data) {
            var preparedData = prepareDonationData(data.results);
            $("#individual_donation_chart").highcharts({
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
        url: "/v1/campaigns/" + "tyler_wiersing" + "/pledged_votes/",
        cache: false,
        processData: false,
        success: function (data) {
            var preparedData = preparePledgedVoteData(data);
            $("#pledged_vote_daily_chart").highcharts({
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
                    }
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
                    pointFormat: '{point.y} Pledge Vote'
                },
                series: [
                    {
                        name: 'Lifetime Pledged Votes',
                        data: preparedData.dailyVoteTotal
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
        url: "/v1/campaigns/" + "tyler_wiersing",
        cache: false,
        processData: false,
        success: function (data) {
            console.log(data);
            $("#total_donation_amount").append("$" + data.total_donation_amount / 100);
            $("#total_pledge_vote_amount").append(data.total_pledge_vote_amount);
        },
        error: function (XMLHttpRequest) {
            errorDisplay(XMLHttpRequest);
        }
    });
});