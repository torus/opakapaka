// -*- mode: java; indent-tabs-mode: nil -*-

D = function (output) {
    this.state = {};
    this.out = output;
};
D.prototype.chat_entry = function () {
    this.out (this.state.nickname + ": " + this.state.content);
};
D.prototype.from = function (user) {
    this.state.nickname = user.nickname;
};
D.prototype.user_by_nickname = function (name) {
    return {nickname: name};
};
D.prototype.string = function (elem) {
    return elem ? elem.nodeValue : "";
};
D.prototype.content = function (cont) {
    this.state.content = cont;
};

D.prototype.evaluate = function (elem) {
    // this.out (elem);
    if (elem.nodeType == 1) {
        var func = elem.tagName;
        func = func.replace (/-/g, "_");

        // this.out (func);

        var args = [];
        for (var e = elem.firstChild; e; e = e.nextSibling) {
            args.push (this.evaluate (e));
        }

        return this[func].apply (this, args);
    } else {
        return elem;
    }
};

function onload () {
    var d = document;
    var b = d.body;
    var ul = d.createElement ("ul");
    var li = d.createElement ("li");
    b.appendChild (ul);

    var f = d.createElement ("form");
    b.appendChild (f);

    var nameinput = d.createElement ("input");
    nameinput.setAttribute ("type", "text");
    nameinput.setAttribute ("size", "30");
    f.appendChild (d.createTextNode ("Nickname: "));
    f.appendChild (nameinput);
    f.appendChild (d.createElement ("br"));

    var inputtext = d.createElement ("textarea");
    inputtext.setAttribute ("style", "width:80%; height:10ex;");

    f.appendChild (inputtext);

    f.onsubmit = function () {return false;}

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
                        var x = new D (out);
                        x.evaluate (e);
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
    var chat_entry = make_dom_element ("chat-entry");
    var from = make_dom_element ("from");
    var user_by_nickname = make_dom_element ("user-by-nickname");
    var string = make_dom_element ("string");
    var content = make_dom_element ("content");

    var doc = document.implementation.createDocument ("", "", null);
    var elem = (chat_entry (from (user_by_nickname (string ("unnamed"))),
                            content (string (text)))) (doc);

    doc.appendChild (elem);

    var client = new XMLHttpRequest();
    client.open("POST", "./push.cgi");
    client.setRequestHeader("Content-Type", "text/xml;charset=UTF-8");
    client.send(doc);
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
