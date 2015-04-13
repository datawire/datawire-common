// Monitoring Console
/* global proton */

var seriesMap = {};             // name -> series object
var svcToColor = {              // service/agent name -> color
    "bizlogic-5680": 0,
    "bizlogic-5681": 1,
    "bizlogic-5682": 2
};

var minTime, maxTime;           // Keep track of chart bounds

function dateToTimeStr(dateValue) {
    "use strict";
    var date = new Date();
    var offset = date.getTimezoneOffset() * 60 * 1000;
    date.setTime(dateValue - offset);
    return date.toISOString().substring(11, 19);
}

var chart1Series = [{
    data: [],
    points: {show: false},
    lines: {show: false},
    bars: {show: false}
}];

var chart1 = $.plot($("#chart1div"), chart1Series, {  // (top) all the outboxes
    series: {
        lines: {show: true},
        points: {show: true}
    },
    grid: {
	borderWidth: 1,
	minBorderMargin: 20,
	labelMargin: 10,
	backgroundColor: {
	    colors: ["#fff", "#e4f4f4"]
	},
	margin: {
	    top: 8,
	    bottom: 20,
	    left: 20
	}
    },
    xaxis: {
        tickFormatter: dateToTimeStr
    },
    yaxis: {
        labelWidth: 40
    },
    legend: {show: true, position: "nw"}
});

var chart2Series = [{
    data: [],
    points: {show: false},
    lines: {show: false},
    bars: {show: false}
}];

var chart2 = $.plot($("#chart2div"), chart2Series, {  // (bottom) in/out rates for bizlogic and outbox
    series: {
        lines: {show: true},
        points: {show: true}
    },
    grid: {
	borderWidth: 1,
	minBorderMargin: 20,
	labelMargin: 10,
	backgroundColor: {
	    colors: ["#fff", "#e4f4f4"]
	},
	margin: {
	    top: 8,
	    bottom: 20,
	    left: 20
	}
    },
    xaxis: {
        tickFormatter: dateToTimeStr
    },
    yaxis: {
        labelWidth: 40,
        min: 0.5,
        ticks: [1,10,100,1000,10000],
        transform: function (v) { "use strict"; return v === 0 ? Math.log(0.00001) : Math.log(v); },
        inverseTransform: function (v) { "use strict"; return Math.exp(v); }
    },
    legend: {show: true, position: "nw"}
});

function trimSeries(series) {
    "use strict";
    for (var idx = 0; idx < series.data.length; idx += 1) {
        if (series.data[idx][0] > minTime) {
            break;
        }
    }
    series.data.splice(0, idx);
}

function updateCharts() {
    "use strict";

    var d = new Date();
    maxTime = d.getTime();
    minTime = maxTime - 30 * 1000;

    chart1Series[0].data = [[minTime, 0], [maxTime, 0]];
    chart2Series[0].data = [[minTime, 1], [maxTime, 1]];

    var idx;
    for (idx = 1; idx < chart1Series.length; idx += 1) {
        trimSeries(chart1Series[idx]);
    }
    for (idx = 1; idx < chart2Series.length; idx += 1) {
        trimSeries(chart2Series[idx]);
    }

    chart1.setData(chart1Series);
    chart1.setupGrid();
    chart1.draw();

    chart2.setData(chart2Series);
    chart2.setupGrid();
    chart2.draw();

    _.delay(updateCharts, 33.3);
}

updateCharts();

function getServiceName(content) {
    "use strict";
    var name = content.address.substring(12, 99);
    name += content.agent.substring(28, 99);
    return name;
}

var fieldNameMap = {
    "manifold_messages":  "Message backlog",
    "manifold_streams":   "Number of addresses",
    "manifold_last_idle": "Message idle time",
    "incoming_rate":      "Incoming messages/sec (x)",
    "outgoing_rate":      "Outgoing messages/sec (o)"
};

function getName(content, field) {
    "use strict";
    return getServiceName(content) + " " + fieldNameMap[field];
}

function cross(ctx, x, y, radius) {  // fifth argument would be shadow
    "use strict";
    var size = radius * Math.sqrt(Math.PI) / 2;
    ctx.moveTo(x - size, y - size);
    ctx.lineTo(x + size, y + size);
    ctx.moveTo(x - size, y + size);
    ctx.lineTo(x + size, y - size);
}

function addDataPoint(content, field, seriesList) {
    "use strict";
    var seriesName = getName(content, field);
    var series = seriesMap[seriesName];
    if (!series) {
        var serviceName = getServiceName(content);
        var color = svcToColor[serviceName];
        if (!color && color !== 0) {
            color = _.size(svcToColor);
            svcToColor[serviceName] = color;
        }
        series = {
            data: [],
            color: color,
            lines: {show: true},
            points: {show: true},
            label: seriesName
        };
        if (field === "incoming_rate") {
            series.points.symbol = cross;
        } else if (field === "outgoing_rate") {
            series.points.fill = true;
        }
        seriesMap[seriesName] = series;
        seriesList.push(series);
    }
    series.data.push([content.timestamp, content[field]]);
}

function processMessage(message) {
    "use strict";
    for (var idx = 0; idx < message.body.length; idx += 1) {
        var content = message.body[idx];
        if (content.timestamp < minTime) {
            continue;
        }

        if (content.address.indexOf("outbox") >= 0) {
            addDataPoint(content, "manifold_messages", chart1Series);
            addDataPoint(content, "outgoing_rate", chart2Series);
            addDataPoint(content, "incoming_rate", chart2Series);
        } else if (content.address.indexOf("bizlogic") >= 0) {
            addDataPoint(content, "outgoing_rate", chart2Series);
            addDataPoint(content, "incoming_rate", chart2Series);
        }
    }
}


// Proton stuff ----------------------------------------------------------------------

var message = new proton.Message();
var messenger = new proton.Messenger();

function pumpData() {
    "use strict";
    while (messenger.incoming()) {
        var t = messenger.get(message, true);  // true means turn binaries into strings
        processMessage(message);
        messenger.accept(t);
    }

    if (messenger.isStopped()) {
        message.free();
        messenger.free();
    }
}

function errorHandler(error) {
    "use strict";
    console.log("Received error " + error);
}

function onSubscription(subscription) {
    "use strict";
    console.log("OnSubscription:");
    console.log(subscription);
    messenger.recv();
}

messenger.on("work", pumpData);
messenger.on("error", errorHandler);
messenger.on("subscription", onSubscription);
messenger.start();

messenger.subscribe("amqp://localhost:5700/" + "//localhost/monitor");
