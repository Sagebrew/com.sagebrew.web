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
        startYear = new Date(donationData[0].created.toLocaleString()).getFullYear();

    $.each(donationData, function (index, value) {
        tempTotal += (value.amount / 100);
        lifetimeTotalData.push(tempTotal);
        var tempDate = new Date(value.created.toLocaleString());
        parsedData.push([Date.UTC(tempDate.getFullYear(), tempDate.getMonth(), tempDate.getDate()), value.amount / 100]);
    });
    return {
        'individualDonationData': parsedData,
        'lifetimeTotalData': {
            'totalAmount': lifetimeTotalData,
            'startYear': startYear
        }
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
                    type: 'scatter'
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
            $("#total_donation_chart").highcharts({
                chart: {
                    type: 'area'
                },
                title: {
                    text: 'Lifetime Cumulative Donations'
                },
                xAxis: {
                    allowDecimals: false,
                    title: {
                        text: 'Donation Count'
                    }
                },
                yAxis: {
                    type: 'linear',
                    title: {
                        text: 'Total Donations Received (in $)'
                    }
                },
                tooltip: {
                    pointFormat: '${point.y:,.0f}'
                },
                plotOptions: {
                    area: {
                        pointStart: 1,
                        marker: {
                            enabled: false,
                            symbol: 'circle',
                            radius: 2,
                            states: {
                                hover: {
                                    enabled: true
                                }
                            }
                        }
                    }
                },
                series: [{
                    name: 'Total Donations',
                    data: preparedData.lifetimeTotalData.totalAmount
                }]
            });
        },
        error: function (XMLHttpRequest) {
            errorDisplay(XMLHttpRequest);
        }
    });

});