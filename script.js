// -*- mode: java; indent-tabs-mode: nil -*-

D = function (output) {
    this.state = {};
    this.out = output;
};
D.prototype.chat_entry = function () {
    // var img = make_dom_element ("img", "src");
    // var p = make_dom_element ("p");

    this.out (this.state.avatar_image);
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
D.prototype.avatar_image = function (url) {
    this.state.avatar_image = url;
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

// http://james.padolsey.com/javascript/get-document-height-cross-browser/
function getDocHeight() {
    var D = document;
    return Math.max(
        Math.max(D.body.scrollHeight, D.documentElement.scrollHeight),
        Math.max(D.body.offsetHeight, D.documentElement.offsetHeight),
        Math.max(D.body.clientHeight, D.documentElement.clientHeight)
    );
}

function initialize () {
    var d = document;
    var b = d.body;
    var ul = d.createElement ("ul");
    var li = d.createElement ("li");
    b.appendChild (ul);

    var f = d.createElement ("form");
    b.appendChild (f);

    var nameinput = d.createElement ("input");
    nameinput.setAttribute ("type", "text");
    nameinput.setAttribute ("size", "20");
    f.appendChild (d.createTextNode ("Nickname: "));
    f.appendChild (nameinput);

    var mailinput = d.createElement ("input");
    mailinput.setAttribute ("type", "text");
    mailinput.setAttribute ("size", "50");
    f.appendChild (d.createTextNode (" Gravatar e-mail: "));
    f.appendChild (mailinput);
    f.appendChild (d.createElement ("br"));

    var inputtext = d.createElement ("textarea");
    inputtext.setAttribute ("style", "width:80%; height:10ex;");
    f.appendChild (inputtext);
    f.onsubmit = function () {return false;}

    var stat = d.createElement ("div");
    var statcont = d.createElement ("p");
    var stattext = d.createTextNode ("initiazelid");
    statcont.appendChild (stattext);
    stat.appendChild (statcont);
    b.appendChild (stat);

    var updatestat = function (text) {
        stattext.nodeValue = text;
    };

    var out = function (t) {
        var x = d.createElement ("li");
        x.appendChild (d.createTextNode (t));
        ul.appendChild (x);
    }

    window.onkeypress = function (ev) {
        if (ev.keyCode == 13) {
            var text = inputtext.value;
            inputtext.value = "";

            // out (mailinput.value)
            sendtext (d, inputtext, ul, nameinput.value, mailinput.value, text);

            return false;
        }
    };

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

                    for (var e = doc.getElementsByTagName ("content")[0].firstChild; e; e = e.nextSibling) {
                        var x = new D (out);
                        x.evaluate (e);
                    }

                    var scrollY = window.pageYOffset || document.body.scrollTop;
                    var threshold = getDocHeight () - window.innerHeight * 1.5;
                    updatestat ("new pos = " + pos + " scrollY = " + scrollY + " threshold = " + threshold);
                    if (scrollY > threshold) {
                        window.scrollTo (0, getDocHeight () - window.innerHeight);
                    }

                    get_log ();
                } else {
                    updatestat ("status = " + this.status);
                    setTimeout (get_log, 3000);
                }
            }
        }
    }
    get_log ();
}

function sendtext (d, inputtext, ul, name, mail, text) {
    var chat_entry = make_dom_element ("chat-entry");
    var from = make_dom_element ("from");
    var user_by_nickname = make_dom_element ("user-by-nickname");
    var avatar_img = make_dom_element ("avatar-image");
    var string = make_dom_element ("string");
    var content = make_dom_element ("content");

    if (!(name && name.length > 0)) {
        name = "Anonymous";
    }

    var avatar_elem = null;
    if (mail && mail.length > 0) {
        avatar_elem = avatar_img (string ("http://www.gravatar.com/avatar/"
                                          + hex_md5 (mail.toLowerCase ()) + "?s=40"));
    }

    var doc = document.implementation.createDocument ("", "", null);
    var elem = (chat_entry (from (user_by_nickname (string (name)),
                                  avatar_elem),
                            content (string (text)))) (doc);

    doc.appendChild (elem);

    var client = new XMLHttpRequest();
    client.open("POST", "./push.cgi");
    client.setRequestHeader("Content-Type", "text/xml;charset=UTF-8");
    client.send(doc);
}

function make_dom_element (tag) {
    var attrs = [];
    for (var i = 1; i < arguments.length; i ++) {
        attrs.push (arguments[i]);
    }

    var dest = function () {
        var args = arguments;
        var len = arguments.length;

        return function (doc) {
            var e = doc.createElement (tag);
            for (var i = 0; i < len; i ++) {
                var c = args[i];
                if (c == null) continue;
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

    return dest;
};

// delay to prevent spin gear on Safari
setTimeout (initialize, 1);
