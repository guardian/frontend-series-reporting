function urlToSeriesName(url) {
	return url.replace(/.*\/series\//, '');
}

function showSection(section) {
$.getJSON('testProcessedData.json', function (data) {

	var publishing_series_json = data.publishing[section].series;
	var publishing_categories_json = data.publishing[section].categories;

	console.log(publishing_series_json)

	$('#seriesPublished').highcharts({
		title: {
		    text: 'Series Published',
		    x: -20 //center
		},
		subtitle: {
		    text: 'Last 30 Days',
		    x: -20
		},
		xAxis: {
			labels: {
					formatter: function() {
						return urlToSeriesName(this.value);
					}
				},
		    categories: publishing_categories_json,
		},
		yAxis: {
		    title: {
		        text: 'Count'
		    },
		    plotLines: [{
		        value: 0,
		        width: 1,
		        color: '#808080'
		    }]
		},
		legend: {
		    layout: 'vertical',
		    align: 'right',
		    verticalAlign: 'middle',
		    borderWidth: 0
		},
		series: publishing_series_json
	});

	var engagement_series_json = data.engagement[section].series;
	var engagement_categories_json = data.engagement[section].categories;

	console.log(engagement_series_json)

	$('#engagement').highcharts({
		chart: {
			type: 'bar'
		},
        title: {
            text: 'Top 10 Series for Multi Episode Visitors'
        },
        subtitle: {
        	text:'Last 30 Days'
        },
		xAxis: {
			labels: {
					formatter: function() {
						return urlToSeriesName(this.value);
					}
				},
			categories: engagement_categories_json
		},
		yAxis: {
			title: {
				text: 'Visitors'
			},
			reversedStacks: false
		},
		legend: {
			reversed: true
		},
		plotOptions: {
			series: {
				stacking: 'normal'
			}
		},					
		series: engagement_series_json
	});

	var loyalty_series_json = data.loyalty[section].series;
	var loyalty_categories_json = data.loyalty[section].categories;

	console.log(loyalty_series_json)

	$('#loyalty').highcharts({
		chart: {
			type: 'bar'
		},
        title: {
            text: 'Top 10 Series for Multi Day Visit Visitors'
        },
        subtitle: {
        	text:'Last 30 Days'
        },
		xAxis: {
			labels: {
					formatter: function() {
						return urlToSeriesName(this.value);
					}
				},
			categories: loyalty_categories_json
		},
		yAxis: {
			title: {
				text: 'Visitors'
			},
			reversedStacks: false
		},
		legend: {
			reversed: true
		},
		plotOptions: {
			series: {
				stacking: 'normal'
			}
		},					
		series: loyalty_series_json
	});

	var x_n_series_json = data.x_n[section].series;
	var x_n_categories_json = data.x_n[section].categories;

	$('#x_n').highcharts({
		chart: {
			type: 'column'
		},
        title: {
            text: 'Number of Episodes Visited for Top 10 Multi Episode Series'
        },
        subtitle: {
        	text:'Last 30 Days'
        },
		xAxis: {
			max: 9,
			crosshair: true,
			categories: x_n_categories_json,
			title: {
				text: 'Number of episodes'
			}
		},
		legend: {
			labelFormatter: function() {
					return urlToSeriesName(this.name);
				}
		},
		yAxis: {
			min: 0,
			title: {
				text: 'Visitors'
			}
		},				
		tooltip: {
			headerFormat: '<span style="font-size:10px">{point.key}</span><table>',
			pointFormat: '<tr><td style="color:{series.color};padding:0">{series.name}: </td>' +
			'<td style="padding:0"><b>{point.y:.1f} mm</b></td></tr>',
			footerFormat: '</table>',
			shared: true,
			useHTML: true
		},
		plotOptions: {
			column: {
				pointPadding: 0.2,
				borderWidth: 0
			}
		},				
		series: x_n_series_json
	});
	// var visits_series_json = data.visits[section].series;
	// var visits_categories_json = data.visits[section].categories;

	// console.log(visits_series_json)

	// $('#visits').highcharts({
	// 	chart: {
	// 		type: 'bar'
	// 	},
 //        title: {
 //            text: 'Top 10 Series for Visits'
 //        },
 //        subtitle: {
 //        	text:'Last 30 Days'
 //        },
	// 	xAxis: {
	// 		labels: {
	// 				formatter: function() {
	// 					return urlToSeriesName(this.value);
	// 				}
	// 			},
	// 		categories: visits_categories_json
	// 	},
	// 	yAxis: {
	// 		title: {
	// 			text: 'Visits'
	// 		}
	// 	},
	// 	legend: {
	// 		reversed: true
	// 	},
	// 	plotOptions: {
	// 		series: {
	// 			stacking: 'normal'
	// 		}
	// 	},					
	// 	series: visits_series_json
	// });

});
}

var selectEl = document.getElementById('sections');
selectEl.addEventListener('change', function(){
	var section = selectEl.options[selectEl.selectedIndex].value;
	showSection(section);
});

showSection('Football');