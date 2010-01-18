#!/usr/bin/env gosh
; -*- scheme -*-

(use www.cgi)
(use text.tree)

(add-load-path ".")

(load "file")
(load "script-lib")
(load "config")

(load "opakapaka.conf.cgi")

(use js)

(define (script-body)
  `(,(js-let-syms (output update-file)
                  (js 
                   `(D =
                       (function
                        (,output ,update-file)
                        this .. state = (^^) //
                        this .. outtext = (function (t) (,output -> (document.createTextNode -> t))) //
                        this .. out = ,output //
                        this .. update_logfile = ,update-file //
                        ))))

    ,(define-tag ("system")
       (js-statement (js-call (js-. 'this 'update_logfile)
                              (js-. 'this 'newfile))))

    ,(define-tag ("new_file" filename)
       (js-statement (js-. 'this 'newfile) "=" filename))
    ,(js-statement "PREVIOUS_USER=null")
    ,(define-tag ("chat_entry")
       (js-let
        ((img (js-call 'make_dom_element "\"img\""))
         (p (js-call 'make_dom_element "\"p\""))
         (div (js-call 'make_dom_element "\"div\""))
         (br (js-call 'make_dom_element "\"br\""))
         (table (js-call 'make_dom_element "\"table\""))
         (td (js-call 'make_dom_element "\"td\""))
         (tr (js-call 'make_dom_element "\"tr\""))
         (span (js-call 'make_dom_element "\"span\""))
         (a (js-call 'make_dom_element "\"a\""))
         (imgsrc "this.state.avatar_image")
         (lines "this.state.content.split (/\\r*\\n/)")
         (lines_with_br (list "[" lines "[0]]")))

        (js (js-let-syms
             (i)
             `(for (var ,i = 1 // ,i < ,lines .. length // ,i ++)
                   ((,lines_with_br .. push) -> (,br ->)) //
                   ((,lines_with_br .. push) -> (,lines (<> i))))))

        (js-let
         ((filtered "[]"))
         (js-for/defvar
          ((i "0"))
          (js-statement i "<" lines_with_br ".length")
          (js-statement* i "++")

          (let1 regexmatch ".match(/^(.*?)(http:\\/\\/[^\\s]*)(.*)$/)"
            (js-let
             ((l `(,lines_with_br "[" ,i "]")))
             (js-if
              `(,(js-call 'typeof l) "==\"string\"")
              (js-let
               ((x `(,l ,regexmatch)))
               `("while(" ,x "){"
                 ,(js-statement l "=" x "[3]")
                 ,(js-statement filtered ".push(" x "[1])")
                 ,(js-statement filtered ".push(" a  "({href: " x "[2]}, " x "[2]))")
                 ,(js-statement x "=" l regexmatch)
                 "}"
                 )))
             (js-statement filtered ".push(" l ")")
             )
            ))

         (js-statement
          (js-let
           ((prev '("PREVIOUS_USER"))
            (new `("this.state.nickname + " ,imgsrc))
            (e (js-?: `(,prev "!=" ,new)
                      `("(" ,table "({style: \"width: 100%; max-width: 100ex\"},"
                        ,tr "({style: \"background-color: rgb(230, 230, 255)\"},"
                        ,td "({width: \"50\", height: \"40\", style: \"vertical-align: top\"},"
                        ,imgsrc "?" ,img "({src:" ,imgsrc "}) : null),"
                        ,td ".apply (this, [{style: \"vertical-align: top;\"},"
                        ,span "({style:\"font-weight: bold;\"}, this.state.nickname),"
                        ,span "({style:\"font-size:small;padding-left:3em\"}, "
                        "(this.state.date ? (this.state.link?" ,a "({href:this.state.link},this.state.date.toLocaleString()):this.state.date.toLocaleString()) : \"\")),"
                        ,br "()].concat (" ,filtered "))"
                        "))) (document)")
                      `("(" ,table "({style: \"width: 100%; max-width: 100ex\"},"
                        ,tr "({style: \"background-color: rgb(230, 230, 255)\"},"
                        ,td "({width: \"50\", style: \"vertical-align: top\"}),"
                        ,td ".apply (this, [{style: \"vertical-align: top;\"}].concat (" ,filtered "))"
                        "))) (document)"))))
           (js-statement "this.out (" e" )")
           (js-statement "PREVIOUS_USER=" new)))
         )))

    ,(js-statement
      "D.prototype.from = "
      (js-function
       (user)
       (js-statement "this.state.nickname =" user ".nickname")
       ))

    , (js-statement
       "D.prototype.date="
       (js-function
        (date)
        (js-statement "this.state.date=" date)))

      , (js-statement
         "D.prototype.posix_time="
         (js-function
          (t)
          (js-let
           ((date "new Date"))
           (js-statement date ".setTime(parseInt(" t ".nodeValue)*1000)")
           (js-statement "return " date))))

        ,(define-tag ("link" file pos)
           (js-statement "this.state.link=\"./archive.cgi?q=\"+" file "+\"#\"+" pos))

        ,(define-tag ("file" elem)
           (js-statement "return " elem " ? " elem ".nodeValue : \"\""))

        ,(define-tag ("pos" elem)
           (js-statement "return " elem " ? " elem ".nodeValue : \"\""))

        ,(js-statement
          "D.prototype.user_by_nickname = "
          (js-function
           (name)
           (js-statement "return {nickname:" name "}")
           ))

        ,(js-statement
          "D.prototype.string = "
          (js-function
           (elem)
           (js-statement "return " elem " ? " elem ".nodeValue : \"\"")
           ))

        ,(js-statement
          "D.prototype.content = "
          (js-function
           (cont)
           (js-statement "this.state.content =" cont)
           ))

        ,(js-statement
          "D.prototype.avatar_image = "
          (js-function
           (url)
           (js-statement "this.state.avatar_image =" url)
           ))

        ,(js-statement
          "D.prototype.evaluate = "
          (js-function
           (elem)
           (js-if
            `(,elem ".nodeType == 1")
            (js-let
             ((func `(,elem ".tagName")))
             (js-statement func "=" func ".replace (/-/g, \"_\")")

             (js-let
              ((args "[]"))
              (js-for/defvar
               ((e `(,elem ".firstChild")))
               (js-statement e) (js-statement* e "=" e ".nextSibling")
               (js-statement args ".push (this.evaluate (" e "))")
               )

              (js-statement "return this[" func "]?this[" func "].apply (this," args "):null")
              )))
           (js-else
            (js-statement "return " elem "")
            )
           ))

        ;; "// http://james.padolsey.com/javascript/get-document-height-cross-browser/"
        ,(js-defun
          "getDocHeight" ()
          (js-let
           ((D "document"))
           (js-statement
            "return Math.max("
            "Math.max(" D ".body.scrollHeight," D ".documentElement.scrollHeight),"
            "Math.max(" D ".body.offsetHeight," D ".documentElement.offsetHeight),"
            "Math.max(" D ".body.clientHeight," D ".documentElement.clientHeight)"
            ")")
           ))

        ,(js-defun
          "ewrap" (e)
          (js-statement "return " (js-function () (js-statement "return " e)))
          )

        ,(js-defun
          "initialize" ()
          (js-let
           ((d "document")
            (b `(,d ".body"))
            (unread-count)
            (active 'true)
            (orig-title (js `(,d .. title)))
            (tags "[\"h1\", \"h2\", \"ul\", \"li\", \"form\", \"input\", \"textarea\", \"div\", \"p\", \"br\", \"a\"]")
            (env "{}"))

           (js `(window.onblur = (function
                                  ()
                                  ,unread-count = 0 //
                                  ,active = false //
                                  window.onfocus = (function
                                                    ()
                                                    ,d .. title = ,orig-title //
                                                    ,active = true //) //) //))

           (js-for/iter
            (i -> tags)
            (js-let ((t `(,tags "[" ,i "]")))
                    (js-statement env "[" t "] = make_dom_element (" t ")")
                    ))

           (js-with
            env
            (js-let ((head (js `((h1 -> ,(config-get 'title)) -> ,d))))
                    (js `((,b .. appendChild) -> ,head))
                    ))

           (js-let
            ((ul `(,d ".createElement (\"ul\")")))
            (js-statement ul ".style.padding = \"0px\"")
            (js-statement b ".appendChild (" ul ")")

            (js-let
             ((out
               (js-function (t)
                            (js-let ((x `(,d ".createElement (\"li\")")))
                                    (js-statement x ".style.listStyle = \"none\"")
                                    (js-statement x ".style.clear = \"both\"")
                                    (js-statement x ".appendChild (" t ")")
                                    (js-statement ul ".appendChild (" x ")")
                                    (js `(if (! ,active)
                                             ,unread-count ++ //
                                             ,d .. title = "[" + ,unread-count + "] " + ,orig-title //))
                                    ))))

             (js-let
              ((form_elem) (nameinput) (mailinput) (inputtext) (submit))
              (js-with
               env
               (js `(,nameinput = ((input -> (^^ (type "text") (size "20"))) -> ,d) //))
               (js `(,nameinput .. name = "nameinput" //))
               (js `(,mailinput = ((input -> (^^ (type "text") (size "40"))) -> ,d) //))
               (js `(,mailinput .. name = "mailinput" //))
               (js `(,submit = ((input -> (^^ (type "submit") (value "say"))) -> ,d) //))
               (js `(,inputtext = ((textarea
                                    -> (^^ (style "width:100%; max-width:100ex; height:10ex;")))
                                   -> ,d) //))
               (js `(,form_elem = ((form -> "Nickname: " (ewrap -> ,nameinput)
                                         (br ->) "E-mail (optional.  used only for icon): " (ewrap -> ,mailinput)
                                         (br ->) (ewrap -> ,inputtext)
                                         (br ->) (ewrap -> ,submit)
                                         (p -> "[TIPS] Press Shift+Enter to add a new line.  "
                                            (a -> (^^ (href "http://gravatar.com")) "Get a Gravatar account to show your icon."))
                                         (p -> (a -> (^^ (href "./archive.cgi")) "Log archive"))
                                         (p -> "Powered by " (a -> (^^ (href "http://github.com/torus/opakapaka")) "Opakapaka chat system")))
                                   -> ,d) //))

               (js-let
                ((cookied_inputs `("{nameinput: " ,nameinput ", mailinput: " ,mailinput "}")))
                (js-for/iter
                 (i -> cookied_inputs)
                 (js-let
                  ((e `(,cookied_inputs "[" ,i "]")))
                  (js-statement
                   e ".onchange = "
                   (js-function
                    ()
                    (js-let
                     ((exp "new Date()"))
                     (js-statement exp ".setTime (new Date ().getTime () + 1000 * 60 * 60 * 24 * 14)") ; // 14 days
                     (js-statement d ".cookie = this.name + \"=\"+ escape (this.value) + \";expires=\"+"
                                   exp ".toGMTString ()")
                     ))
                   )))

                (js-if
                 `(,d ".cookie")
                 (js-let
                  ((lis `(,d ".cookie.split (/;\\s*/)")))
                  (js-for/iter
                   (i -> lis)
                   (js-let
                    ((key_value `(,lis "[" ,i "].split (/=/)"))
                     (key `(,key_value "[0]"))
                     (val `(,key_value "[1]")))

                    (js-let
                     ((e `( ,cookied_inputs "[" ,key "]")))
                     (js-if e
                            (js-statement e ".value = unescape (" val ")")
                            (js `(((,e .. onchange) ->) //))
                            #;(js `((alert -> ,e) //)))
                            )))
                   ))
                 ))

               (js `(,form_elem .. onsubmit =
                                (function
                                 ()
                                 var text = ,inputtext .. value //
                                 (if (text.length > 0)
                                     ,inputtext .. value = "" //
                                     (sendtext -> ,d ,inputtext ,ul
                                               (,nameinput .. value) (,mailinput .. value) text) //
                                               )
                                 return false //) //))
               (js-statement b ".appendChild (" form_elem ")")

               (js-let
                ((stat `(,d ".createElement (\"div\")"))
                 (statcont `(,d ".createElement (\"p\")"))
                 (stattext `(,d ".createTextNode (\"initialized.  waiting for data...\")")))
                (js-statement statcont ".appendChild (" stattext ")")
                (js-statement stat ".appendChild (" statcont ")")
                (js-statement b ".appendChild (" stat ")")
                (js-statement stat ".style.backgroundColor = \"#cccccc\"")

                (js-let
                 ((updatestat (js-function (text)
                                           (js-statement stattext ".nodeValue =" text)
                                           )))

                 (js-statement
                  "window.onkeypress = "
                  (js-function
                   (ev)
                   (js-if
                    `(,ev ".keyCode == 13 && !" ,ev ".shiftKey")
                    (js `(return (,form_elem .. (onsubmit ->)) //))
                    )))

                 (js-let
                  ((initial "true")
                   (pos "0")
                   (file))
                  (js-defun
                   "get_log" ()
                   (js-let
                    ((client "new XMLHttpRequest()"))
                    (js `(((,client .. open) ->
                           "GET"
                           ("./pull.cgi?p=" + ,pos
                            + (() ,file ? "&q=" + ,file |:| "&o=" + ,(config-get 'id)))
                           true) //))
                    (js-statement client ".send(null)")
                    (js-statement
                     "" client ".onreadystatechange = "
                     (js-function
                      ()
                      (js-if
                       "this.readyState == 4"
                       (js-if
                        "this.status == 200"
                        (js-let
                         ((doc "this.responseXML"))
                         (js-statement pos " = " doc ".getElementsByTagName (\"pos\")[0].firstChild.data")
                         (js-statement file " = " doc ".getElementsByTagName (\"file\")[0].firstChild.data")
                         
                         (js-for/defvar
                          ((e `(,doc ".getElementsByTagName (\"content\")[0].firstChild")))
                          (js-statement e)
                          (js-statement* e "=" e ".nextSibling")

                          (js-let
                           ((update-file
                             (js-function
                              (newfile)
                              (js-statement file "=" newfile)
                              (js-statement pos "=0")))
                            (x `("new D (" ,out "," ,update-file ")")))
                           (js-statement x ".evaluate (" e ")")
                           ))

                         (js-let
                          ((scrollY "window.pageYOffset || document.body.scrollTop")
                           (threshold "getDocHeight () - window.innerHeight * 1.5"))
                          #;(js-statement updatestat " (\"new pos = \" + " pos
                          " + \" file = \" + " file
                          " + \" scrollY = \" + " scrollY
                          " + \" threshold = \" + " threshold ")")
                         (js `((,updatestat -> ("last updated: " + ((((new Date) ->) .. toLocaleString) ->))) //))
                         (js-if
                          `(,initial " || " ,scrollY " > " ,threshold )
                          (js-statement initial " = false")
                          (js-statement "window.scrollTo (0, getDocHeight () - window.innerHeight)")
                          )

                         (js-statement "setTimeout (get_log, 100)")
                         )))
                      (js-else
                       (js-statement updatestat " (\"status = \" + this.status)")
                       (js-statement "setTimeout (get_log, 3000)")
                       )
                      )
                     ))
                   ))
                 (js-statement "get_log ()")
                 )))))))
          )

        ,(js-defun
          "sendtext" (d inputtext ul name mail text)
          (js-let
           ((chat_entry (js-call 'make_dom_element "\"chat-entry\""))
            (from (js-call 'make_dom_element "\"from\""))
            (user_by_nickname (js-call 'make_dom_element "\"user-by-nickname\""))
            (avatar_img (js-call 'make_dom_element "\"avatar-image\""))
            (string (js-call 'make_dom_element "\"string\""))
            (content (js-call 'make_dom_element "\"content\"")))

           (js-if `("!(" ,name " && " ,name ".length > 0)")
                  (js-statement name " = \"Anonymous\""))

           (js-let
            ((avatar_elem "null"))
            (js-if `(,mail " && " ,mail ".length > 0")
                   (js-statement avatar_elem " = " avatar_img " (" string " (\"http://www.gravatar.com/avatar/\""
                                 "+ hex_md5 (" mail ".toLowerCase ()) + \"?s=40&default=identicon\"))"))

            (js-let
             ((doc "document.implementation.createDocument (\"\", \"\", null)")
              (elem `("(" ,chat_entry " ({room:\"" ,(config-get 'id) "\"}," ,from " (" ,user_by_nickname " (" ,string " (" ,name ")),"
                      ,avatar_elem "),"
                      ,content " (" ,string " (" ,text ")))) (" ,doc ")")))

             (js-statement doc ".appendChild (" elem ")")

             (js-let
              ((client "new XMLHttpRequest()"))
              (js-statement client ".open(\"POST\", \"./push.cgi\")")
              (js-statement client ".setRequestHeader(\"Content-Type\", \"text/xml;charset=UTF-8\")")
              (js-statement client ".send(" doc ")")
              )))))

        ,(js-defun
          "make_dom_element" (tag)
          (js-let
           ((attrs "[]"))
           (js-for/defvar
            ((i "1"))
            (js-statement i "< arguments.length") (js-statement* i "++")
            (js-statement attrs ".push (arguments[" i "])"))

           (js-let
            ((dest (js-function
                    ()
                    (js-let
                     ((args "arguments")
                      (len "arguments.length"))

                     (js-statement
                      "return "
                      (js-function
                       (doc)
                       (js-let
                        ((e `(,doc ".createElement (" ,tag ")")))
                        (js-for/defvar
                         ((i "0"))
                         (js-statement i "<" len ) (js-statement* i "++")
                         (js-let
                          ((c `(,args "[" ,i "]")))
                          (js-if `(,c " == null") (js-statement "continue"))
                          (js-if `("typeof (" ,c ") == \"function\"")
                                 (js-statement e ".appendChild (" args "[" i "](" doc "))"))
                          (js-else-if `("typeof (" ,c ") == \"object\"")
                                      (js-for/iter (j -> c)
                                                   (js-statement e ".setAttribute (" j ", " c "[" j "])")))
                          (js-else
                           (js-let
                            ((t `(,doc ".createTextNode (" ,c ")")))
                            (js-statement e ".appendChild (" t ")")))
                          ))
                        (js-statement "return " e )
                        ))
                      )))
                   ))
            (js-statement "return" " " dest)
            )))

        ;; "// delay to prevent spin gear on Safari"
        ,(js-statement "setTimeout (initialize, 1)")
        )
  )

(define (main args)
  (write-tree
   `(,(cgi-header :content-type "text/javascript")
     ,(map (lambda (x) (list x "\n"))
           (script-body)))))
