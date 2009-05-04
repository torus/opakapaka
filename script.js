// -*- mode: java; indent-tabs-mode: nil -*-

function onload () {
    var d = document;
    var b = d.body;
    var ul = d.createElement ("ul");
    var li = d.createElement ("li");
    b.appendChild (ul);

    var f = d.createElement ("form");
    b.appendChild (f);

    var inputtext = d.createElement ("textarea");
    inputtext.setAttribute ("type", "text");
    inputtext.setAttribute ("style", "width:80%; height:10ex;");

    f.appendChild (inputtext);

    window.onkeypress = function (ev) {
        if (ev.keyCode == 13) {
            var text = inputtext.value;
            inputtext.value = "";

            sendtext (d, inputtext, ul, text);

            return false;
        }
    };

    var out = function (t) {
        var x = d.createElement ("li");
        x.appendChild (d.createTextNode (t));
        ul.appendChild (x);
    }

    var pos = 0;
    function get_log () {
        var client = new XMLHttpRequest();
        client.open("GET", "./pull.cgi?p=" + pos, true);
        client.send(null);
        client.onreadystatechange = function() {
            if (this.readyState == 4) {
                if (this.status == 200) {
                    var doc = this.responseXML;
                    pos = doc.getElementsByTagName ("pos")[0].firstChild.data;
                    out ("new pos = " + pos);
                    for (var e = doc.getElementsByTagName ("content")[0].firstChild; e; e = e.nextSibling) {
                        var name = e.getElementsByTagName ("user-by-nickname")[0].firstChild.firstChild.data;
                        var mesg = e.getElementsByTagName ("content")[0].firstChild.firstChild.data;
                        out (name + ": " + mesg);
                    }
                    get_log ();
                } else {
                    out ("status = " + this.status);
                    setTimeout (get_log, 3000);
                }
            }
        }
    }
    get_log ();
}

function sendtext (d, inputtext, ul, text) {
    // var out = function (t) {
    //     var x = d.createElement ("li");
    //     x.appendChild (d.createTextNode (t));
    //     ul.appendChild (x);
    // }

    var chat_entry = make_dom_element ("chat-entry");
    var from = make_dom_element ("from");
    var user_by_nickname = make_dom_element ("user-by-nickname");
    var string = make_dom_element ("string");
    var content = make_dom_element ("content");

    var doc = document.implementation.createDocument ("", "", null);
    var elem = (chat_entry (from (user_by_nickname (string ("unnamed"))),
                            content (string (text)))) (doc);

    doc.appendChild (elem);

    // var s = new XMLSerializer();
    // var serialized = s.serializeToString (doc);

    var client = new XMLHttpRequest();
    client.open("POST", "./push.cgi");
    client.setRequestHeader("Content-Type", "text/xml;charset=UTF-8");
    client.send(doc);

    // client.send(serialized);

    // out (serialized);
}

function make_dom_element (tag) {
    return function () {
        var args = arguments;
        var len = arguments.length;

        return function (doc) {
            var e = doc.createElement (tag);
            for (var i = 0; i < len; i ++) {
                var c = args[i];
                if (typeof (c) == "function") {
                    e.appendChild (args[i](doc));
                } else {
                    var t = doc.createTextNode (c);
                    e.appendChild (t);
                }
            }
            return e;
        }
    }
};
