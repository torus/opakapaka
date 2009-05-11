// -*- mode: java; indent-tabs-mode: nil -*-

D = function (output) {
    this.state = {};
    this.outtext = function (t) {output (document.createTextNode (t))};
    this.out = output;
};
D.prototype.chat_entry = function () {
    var img = make_dom_element ("img", "src");
    var p = make_dom_element ("p");
    var div = make_dom_element ("div");
    var br = make_dom_element ("br");
    var table = make_dom_element ("table");
    var td = make_dom_element ("td");
    var tr = make_dom_element ("tr");

    var imgsrc = this.state.avatar_image;

    var e = (table (tr ({style: "background-color: rgb(200, 200, 255)"},
                        td ({width: "50", height: "40", style: "vertical-align: top"},
                            imgsrc ? img ({src: imgsrc}) : null),
                        td ({style: "vertical-align: top"},
                            this.state.nickname, br (),
                            this.state.content)
                        ))) (document);
    this.out (e);
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
    if (elem.nodeType == 1) {
        var func = elem.tagName;
        func = func.replace (/-/g, "_");

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

function ewrap (e) {
    return function () {return e};
}

function initialize () {
    var d = document;
    var b = d.body;

    var tags = ["ul", "li", "form", "input", "textarea", "div", "p", "br"];
    var env = {};
    for (var i in tags) {
        var t = tags[i];
        env[t] = make_dom_element (t);
    }

    var ul = d.createElement ("ul");
    b.appendChild (ul);

    var form_elem;
    var nameinput;
    var mailinput;
    var inputtext;
    with (env) {
        nameinput = input ({type: "text", size: "20"}) (d);
        mailinput = input ({type: "text", size: "50"}) (d);
        inputtext = textarea ({style: "width:80%; height:10ex;"}) (d);
        form_elem = (form ("Nickname: ", ewrap (nameinput),
                           " Gravatar e-mail: ", ewrap (mailinput),
                           br (), ewrap (inputtext)
                           )) (d);
    }

    // alert ([form_elem, nameinput, mailinput, inputtext].join (", "));

    form_elem.onsubmit = function () {return false;}
    b.appendChild (form_elem);

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
        x.style.listStyle = "none";
        x.style.clear = "both";
        x.appendChild (t);
        ul.appendChild (x);
    }

    window.onkeypress = function (ev) {
        if (ev.keyCode == 13 && !ev.shiftKey) {
            var text = inputtext.value;
            inputtext.value = "";

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
                } else if (typeof (c) == "object") {
                    for (var j in c) {
                        e.setAttribute (j, c[j]);
                    }
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

function test_function () {
    var img = make_dom_element ("img");
    var p = make_dom_element ("p");
    var div = make_dom_element ("div");

    var e = (div ({"class": "hoge", id: "fuga"},
                  img ({src: "http://hoge/fuga.jpg"}),
                  p ("anananan"))) (document);
    alert (e);

    document.body.appendChild (e);
}

// test_function ()

// delay to prevent spin gear on Safari
setTimeout (initialize, 1);
