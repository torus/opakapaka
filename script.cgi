#!/usr/local/bin/gosh
; -*- scheme -*-

(use www.cgi)
(use text.tree)

(define (js-statement . x) (list x ";"))
(define (js-statement* . x) x)
(define (js-defun name args . body) (list "function" " " name args "{" body  "}"))
(define (js-anon-fun args . body) (list "function" args "{" body  "}"))
(define (js-for init condition succ . body) (list "for(" init condition succ "){" body "}"))
(define (js-for-each x . body) (list "for(" x "){" body "}"))
(define (js-if condition . body) (list "if(" condition "){" body "}"))
(define (js-else-if condition . body) (list "else" " " (apply js-if condition body)))
(define (js-else . body) (list "else{" body "}"))
(define (js-with obj . body) (list "with(" obj "){" body "}"))
(define (js-defvar v) (list "var" " " v))

(define (main args)
  (write-tree
   `(,(cgi-header :content-type "text/javascript")
     (,(js-statement
        "D = "
        (js-anon-fun
           "(output)"
           (js-statement "this.state = {}")
           (js-statement "this.outtext = " (js-anon-fun "(t)" (js-statement "output (document.createTextNode (t))")))
           (js-statement "this.out = output")
           ))
      ,(js-statement
        "D.prototype.chat_entry = "
        (js-anon-fun
          "()"
          (js-statement (js-defvar "img") "= make_dom_element (\"img\", \"src\")")
          (js-statement (js-defvar "p") "= make_dom_element (\"p\")")
          (js-statement (js-defvar "div") "= make_dom_element (\"div\")")
          (js-statement (js-defvar "br") "= make_dom_element (\"br\")")
          (js-statement (js-defvar "table") "= make_dom_element (\"table\")")
          (js-statement (js-defvar "td") "= make_dom_element (\"td\")")
          (js-statement (js-defvar "tr") "= make_dom_element (\"tr\")")
          (js-statement (js-defvar "span") "= make_dom_element (\"span\")")

          (js-statement (js-defvar "imgsrc") "= this.state.avatar_image")

          (js-statement (js-defvar "lines") "= this.state.content.split (/\\r*\\n/)")
          (js-statement (js-defvar "lines") "_with_br = [lines[0]]")
          (js-for
           (js-statement (js-defvar "i") "= 1")
           (js-statement "i < lines.length")
           (js-statement* "i ++")

           (js-statement "lines_with_br.push (br ())")
           (js-statement "lines_with_br.push (lines[i])")
           )

          (js-statement
            (js-defvar "e") "= (table ({style: \"width: 80%\"},"
            "tr ({style: \"background-color: rgb(200, 200, 255)\"},"
            "td ({width: \"50\", height: \"40\", style: \"vertical-align: top\"},"
            "imgsrc ? img ({src: imgsrc}) : null),"
            "td.apply (this, [{style: \"vertical-align: top;\"},"
            "span ({style: \"font-weight: bold;\"}, this.state.nickname),"
            "br ()].concat (lines_with_br))"
            "))) (document)")
          (js-statement "this.out (e)")
          ))

      ,(js-statement
        "D.prototype.from = "
        (js-anon-fun
         "(user)"
         (js-statement "this.state.nickname = user.nickname")
         ))

      ,(js-statement
        "D.prototype.user_by_nickname = "
        (js-anon-fun
         "(name)"
         (js-statement "return {nickname: name}")
         ))

      ,(js-statement
        "D.prototype.string = "
        (js-anon-fun
         "(elem)"
         (js-statement "return elem ? elem.nodeValue : \"\"")
         ))

      ,(js-statement
        "D.prototype.content = "
        (js-anon-fun
         "(cont)"
         (js-statement "this.state.content = cont")
         ))

      ,(js-statement
        "D.prototype.avatar_image = "
        (js-anon-fun
         "(url)"
         (js-statement "this.state.avatar_image = url")
         ))

      ,(js-statement
        "D.prototype.evaluate = "
        (js-anon-fun
         "(elem)"
         (js-if "elem.nodeType == 1"
                (js-statement (js-defvar "func") "= elem.tagName")
                (js-statement "func = func.replace (/-/g, \"_\")")

                (js-statement (js-defvar "args") "= []")
                (js-for (js-statement (js-defvar "e") "= elem.firstChild") (js-statement "e") (js-statement* "e = e.nextSibling")
                        (js-statement "args.push (this.evaluate (e))")
                        )

                (js-statement "return this[func].apply (this, args)")
                )
         (js-else
          (js-statement "return elem")
          )
         ))

      ;; "// http://james.padolsey.com/javascript/get-document-height-cross-browser/"
      ,(js-defun
        "getDocHeight" "()"
        (js-statement (js-defvar "D") "= document")
        (js-statement
         "return Math.max("
         "Math.max(D.body.scrollHeight, D.documentElement.scrollHeight),"
         "Math.max(D.body.offsetHeight, D.documentElement.offsetHeight),"
         "Math.max(D.body.clientHeight, D.documentElement.clientHeight)"
         ")")
        )

      ,(js-defun
        "ewrap" "(e)"
        (js-statement "return " (js-anon-fun "()" (js-statement "return e")))
        )

      ,(js-defun
      "initialize" "()"
      (js-statement (js-defvar "d") "= document")
      (js-statement (js-defvar "b") "= d.body")

      (js-statement (js-defvar "tags") "= [\"h1\", \"h2\", \"ul\", \"li\", \"form\", \"input\", \"textarea\", \"div\", \"p\", \"br\", \"a\"]")
      (js-statement (js-defvar "env") "= {}")
      (js-for-each (js-statement* (js-defvar "i") " " "in tags")
                   (js-statement (js-defvar "t") " " "= tags[i]")
                   (js-statement "env[t] = make_dom_element (t)")
                   )

      (js-with "env"
               (js-statement (js-defvar "head") "= (h1 (\"Web chat\")) (d)")
               (js-statement "b.appendChild (head)")
               )

      (js-statement (js-defvar "ul") "= d.createElement (\"ul\")")
      (js-statement "ul.style.padding = \"0px\"")
      (js-statement "b.appendChild (ul)")

      (js-statement (js-defvar "out") "= "
                    (js-anon-fun "(t)"
                                 (js-statement (js-defvar "x") "= d.createElement (\"li\")")
                                 (js-statement "x.style.listStyle = \"none\"")
                                 (js-statement "x.style.clear = \"both\"")
                                 (js-statement "x.appendChild (t)")
                                 (js-statement "ul.appendChild (x)")
                                 ))

      (js-statement (js-defvar "form") "_elem")
      (js-statement (js-defvar "nameinput") )
      (js-statement (js-defvar "mailinput") )
      (js-statement (js-defvar "inputtext") )
      (js-with "env"
               (js-statement "nameinput = input ({type: \"text\", size: \"20\"}) (d)")
               (js-statement "nameinput.name = \"nameinput\"")
               (js-statement "mailinput = input ({type: \"text\", size: \"50\"}) (d)")
               (js-statement "mailinput.name = \"mailinput\"")
               (js-statement "inputtext = textarea ({style: \"width:80%; height:10ex;\"}) (d)")
               (js-statement "form_elem = (form (\"Nickname: \", ewrap (nameinput),"
                             "\"Gravatar e-mail: \", ewrap (mailinput),"
                             "a ({href: \"http://gravatar.com\"}, \"What's this?\"),"
                             "br (), ewrap (inputtext),"
                             "p (\"[TIPS] Press Shift+Enter to add a new line.  \","
                             "a ({href: \"http://gravatar.com\"}, \"Get a Gravatar account to show your icon.\"))"
                             ")) (d)")

               (js-statement (js-defvar "cookied_inputs") "= {nameinput: nameinput, mailinput: mailinput}")
               (js-for-each (js-statement* (js-defvar "i") " " "in cookied_inputs")
                            (js-statement (js-defvar "e") "= cookied_inputs[i]")
                            (js-statement
                             "e.onchange = "
                             (js-anon-fun
                              "()"
                              (js-statement (js-defvar "exp") "= new Date()")
                              (js-statement "exp.setTime (new Date ().getTime () + 1000 * 60 * 60 * 24 * 14)") ; // 14 days
                              (js-statement "d.cookie = this.name + \"=\"+ escape (this.value) + \";expires=\"+ exp.toGMTString ()")
                              ))
                            )

               (js-if "d.cookie"
                      (js-statement (js-defvar "lis") "= d.cookie.split (/;\\s*/)")
                      ;; ,(js-statement "// out (d.createTextNode (d.cookie))")
                      (js-for-each (js-statement* (js-defvar "i") " " "in lis")
                                   (js-statement (js-defvar "key") "_value = lis[i].split (/=/)")
                                   (js-statement (js-defvar "key") "= key_value[0]")
                                   (js-statement (js-defvar "val") "= key_value[1]")

                                   (js-statement (js-defvar "e") "= cookied_inputs[key]")
                                   (js-if "e"
                                          (js-statement "e.value = unescape (val)")
                                          )
                                   )
                      )
               )

      ;; ,(js-statement "// alert ([form_elem, nameinput, mailinput, inputtext].join (\", \"))")

      (js-statement "form_elem.onsubmit = " (js-anon-fun "()" (js-statement "return false")))
      (js-statement "b.appendChild (form_elem)")

      (js-statement (js-defvar "stat") "= d.createElement (\"div\")")
      (js-statement (js-defvar "statcont") "= d.createElement (\"p\")")
      (js-statement (js-defvar "stattext") "= d.createTextNode (\"initiazelid.  waiting for data...\")")
      (js-statement "statcont.appendChild (stattext)")
      (js-statement "stat.appendChild (statcont)")
      (js-statement "b.appendChild (stat)")
      (js-statement "stat.style.backgroundColor = \"#cccccc\"")

      (js-statement (js-defvar "updatestat") "= "
                    (js-anon-fun "(text)"
                                 (js-statement "stattext.nodeValue = text")
                                 ))

      (js-statement "window.onkeypress = "
                    (js-anon-fun "(ev)"
                                 (js-if "ev.keyCode == 13 && !ev.shiftKey"
                                        (js-statement (js-defvar "text") "= inputtext.value")
                                        (js-statement "inputtext.value = \"\"")

                                        (js-statement "sendtext (d, inputtext, ul, nameinput.value, mailinput.value, text)")

                                        (js-statement "return false")
                                 )
                                 ))

      (js-statement (js-defvar "initial") "= true")

      (js-statement (js-defvar "pos") "= 0")
      (js-defun "get_log" "()"
                (js-statement (js-defvar "client") "= new XMLHttpRequest()")
                (js-statement "client.open(\"GET\", \"./pull.cgi?p=\" + pos, true)")
                (js-statement "client.send(null)")
                (js-statement
                 "client.onreadystatechange = "
                 (js-anon-fun "()"
                              (js-if "this.readyState == 4"
                                     (js-if "this.status == 200"
                                            (js-statement (js-defvar "doc") "= this.responseXML")
                                            (js-statement "pos = doc.getElementsByTagName (\"pos\")[0].firstChild.data")

                                            (js-for
                                             (js-statement (js-defvar "e") "= doc.getElementsByTagName (\"content\")[0].firstChild")
                                             (js-statement "e")
                                             (js-statement* "e = e.nextSibling")

                                             (js-statement (js-defvar "x") "= new D (out)")
                                             (js-statement "x.evaluate (e)")
                                             )

                                            (js-statement (js-defvar "scrollY") "= window.pageYOffset || document.body.scrollTop")
                                            (js-statement (js-defvar "threshold") "= getDocHeight () - window.innerHeight * 1.5")
                                            (js-statement "updatestat (\"new pos = \" + pos + \" scrollY = \" + scrollY + \" threshold = \" + threshold)")
                                            (js-if "initial || scrollY > threshold"
                                                   (js-statement "initial = false")
                                                   (js-statement "window.scrollTo (0, getDocHeight () - window.innerHeight)")
                                                   )

                                            (js-statement "setTimeout (get_log, 100)")
                                            ) (js-else
                                               (js-statement "updatestat (\"status = \" + this.status)")
                                               (js-statement "setTimeout (get_log, 3000)")
                                               )
                                              )
                              ))
                )
      (js-statement "get_log ()")
      )

      ,(js-defun
      "sendtext" "(d, inputtext, ul, name, mail, text)"
      (js-statement (js-defvar "chat") "_entry = make_dom_element (\"chat-entry\")")
      (js-statement (js-defvar "from") "= make_dom_element (\"from\")")
      (js-statement (js-defvar "user") "_by_nickname = make_dom_element (\"user-by-nickname\")")
      (js-statement (js-defvar "avatar") "_img = make_dom_element (\"avatar-image\")")
      (js-statement (js-defvar "string") "= make_dom_element (\"string\")")
      (js-statement (js-defvar "content") "= make_dom_element (\"content\")")

      (js-if "!(name && name.length > 0)"
             (js-statement "name = \"Anonymous\"")
             )

      (js-statement (js-defvar "avatar") "_elem = null")
      (js-if "mail && mail.length > 0"
             (js-statement "avatar_elem = avatar_img (string (\"http://www.gravatar.com/avatar/\""
                           "+ hex_md5 (mail.toLowerCase ()) + \"?s=40\"))")
             )

      (js-statement (js-defvar "doc") "= document.implementation.createDocument (\"\", \"\", null)")
      (js-statement (js-defvar "elem") "= (chat_entry (from (user_by_nickname (string (name)),"
                     "avatar_elem),"
                     "content (string (text)))) (doc)")

      (js-statement "doc.appendChild (elem)")

      (js-statement (js-defvar "client") "= new XMLHttpRequest()")
      (js-statement "client.open(\"POST\", \"./push.cgi\")")
      (js-statement "client.setRequestHeader(\"Content-Type\", \"text/xml;charset=UTF-8\")")
      (js-statement "client.send(doc)")
      )

      ,(js-defun
        "make_dom_element" "(tag)"
        (js-statement (js-defvar "attrs") "= []")
        (js-for (js-statement (js-defvar "i") "= 1") (js-statement "i < arguments.length") (js-statement* "i ++")
                (js-statement "attrs.push (arguments[i])")
                )

        (js-statement
         (js-defvar "dest") "= "
         (js-anon-fun "()"
                      (js-statement (js-defvar "args") "= arguments")
                      (js-statement (js-defvar "len") "= arguments.length")

                      (js-statement "return " (js-anon-fun "(doc)"
                      (js-statement (js-defvar "e") "= doc.createElement (tag)")
                      (js-for (js-statement (js-defvar "i") "= 0") (js-statement "i < len") (js-statement* "i ++")
                              (js-statement (js-defvar "c") "= args[i]")
                              (js-if "c == null" (js-statement "continue"))
                              (js-if "typeof (c) == \"function\""
                                     (js-statement "e.appendChild (args[i](doc))")
                                     )
                              (js-else-if "typeof (c) == \"object\""
                                          (js-for-each (js-statement* (js-defvar "j") " " "in c")
                                                       (js-statement "e.setAttribute (j, c[j])")
                                                       )
                                          )
                              (js-else
                               (js-statement ""(js-defvar "t") "= doc.createTextNode (c)")
                               (js-statement "e.appendChild (t)")
                               )
                              )
                      (js-statement "return e")
                      )
                      )))

        (js-statement "return dest")
      )

      ;; "// delay to prevent spin gear on Safari"
      ,(js-statement "setTimeout (initialize, 1)")
      )
     )
   ))
