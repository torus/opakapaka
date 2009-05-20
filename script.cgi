#!/usr/local/bin/gosh
; -*- scheme -*-

(use www.cgi)
(use text.tree)

(define (js-statement . x) (list x ";"))

(define (main args)
  (write-tree
   `(,(cgi-header :content-type "text/javascript")
     (;; "// -*- mode: java; indent-tabs-mode: nil -*-"

      "D = function (output) {"
      ,(js-statement "this.state = {}")
      ,(js-statement "this.outtext = function (t) {output (document.createTextNode (t))}")
      ,(js-statement "this.out = output")
      "};"
      "D.prototype.chat_entry = function () {"
      ,(js-statement "var img = make_dom_element (\"img\", \"src\")")
      ,(js-statement "var p = make_dom_element (\"p\")")
      ,(js-statement "var div = make_dom_element (\"div\")")
      ,(js-statement "var br = make_dom_element (\"br\")")
      ,(js-statement "var table = make_dom_element (\"table\")")
      ,(js-statement "var td = make_dom_element (\"td\")")
      ,(js-statement "var tr = make_dom_element (\"tr\")")
      ,(js-statement "var span = make_dom_element (\"span\")")

      ,(js-statement "var imgsrc = this.state.avatar_image")

      ,(js-statement "var lines = this.state.content.split (/\\r*\\n/)")
      ,(js-statement "var lines_with_br = [lines[0]]")
      "    for (var i = 1; i < lines.length; i ++) {"
      ,(js-statement "lines_with_br.push (br ())")
      ,(js-statement "lines_with_br.push (lines[i])")
      "    }"

      ,(js-statement
        "var e = (table ({style: \"width: 80%\"},"
        "tr ({style: \"background-color: rgb(200, 200, 255)\"},"
        "td ({width: \"50\", height: \"40\", style: \"vertical-align: top\"},"
        "imgsrc ? img ({src: imgsrc}) : null),"
        "td.apply (this, [{style: \"vertical-align: top;\"},"
        "span ({style: \"font-weight: bold;\"}, this.state.nickname),"
        "br ()].concat (lines_with_br))"
        "))) (document)")
      ,(js-statement "this.out (e)")
      "};"
      "D.prototype.from = function (user) {"
      ,(js-statement "this.state.nickname = user.nickname")
      "};"
      "D.prototype.user_by_nickname = function (name) {"
      ,(js-statement "return {nickname: name}")
      "};"
      "D.prototype.string = function (elem) {"
      ,(js-statement "return elem ? elem.nodeValue : \"\"")
      "};"
      "D.prototype.content = function (cont) {"
      ,(js-statement "this.state.content = cont")
      "};"
      "D.prototype.avatar_image = function (url) {"
      ,(js-statement "this.state.avatar_image = url")
      "};"

      "D.prototype.evaluate = function (elem) {"
      "if (elem.nodeType == 1) {"
      ,(js-statement "var func = elem.tagName")
      ,(js-statement "func = func.replace (/-/g, \"_\")")

      ,(js-statement "var args = []")
      "for (var e = elem.firstChild; e; e = e.nextSibling) {"
      ,(js-statement "args.push (this.evaluate (e))")
      "}"

      ,(js-statement "return this[func].apply (this, args)")
      "} else {"
      ,(js-statement "return elem")
      "}"
      "};"

      ;; "// http://james.padolsey.com/javascript/get-document-height-cross-browser/"
      "function getDocHeight() {"
      ,(js-statement "var D = document")
      ,(js-statement
        "return Math.max("
        "Math.max(D.body.scrollHeight, D.documentElement.scrollHeight),"
        "Math.max(D.body.offsetHeight, D.documentElement.offsetHeight),"
        "Math.max(D.body.clientHeight, D.documentElement.clientHeight)"
        ")")
      "}"

      "function ewrap (e) {"
      ,(js-statement "return function () {return e}")
      "}"

      "function initialize () {"
      ,(js-statement "var d = document")
      ,(js-statement "var b = d.body")

      ,(js-statement "var tags = [\"h1\", \"h2\", \"ul\", \"li\", \"form\", \"input\", \"textarea\", \"div\", \"p\", \"br\", \"a\"]")
      ,(js-statement "var env = {}")
      "for (var i in tags) {"
      ,(js-statement "var t = tags[i]")
      ,(js-statement "env[t] = make_dom_element (t)")
      "}"

      "with (env) {"
      ,(js-statement "var head = (h1 (\"Web chat\")) (d)")
      ,(js-statement "b.appendChild (head)")
      "}"

      ,(js-statement "var ul = d.createElement (\"ul\")")
      ,(js-statement "ul.style.padding = \"0px\"")
      ,(js-statement "b.appendChild (ul)")

      ,(js-statement "var out = function (t) {"
                     (js-statement "var x = d.createElement (\"li\")")
                     (js-statement "x.style.listStyle = \"none\"")
                     (js-statement "x.style.clear = \"both\"")
                     (js-statement "x.appendChild (t)")
                     (js-statement "ul.appendChild (x)")
                     "}")

      ,(js-statement "var form_elem")
      ,(js-statement "var nameinput")
      ,(js-statement "var mailinput")
      ,(js-statement "var inputtext")
      "with (env) {"
      ,(js-statement "nameinput = input ({type: \"text\", size: \"20\"}) (d)")
      ,(js-statement "nameinput.name = \"nameinput\"")
      ,(js-statement "mailinput = input ({type: \"text\", size: \"50\"}) (d)")
      ,(js-statement "mailinput.name = \"mailinput\"")
      ,(js-statement "inputtext = textarea ({style: \"width:80%; height:10ex;\"}) (d)")
      ,(js-statement "form_elem = (form (\"Nickname: \", ewrap (nameinput),"
                     "\"Gravatar e-mail: \", ewrap (mailinput),"
                     "a ({href: \"http://gravatar.com\"}, \"What's this?\"),"
                     "br (), ewrap (inputtext),"
                     "p (\"[TIPS] Press Shift+Enter to add a new line.  \","
                     "a ({href: \"http://gravatar.com\"}, \"Get a Gravatar account to show your icon.\"))"
                     ")) (d)")

      ,(js-statement "var cookied_inputs = {nameinput: nameinput, mailinput: mailinput}")
      "for (var i in cookied_inputs) {"
      ,(js-statement "var e = cookied_inputs[i]")
      ,(js-statement
        "e.onchange = function () {"
        (js-statement "var exp = new Date()")
        (js-statement "exp.setTime (new Date ().getTime () + 1000 * 60 * 60 * 24 * 14)") ; // 14 days
        (js-statement "d.cookie = this.name + \"=\"+ escape (this.value) + \";expires=\"+ exp.toGMTString ()")

        ;; "// out (d.createTextNode (d.cookie));"
        "}")
      "}"

      "if (d.cookie) {"
      ,(js-statement "var lis = d.cookie.split (/;\\s*/)")
      ;; ,(js-statement "// out (d.createTextNode (d.cookie))")
      "for (var i in lis) {"
      ;; ,(js-statement "// out (d.createTextNode (\"cookie: \" + i + \" = \" + lis[i]))")
      ,(js-statement "var key_value = lis[i].split (/=/)")
      ,(js-statement "var key = key_value[0]")
      ,(js-statement "var val = key_value[1]")

      ;; ,(js-statement "// out (d.createTextNode (\"cookie key val: \" + key + \" = \" + val))")

      ,(js-statement "var e = cookied_inputs[key]")
      "if (e) {"
      ,(js-statement "e.value = unescape (val)")
      "}"
      "}"
      "}"
      "}"

      ;; ,(js-statement "// alert ([form_elem, nameinput, mailinput, inputtext].join (\", \"))")

      ,(js-statement "form_elem.onsubmit = function () {return false;}")
      ,(js-statement "b.appendChild (form_elem)")

      ,(js-statement "var stat = d.createElement (\"div\")")
      ,(js-statement "var statcont = d.createElement (\"p\")")
      ,(js-statement "var stattext = d.createTextNode (\"initiazelid.  waiting for data...\")")
      ,(js-statement "statcont.appendChild (stattext)")
      ,(js-statement "stat.appendChild (statcont)")
      ,(js-statement "b.appendChild (stat)")
      ,(js-statement "stat.style.backgroundColor = \"#cccccc\"")

      ,(js-statement "var updatestat = function (text) {"
                     (js-statement "stattext.nodeValue = text")
                     "}")

      ,(js-statement "window.onkeypress = function (ev) {"
                     "if (ev.keyCode == 13 && !ev.shiftKey) {"
                     (js-statement "var text = inputtext.value")
                     (js-statement "inputtext.value = \"\"")

                     (js-statement "sendtext (d, inputtext, ul, nameinput.value, mailinput.value, text)")

                     (js-statement "return false")
                     "}"
                     "}")

      ,(js-statement "var initial = true")

      ,(js-statement "var pos = 0")
      "function get_log () {"
      ,(js-statement "var client = new XMLHttpRequest()")
      ,(js-statement "client.open(\"GET\", \"./pull.cgi?p=\" + pos, true)")
      ,(js-statement "client.send(null)")
      ,(js-statement
        "client.onreadystatechange = function() {"
        "if (this.readyState == 4) {"
        "if (this.status == 200) {"
        (js-statement "var doc = this.responseXML")
        (js-statement "pos = doc.getElementsByTagName (\"pos\")[0].firstChild.data")

        "for (var e = doc.getElementsByTagName (\"content\")[0].firstChild; e; e = e.nextSibling) {"
        (js-statement "var x = new D (out)")
        (js-statement "x.evaluate (e)")
        "}"

        (js-statement "var scrollY = window.pageYOffset || document.body.scrollTop")
        (js-statement "var threshold = getDocHeight () - window.innerHeight * 1.5")
        (js-statement "updatestat (\"new pos = \" + pos + \" scrollY = \" + scrollY + \" threshold = \" + threshold)")
        "if (initial || scrollY > threshold) {"
        (js-statement "initial = false")
        (js-statement "window.scrollTo (0, getDocHeight () - window.innerHeight)")
        "}"

        (js-statement "setTimeout (get_log, 100)")
        "} else {"
        (js-statement "updatestat (\"status = \" + this.status)")
        (js-statement "setTimeout (get_log, 3000)")
        "}"
        "}"
        "}")
      "}"
      ,(js-statement "get_log ()")
      "}"

      "function sendtext (d, inputtext, ul, name, mail, text) {"
      ,(js-statement "var chat_entry = make_dom_element (\"chat-entry\")")
      ,(js-statement "var from = make_dom_element (\"from\")")
      ,(js-statement "var user_by_nickname = make_dom_element (\"user-by-nickname\")")
      ,(js-statement "var avatar_img = make_dom_element (\"avatar-image\")")
      ,(js-statement "var string = make_dom_element (\"string\")")
      ,(js-statement "var content = make_dom_element (\"content\")")

      "if (!(name && name.length > 0)) {"
      ,(js-statement "name = \"Anonymous\"")
      "}"

      ,(js-statement "var avatar_elem = null")
      "if (mail && mail.length > 0) {"
      ,(js-statement "avatar_elem = avatar_img (string (\"http://www.gravatar.com/avatar/\""
                     "+ hex_md5 (mail.toLowerCase ()) + \"?s=40\"))")
      "}"

      ,(js-statement "var doc = document.implementation.createDocument (\"\", \"\", null)")
      ,(js-statement "var elem = (chat_entry (from (user_by_nickname (string (name)),"
                     "avatar_elem),"
                     "content (string (text)))) (doc)")

      ,(js-statement "doc.appendChild (elem)")

      ,(js-statement "var client = new XMLHttpRequest()")
      ,(js-statement "client.open(\"POST\", \"./push.cgi\")")
      ,(js-statement "client.setRequestHeader(\"Content-Type\", \"text/xml;charset=UTF-8\")")
      ,(js-statement "client.send(doc)")
      "}"

      "function make_dom_element (tag) {"
      ,(js-statement "var attrs = []")
      "for (var i = 1; i < arguments.length; i ++) {"
      ,(js-statement "attrs.push (arguments[i])")
      "}"

      ,(js-statement
        "var dest = function () {"
        (js-statement "var args = arguments")
        (js-statement "var len = arguments.length")

        "return function (doc) {"
        (js-statement "var e = doc.createElement (tag)")
        "for (var i = 0; i < len; i ++) {"
        (js-statement "var c = args[i]")
        "if (c == null) continue;"
        "if (typeof (c) == \"function\") {"
        (js-statement "e.appendChild (args[i](doc))")
        "} else if (typeof (c) == \"object\") {"
        "for (var j in c) {"
        (js-statement "e.setAttribute (j, c[j])")
        "}"
        "} else {"
        (js-statement "var t = doc.createTextNode (c)")
        (js-statement "e.appendChild (t)")
        "}"
        "}"
        (js-statement "return e")
        "}"
        "}")

      ,(js-statement "return dest")
      "}"

      "function test_function () {"
      ,(js-statement "var img = make_dom_element (\"img\")")
      ,(js-statement "var p = make_dom_element (\"p\")")
      ,(js-statement "var div = make_dom_element (\"div\")")

      ,(js-statement
        "var e = (div ({\"class\": \"hoge\", id: \"fuga\"},"
        "img ({src: \"http://hoge/fuga.jpg\"}),"
        "p (\"anananan\"))) (document)")
      ,(js-statement "alert (e)")

      ,(js-statement "document.body.appendChild (e)")
      "}"

      ;; "// test_function ()"

      ;; "// delay to prevent spin gear on Safari"
      ,(js-statement "setTimeout (initialize, 1)")
      )
     )
   ))
