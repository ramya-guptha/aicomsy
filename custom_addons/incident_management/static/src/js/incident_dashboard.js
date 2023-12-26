odoo.define('incident_dashboard.Dashboard', function(require) {
    "use strict";
    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var QWeb = core.qweb;
    var ajax = require('web.ajax');
    var rpc = require('web.rpc');
    var session = require('web.session');
    var _t = core._t;
    var web_client = require('web.web_client');
    var chartInstances = [];
    var IncidentDashboard = AbstractAction.extend({
        template: 'IncidentDashboard',
        events: {
            'click .tot_incidents': 'tot_incidents',
            'click #apply_btn': '_onchangeFilter',
        },
        init: function(parent, context) {
            this._super(parent, context);
            this.dashboards_templates = ['DashboardFilterCards', 'DashboardIncChart'];
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
            ajax.rpc('/incident/filter').then(function(data) {
                var locations = data[0]
                $(locations).each(function(location) {
                    $('#locations_selection').append("<option value=" + locations[location].id + ">" + locations[location].name + "</option>");
                });
            })
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
            var incidents_selection = $('#incidents_selection').val();

            ajax.rpc('/incident/filter-apply', {
                'data': {
                    'start_date': start_date,
                    'end_date': end_date,
                    'location': locations_selection,
                    'incidents': incidents_selection,
                    'uid': session.uid
                }
            }).then(function(data) {
                self.total_incidents_ids = data['total_incidents_ids']
                document.getElementById("tot_incidents").innerHTML = data['total_incidents_ids'].length
            })
            self.render_graphs();

        },
        // Function to generate random color
        getBackgroundColor: function() {
                    var color = '#1183DC';
                    return color;
                },
         /**
        rendering the graph
        */
        render_graphs: function() {
            var self = this;
            self.destroyCharts()
            self.render_inc_severity_graph();
            self.render_inc_cost_impact_graph();
            self.render_normal_days_mom_graph();
            self.render_severity_classification_graph();
            self.render_incident_frequency_rate_graph();
            self.render_incident_status_graph();
        },
        render_normal_days_mom_graph: function() {
            var self = this
            var ctx = self.$(".normal_days_mom");
            var start_date = $('#start_date').val();
            var end_date = $('#end_date').val();
            var location = $('#locations_selection').val();
            var incident_type = $('#incidents_selection').val();

            rpc.query({
                model: "x.inc.report.normal.days",
                method: 'get_normal_mom',
                args: [start_date, end_date, location, incident_type],
            }).then(function(data) {
                var formattedLabels = data.labels.map(function(label) {
                    var date = new Date(label);
                    return date.toLocaleString('en-US', { month: 'short', year: 'numeric' });
                });
                var data = {
                    labels: formattedLabels,
                    datasets: [{
                            label: "Normal Days MOM",
                            data: data.data,
                            backgroundColor: self.getBackgroundColor(),
                            borderColor: self.getBackgroundColor(),
                            borderWidth: 1
                        },

                    ]
                };
                //options
                var options = {
                    responsive: true,
                    title: {
                        display: true,
                        position: "top",
                        text: "Normal Days MOM",
                        fontSize: 18,
                        fontColor: "#111"
                    },
                    legend: {
                        display: true,
                    },
                    scales: {
                        yAxes: [{
                            ticks: {
                                min: 0
                            }
                        }]
                    }
                };
                //create Chart class object
                var chart = new Chart(ctx, {
                    type: 'bar',
                    data: data,
                    options: options
                });
                // Save the chart instance for later use
                chartInstances.push(chart);

            });

        },
         render_incident_status_graph: function() {
            var self = this
            var ctx = self.$(".incident_status");
            var start_date = $('#start_date').val();
            var end_date = $('#end_date').val();
            var location = $('#locations_selection').val();
            var incident_type = $('#incidents_selection').val();
            rpc.query({
                model: "x.inc.report.normal.days",
                method: 'get_incident_status',
                args: [start_date, end_date, location, incident_type],
            }).then(function(data) {
                var modifiedLabel = []

                for(var i=0;i <data.labels.length ;i++){
                    if(data.labels[i] === "new"){
                        modifiedLabel.push("New")
                    }
                    else if(data.labels[i] === "investigation_assigned"){
                        modifiedLabel.push("Assigned")
                    }
                    else if(data.labels[i] === "investigation_in_progress"){
                        modifiedLabel.push("In Progress")
                    }
                    else if(data.labels[i] === "action_review"){
                        modifiedLabel.push("Action Review")
                    }
                    else if(data.labels[i] === "action_review"){
                        modifiedLabel.push("Action Review")
                    }
                    else if(data.labels[i] === "closed"){
                        modifiedLabel.push("Closed")
                    }
                    else if(data.labels[i] === "canceled"){
                        modifiedLabel.push("Canceled")
                    }
                }
                var data = {
                    labels: modifiedLabel,
                    datasets: [{
                            label: "Incident Status",
                            data: data.data,
                            backgroundColor:  [
                                "rgba(17, 131, 220,1)",
                                "#ef9b20",
                                "rgba(130, 195, 65,1)",

                                "rgba(115, 251, 253,1)",
                                "rgba(208, 253, 129,1)",
                                "rgba(15, 3, 150,1)",
                            ],
                            borderColor: [
                                "rgba(255, 255, 255,1)",

                            ],
                            borderWidth: 1
                        },

                    ]
                };
                //options
                var options = {
                    responsive: true,
                    title: {
                        display: true,
                        position: "top",
                        text: "Incident Status",
                        fontSize: 18,
                        fontColor: "#111"
                    },
                    legend: {
                        display: true,
                    },

                };
                //create Chart class object
                var chart = new Chart(ctx, {
                    type: 'doughnut',
                    data: data,
                    options: options
                });
                // Save the chart instance for later use
                chartInstances.push(chart);

            });

        },
        render_incident_frequency_rate_graph: function() {
            var self = this
            var ctx = self.$(".incident_frequency_rate");
            var start_date = $('#start_date').val();
            var end_date = $('#end_date').val();
            var location = $('#locations_selection').val();
            var incident_type = $('#incidents_selection').val();
            rpc.query({
                model: "x.inc.report.normal.days",
                method: 'get_incident_frequency_rate',
                args: [start_date, end_date, location, incident_type],
            }).then(function(data) {

                var formattedLabels = data.labels.map(function(label) {
                    var date = new Date(label);
                    return date.toLocaleString('en-US', { month: 'short', year: 'numeric' });
                });

                var data = {
                    labels: formattedLabels,
                    datasets: [{
                            label: "Incident Frequency Rate",
                            data: data.data,
                            backgroundColor:self.getBackgroundColor(),
                            borderColor: self.getBackgroundColor(),
                            borderWidth: 1
                        },

                    ]
                };
                //options
                var options = {
                    responsive: true,
                    title: {
                        display: true,
                        position: "top",
                        text: "Incident Frequency Rate",
                        fontSize: 18,
                        fontColor: "#111"
                    },
                    legend: {
                        display: true,
                    },
                    scales: {
                        yAxes: [{
                            ticks: {
                                min: 0
                            }
                        }]
                    }
                };
                //create Chart class object
                var chart = new Chart(ctx, {
                    type: 'line',
                    data: data,
                    options: options
                });
                // Save the chart instance for later use
                chartInstances.push(chart);

            });

        },
        render_severity_classification_graph: function () {
            var self = this;

            var ctx = self.$(".incident_severity_classification");
            var start_date = $('#start_date').val();
            var end_date = $('#end_date').val();
            var location = $('#locations_selection').val();
            var incident_type = $('#incidents_selection').val();
             rpc.query({
                        model: "x.inc.report.normal.days",
                        method: 'get_severity_classification',
                        args: [start_date, end_date, location, incident_type],
                    }).then(function(data) {
                        // Sample Inputs
                        var input1 = data.labels;
                        var input2 = data.data;
                        var input3 = data.classification;

                        // Organize data by month
                        var dataByMonth = {};
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

                            dataByMonth[monthKey].datasets[classification].push(input2[i]);
                        }

                        // Extract data for the chart
                        var labels = [];
                        var datasets = [];
                        // Define a list of colors for each classification

                        var classificationColors = {
                            'Class A': '#ef9b20',
                            'Class B': '#82C341',
                            'Class C': '#ea5545',
                            'Class D': '#1179DC',
                            // Add more colors as needed
                        };
                        // Iterate through each month
                        for (var monthKey in dataByMonth) {
                            if (dataByMonth.hasOwnProperty(monthKey)) {

                                var monthData = dataByMonth[monthKey];

                                // Create labels
                                var monthLabel = monthData.labels[0];
                                var formattedLabel = monthLabel.toLocaleString('default', { month: 'short', year: 'numeric' });

                                labels.push(formattedLabel);

                                // Create datasets for each classification type
                                for (var classification in monthData.datasets) {
                                    if (monthData.datasets.hasOwnProperty(classification)) {
                                        var dataForClassification = monthData.datasets[classification];

                                         // Skip datasets with no data
                                        if (dataForClassification.length === 0 || dataForClassification.reduce((a, b) => a + b, 0) === 0) {
                                            continue;
                                        }
                                        // Find or create the dataset for the classification
                                        var datasetIndex = datasets.findIndex(function (dataset) {
                                            return dataset.label === classification;
                                        });

                                        if (datasetIndex === -1) {
                                            // Create the dataset if it doesn't exist
                                            var newDataset = {
                                                label: classification,
                                                data: [],
                                                backgroundColor:  classificationColors[classification],
                                                borderColor:  '#ffffff',
                                                borderWidth: 1
                                            };
                                            datasets.push(newDataset);
                                            datasetIndex = datasets.length - 1; // Update the datasetIndex
                                        }

                                        // Pad the data array with 0s for previous months
                                        while (datasets[datasetIndex].data.length < labels.length - 1) {
                                            datasets[datasetIndex].data.push(0);
                                        }

                                        // Add the current month's count
                                        datasets[datasetIndex].data.push(dataForClassification.reduce((a, b) => a + b, 0));
                                    }
                                }
                            }
                        }



                        var chartData = {
                            labels: labels,
                            datasets: datasets
                        };

                        // Options for the chart
                        var options = {
                            responsive: true,
                            title: {
                                display: true,
                                position: "top",
                                text: "Severity Classification",
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
                                    stacked: true
                                }],
                                xAxes: [{
                                    stacked: true
                                }]
                            }

                        };

                        // Create Chart class object
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
                    });
              },

        render_inc_cost_impact_graph: function() {
             var self = this

            var ctx = self.$(".incident_cost_impact");
            var start_date = $('#start_date').val();
            var end_date = $('#end_date').val();
            var location = $('#locations_selection').val();
            var incident_type = $('#incidents_selection').val();
            rpc.query({
                model: "x.inc.report.cost.impact",
                method: 'get_cost_impact',
                args: [start_date, end_date, location, incident_type],
            }).then(function(data) {
                 var formattedLabels = data.labels.map(function(label) {
                    var date = new Date(label);
                    return date.toLocaleString('en-US', { month: 'short', year: 'numeric' });
                });

                var data = {
                    labels: formattedLabels,
                    datasets: [{
                            label: "Cost Impact Ratio",
                            data: data.data,
                            backgroundColor: self.getBackgroundColor(),
                            borderColor: self.getBackgroundColor(),
                            borderWidth: 1
                        },

                    ]
                };
                //options
                var options = {
                    responsive: true,
                    title: {
                        display: true,
                        position: "top",
                        text: "Incident Cost Impact Ratio",
                        fontSize: 18,
                        fontColor: "#111"
                    },
                    legend: {
                        display: true,
                    },
                    scales: {
                        yAxes: [{
                            ticks: {
                                min: 0
                            }
                        }]
                    }
                };
                //create Chart class object
                var chart = new Chart(ctx, {
                    type: 'line',
                    data: data,
                    options: options
                });
                // Save the chart instance for later use
                chartInstances.push(chart);

            });

        },

        /**
        function for getting values to employee graph
        */
        render_inc_severity_graph: function() {
            var self = this
            var ctx = self.$(".incident_severity_rate");
            var start_date = $('#start_date').val();
            var end_date = $('#end_date').val();
            var location = $('#locations_selection').val();
            var incident_type = $('#incidents_selection').val();
            rpc.query({
                model: "x.inc.report.severity.rate",
                method: 'get_severity_rate',
                args: [start_date, end_date, location, incident_type],
            }).then(function(data) {
                var formattedLabels = data.labels.map(function(label) {
                    var date = new Date(label);
                    return date.toLocaleString('en-US', { month: 'short', year: 'numeric' });
                });
                var data = {
                    labels: formattedLabels,
                    datasets: [{
                            label: "Severity Rate",
                            data: data.data,
                            backgroundColor: self.getBackgroundColor(),
                            borderColor: self.getBackgroundColor(),
                            borderWidth: 1
                        },

                    ]
                };
                //options
                var options = {
                    responsive: true,
                    title: {
                        display: true,
                        position: "top",
                        text: "Incident Severity Rate",
                        fontSize: 18,
                        fontColor: "#111"
                    },
                    legend: {
                        display: true,
                    },
                    scales: {
                        yAxes: [{
                            ticks: {
                                min: 0
                            }
                        }]
                    }
                };
                //create Chart class object
                var chart = new Chart(ctx, {
                    type: 'bar',
                    data: data,
                    options: options
                });
                // Save the chart instance for later use
                chartInstances.push(chart);

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
        for opening project view
        */
        tot_incidents: function(e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            var options = {
                on_reverse_breadcrumb: this.on_reverse_breadcrumb,
            };
                this.do_action({
                    name: _t("Incidents"),
                    type: 'ir.actions.act_window',
                    res_model: 'x.incident.record',
                     domain: [
                        ["id", "in", this.total_incidents_ids]
                    ],
                    view_mode: 'tree,form',
                    views: [
                        [false, 'tree'],
                        [false, 'form']
                    ],
                    target: 'current'
                }, options)
        },
       /**
        function for getting values when page is loaded
        */
        fetch_data: function() {
            this.flag = 0
            var self = this;
            var def1 = this._rpc({
                model: 'x.incident.record',
                method: 'get_tiles_data'
            }).then(function(result) {
                    self.total_locations = result['total_locations']
                    self.total_incidents = result['total_incidents']
                    self.total_incidents_ids = result['total_incidents_ids']
            });
            /**
            function for getting values to hours table
            */

            return $.when(def1);
        },
    });
    core.action_registry.add('incident_dashboard', IncidentDashboard);
    return IncidentDashboard;
});

