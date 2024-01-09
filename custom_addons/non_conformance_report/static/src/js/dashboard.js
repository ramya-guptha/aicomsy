odoo.define('noncr_dashboard.Dashboard', function(require) {
    "use strict";
    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var QWeb = core.qweb;
    var ajax = require('web.ajax');
    var rpc = require('web.rpc');
    var session = require('web.session');
    var _t = core._t;
    var web_client = require('web.web_client');
    // Declare an array to store chart instances
    var chartInstances = [];
    var NCRDashboard = AbstractAction.extend({
        template: 'NCRDashboard',
        events: {
            'click #apply_btn': '_onchangeFilter',
        },
        init: function(parent, context) {
            this._super(parent, context);
            this.dashboards_templates = ['DashboardNCRFilterCards', 'DashboardNcrChart'];
            this.today_sale = [];
        },
        willStart: function() {
            var self = this;
            return $.when(this._super()).then(function() {
                return self.fetch_data();
            });
        },
        start: function() {
            var self = this;
            this.set("title", 'Dashboard');
            return this._super().then(function() {
                self.render_dashboards();
                self.render_graphs();
                self.render_filter();
            });
        },
        /**
        rendering the dashboard
        */
        render_dashboards: function() {
            var self = this;
            _.each(this.dashboards_templates, function(template) {
                self.$('.o_pj_dashboard').append(QWeb.render(template, {
                    widget: self
                }));
            });
        },
        /**
        function for getting values to the filters
        */
        render_filter: function() {
            ajax.rpc('/ncr/filter').then(function(data) {
                var locations = data[0]
                var ncr_source =data[1]
                $(locations).each(function(location) {
                    $('#locations_selection').append("<option value=" + locations[location].id + ">" + locations[location].name + "</option>");
                });
                $(ncr_source).each(function(src) {
                    $('#src_selection').append("<option value=" + ncr_source[src].id + ">" + ncr_source[src].name + "</option>");
                });
                var startDateInput = document.getElementById("start_date");
                var endDateInputt = document.getElementById("end_date");


                // Set the value to a specific date (e.g., "2023-06-01")
                var today = new Date();

                var formattedDate = today.getFullYear() + '-' +
                            ('0' + (today.getMonth() + 1)).slice(-2) + '-' +
                            ('0' + today.getDate()).slice(-2);
                endDateInputt.value = formattedDate
                var sixMonthsAgo = new Date();
                sixMonthsAgo.setMonth(sixMonthsAgo.getMonth() - 6);
                sixMonthsAgo.setDate(1);
                startDateInput.value = sixMonthsAgo.getFullYear() + '-' + ('0' + (sixMonthsAgo.getMonth() + 1)).slice(-2)
                                    + '-' + ('0' + sixMonthsAgo.getDate()).slice(-2);


            })
        },

        /**
        function for getting values to the filters
        */
        _onchangeFilter: function() {
            this.flag = 1
            var start_date = $('#start_date').val();
            var end_date = $('#end_date').val();
            var self = this;
            if (!start_date) {
                start_date = "null"
            }
            if (!end_date) {
                end_date = "null"
            }
            var locations_selection = $('#locations_selection').val();
            var src_selection = $('#src_selection').val();
            var ncr_selection = $('#ncr_selection').val();

            /**ajax.rpc('/incident/filter-apply', {
                'data': {
                    'start_date': start_date,
                    'end_date': end_date,
                    'location': locations_selection,
                    'ncr': src_selection,
                    'uid': session.uid
                }
            }).then(function(data) {
                self.total_incidents_ids = data['total_incidents_ids']
                document.getElementById("tot_incidents").innerHTML = data['total_incidents_ids'].length
            })**/
            self.render_graphs();

        },

        // Function to generate random color
        getBackgroundColor: function() {
                    var color = '#1183DC';
                    return color;
                },

        // Function to destroy existing charts
         destroyCharts: function() {
            if (chartInstances.length > 0) {
                chartInstances.forEach(function (chart) {
                    chart.destroy();
                });
                chartInstances = [];
            }
        },

        /**
        rendering the graph
        */
        render_graphs: function() {
            var self = this;
            self.destroyCharts()
            self.render_ncr_by_location();
            self.render_ncr_source_classification_graph();
            self.render_ncr_cost_of_rework_graph();
            self.render_ncr_backcharges();
        },
        createBarChart: function(ctx, data, title) {
            var input1 = data.labels;
            var input2 = data.data;
            var input3 = data.classification;

            var dataByMonth = {};
            var colors_list = ["#ef9b20", "#82C341", "#EA5545", "#1179DC", "#82F341", "#A1FB8E", "#73FBFD", "#D0FD81",
                               "#0F0396", "#7E909A", "#1C4E80", "#488A99", "#AC3E31", "#DADADA", "1F3F49", "#3484848"];

            var colors = new Map();
            var count = 0;
            for (var i = 0; i < input1.length; i++) {
                var dateString = input1[i];
                var date = new Date(dateString);
                var monthKey = date.getMonth() + 1 + '-' + date.getFullYear();

                if (!dataByMonth[monthKey]) {
                    dataByMonth[monthKey] = {
                        labels: [],
                        datasets: {}
                    };
                }

                dataByMonth[monthKey].labels.push(date);

                var classification = input3[i];
                if (!dataByMonth[monthKey].datasets[classification]) {
                    dataByMonth[monthKey].datasets[classification] = [];
                }
                if(!colors.get(classification)){
                    colors.set(classification, colors_list[count]);
                    count++;
                }

                dataByMonth[monthKey].datasets[classification].push(input2[i]);
            }

            var labels = [];
            var datasets = [];

            for (var monthKey in dataByMonth) {
                if (dataByMonth.hasOwnProperty(monthKey)) {
                    var monthData = dataByMonth[monthKey];
                    var monthLabel = monthData.labels[0];
                    var formattedLabel = monthLabel.toLocaleString('default', { month: 'short', year: 'numeric' });

                    labels.push(formattedLabel);

                    for (var classification in monthData.datasets) {
                        if (monthData.datasets.hasOwnProperty(classification)) {
                            var dataForClassification = monthData.datasets[classification];

                            if (dataForClassification.length === 0 || dataForClassification.reduce((a, b) => a + b, 0) === 0) {
                                continue;
                            }

                            var datasetIndex = datasets.findIndex(function (dataset) {
                                return dataset.label === classification;
                            });

                            if (datasetIndex === -1) {
                                var newDataset = {
                                    label: classification,
                                    data: [],
                                    backgroundColor: colors.get(classification) || getRandomColor(),
                                    borderColor: '#ffffff',
                                    borderWidth: 1
                                };
                                datasets.push(newDataset);
                                datasetIndex = datasets.length - 1;
                            }

                            while (datasets[datasetIndex].data.length < labels.length - 1) {
                                datasets[datasetIndex].data.push(0);
                            }


                            datasets[datasetIndex].data.push(dataForClassification.reduce((a, b) => a + b, 0));
                        }
                    }
                }
            }

            var chartData = {
                labels: labels,
                datasets: datasets
            };

            var options = {
                responsive: true,
                title: {
                    display: true,
                    position: "top",
                    text: title || "Chart Title",
                    fontSize: 18,
                    fontColor: "#111"
                },
                legend: {
                    display: true,
                    position: "top"
                },
                scales: {
                    yAxes: [{
                        ticks: {
                            min: 0
                        },
                        stacked: false
                    }],
                    xAxes: [{
                        stacked: false
                    }]
                }
            };

            var chart = new Chart(ctx, {
                type: 'bar',
                data: chartData,
                options: options
            });
            // Save the chart instance for later use
            chartInstances.push(chart);

            // Function to generate random color
            function getRandomColor() {
                var colorList = ["#1179DC", "#82C341", "#A1FB8E", "#73FBFD", "#D0FD81", "#0F0396"]
                var randomIndex = Math.floor(Math.random() * colorList.length);
                return colorList[randomIndex];

            }
        },

        _getStartDate: function(){
            var self = this;
            if (self.flag === 0){
                var sixMonthsAgo = new Date();
                sixMonthsAgo.setMonth(sixMonthsAgo.getMonth() - 6);
                sixMonthsAgo.setDate(1);
                return sixMonthsAgo.getFullYear() + '-' + ('0' + (sixMonthsAgo.getMonth() + 1)).slice(-2)
                                    + '-' + ('0' + sixMonthsAgo.getDate()).slice(-2);
            }
            else {
                return  $('#start_date').val();
            }
        },
        _getEndDate: function(){
            var self = this;
            if (self.flag === 0){
                var today = new Date();

                return today.getFullYear() + '-' +
                            ('0' + (today.getMonth() + 1)).slice(-2) + '-' +
                            ('0' + today.getDate()).slice(-2);
            }
            else {
                return $('#end_date').val();
            }
        },
        /**
        function for getting values to location  graph
        */
        render_ncr_by_location: function() {
            var self = this;

            var ctx = self.$(".ncr_by_location");
            var end_date = self._getEndDate();
            var start_date = self._getStartDate();

            var location = $('#locations_selection').val();
            var src_selection = $('#src_selection').val();
            var ncr_selection = $('#ncr_selection').val();
             rpc.query({
                         model: "x.ncr.dashboard",
                         method: 'get_ncr_by_location',
                         args: [start_date, end_date, location,src_selection, ncr_selection],
                    }).then(function(data) {
                        var classificationColors = {
                            'Plant location - 1': '#ef9b20',
                            'Plant location - 2': '#82C341',
                            'Plant location - 3': '#ea5545',
                            'Plant location - 4': '#1179DC',
                            // Add more colors as needed
                        };
                        self.createBarChart(ctx, data, "NCR Breakdown By Location");
                    });
        },

        render_ncr_source_classification_graph: function () {
            var self = this;

            var ctx = self.$(".ncs_source_classification");
            var end_date = self._getEndDate();
            var start_date = self._getStartDate();
            var location = $('#locations_selection').val();
            var src_selection = $('#src_selection').val();
            var ncr_selection = $('#ncr_selection').val();
             rpc.query({
                        model: "x.ncr.dashboard",
                        method: 'get_ncr_source_classification',
                        args: [start_date, end_date, location, src_selection, ncr_selection],
                    }).then(function(data) {
                        var classificationColors = {
                            'Material': '#ef9b20',
                            'Engineering': '#82C341',
                            'In-Process Dimensional': '#ea5545',
                            'In-Process Welding/Brazing': '#1179DC',
                            // Add more colors as needed
                        };
                        self.createBarChart(ctx, data, "NCR Breakdown By Source");
                    });
        },

        render_ncr_cost_of_rework_graph: function () {
            var self = this;

            var ctx = self.$(".ncs_cost_of_rework");
            var end_date = self._getEndDate();
            var start_date = self._getStartDate();
            var location = $('#locations_selection').val();
            var src_selection = $('#src_selection').val();
            var ncr_selection = $('#ncr_selection').val();
             rpc.query({
                        model: "x.ncr.dashboard",
                        method: 'get_cost_of_rework',
                        args: [start_date, end_date, location, src_selection, ncr_selection],
                    }).then(function(data) {
                        var classificationColors = {
                            'Material': '#ef9b20',
                            'Engineering': '#82C341',
                            'In-Process Dimensional': '#ea5545',
                            'In-Process Welding/Brazing': '#1179DC',
                            // Add more colors as needed
                        };
                        self.createBarChart(ctx, data, "Cost of Rework");
                    });
        },

        render_ncr_backcharges: function () {
            var self = this;

            var ctx = self.$(".ncs_backcharges");
            var end_date = self._getEndDate();
            var start_date = self._getStartDate();
            var location = $('#locations_selection').val();
            var src_selection = $('#src_selection').val();
            var ncr_selection = $('#ncr_selection').val();
             rpc.query({
                        model: "x.ncr.dashboard",
                        method: 'get_customer_backcharges',
                        args: [start_date, end_date, location, src_selection, ncr_selection],
                    }).then(function(data) {
                        var classificationColors = {
                            'Material': '#ef9b20',
                            'Engineering': '#82C341',
                            'In-Process Dimensional': '#ea5545',
                            'In-Process Welding/Brazing': '#1179DC',
                            // Add more colors as needed
                        };
                        self.createBarChart(ctx, data, "Customer Backcharges on Site Discrepancy");
                    });
        },


        on_reverse_breadcrumb: function() {
            var self = this;
            web_client.do_push_state({});
            this.fetch_data().then(function() {
                self.$('.o_pj_dashboard').empty();
                self.render_dashboards();
                self.render_graphs();
                self.render_filter();
            });
        },

        /**
        function for getting values when page is loaded
        */
        fetch_data: function() {
            this.flag = 0
            var self = this;


            return 0;
        },


    });
    core.action_registry.add('ncr_dashboard', NCRDashboard);
    return NCRDashboard;
});

