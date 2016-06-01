/* global $ */

function prepareDonationData(donationData) {
    var parsedData = [],
        lifetimeTotalData = [],
        tempTotal = 0,
        startYear,
        parsedShortData = [];
    if (donationData.length > 0) {
        startYear = new Date(
            donationData[0].created.toLocaleString()).getFullYear();
        $.each(donationData, function (index, value) {
            tempTotal += parseFloat(value.actual_amount.replace(/,/g, ''));
            lifetimeTotalData.push(tempTotal);
            var tempDate = new Date(value.created.toLocaleString());
            parsedData.push([Date.UTC(
                tempDate.getFullYear(), tempDate.getMonth(),
                tempDate.getDate(), tempDate.getHours(),
                tempDate.getMinutes(), tempDate.getSeconds()),
                parseFloat(value.actual_amount.replace(/,/g, ''))]);
            parsedShortData.push([Date.UTC(
                tempDate.getFullYear(), tempDate.getMonth(),
                tempDate.getDate()), value.actual_amount]);
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

export function donationsGraph(data, elementID) {
    var Highcharts = require('highcharts');
    require('highcharts/modules/exporting')(Highcharts);
    var preparedData = prepareDonationData(data.results);
    // Create a scatter plot showing each donation received as a point
    Highcharts.setOptions({
        lang: {
            thousandsSep: ','
        }
    });
    $(elementID).highcharts({
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
            pointFormat: '{point.x:%e. %b}: ${point.y:,.2f}'
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
}