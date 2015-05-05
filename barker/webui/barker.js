// Barker UI
/* global proton, barker_host */

var message = new proton.Message();
var messenger = new proton.Messenger();

var myUsername = "ark3";

function sendMessage(address, content) {
    "use strict";
    message.clear();
    message.setAddress("amqp://" + barker_host + ":5674/" + address);
    message.body = content;
    messenger.put(message);
    messenger.send();
}

function errorHandler(error) {
    "use strict";
    console.log("Received error " + error);
}

function pumpData() {
    "use strict";
    while (messenger.incoming()) {
        var t = messenger.get(message, true);  // true means turn binaries into strings

        // body is the body as a native JavaScript Object, useful for most real cases.
        //console.log("Content JS:");
        console.log("Received: " + message.body);

        var sender = message.body[0];
        var content = message.body[1];
        var messageId = message.body[2];
        var dClass = "message";

        if (sender === myUsername) {
            dClass += " mine bg-success";
        }

        var rendering = ("<div class=\"" + dClass + "\"><h4>" + sender + " <small>(" + messageId + ")</small></h4>" +
                        "<p>" + content + "</p></div>");

        $("#stream").prepend(rendering);

        // data is the body as a proton.Data Object, used in this case because
        // format() returns exactly the same representation as recv.c
        //console.log("Content PN:");
        //console.log(message.data);

        messenger.accept(t);
    }
    if (messenger.isStopped()) {
        message.free();
        messenger.free();
    }
}

function sendNewBark() {
    "use strict";
    var content = $("#noises").val();

    var timeStamp = Math.round(Number(new Date()) / 10.0);
    var hexStamp = ("0000000000" + timeStamp.toString(16)).slice(-10);
    var messageId = "msgjsjs" + hexStamp;

    console.log(messageId);

    var body = [new proton.Data.Binary(myUsername),
                new proton.Data.Binary(content),
                new proton.Data.Binary(messageId)];

    sendMessage("//" + barker_host + "/outbox/" + myUsername, body);

    $("#noises").val("");
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

messenger.subscribe("amqp://" + barker_host + ":5673/" + "//" + barker_host + "/inbox/" + myUsername);
