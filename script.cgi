#!/usr/bin/env gosh
; -*- scheme -*-

(use www.cgi)
(use text.tree)

(define (js-statement . x) (list x ";"))
(define (js-statement* . x) x)
(define (js-if condition . body) (list "if(" condition "){" body "}"))
(define (js-else-if condition . body) (list "else" " " (apply js-if condition body)))
(define (js-else . body) (list "else{" body "}"))
(define (js-with obj . body) (list "with(" obj "){" body "}"))

(define-syntax js-let
  (syntax-rules ()
    ((_ (vars ...) body ...)
     (js-let-helper () (vars ...) body ...)
     )))

(define-syntax js-let-helper
  (syntax-rules ()
    ((_ ((var init) ...) () body ...)
     (let ((var (string-append "$" (symbol->string (gensym)))) ...)
       (list (js-multi-defver (var init) ...)
             body ...)))
    ((_ (part ...) ((var init) rest ...) body ...)
     (js-let-helper (part ... (var init)) (rest ...) body ...))
    ((_ (part ...) ((var) rest ...) body ...)
     (js-let-helper (part ... (var ())) (rest ...) body ...))
    ))

(define-syntax js-defvar-helper
  (syntax-rules ()
    ((_ var ())
     var)
    ((_ var init ...)
     (list var "=" init ...))
    ))

(define-syntax js-multi-defver
  (syntax-rules ()
    ((_ (var1 init1))
     (js-statement "var" " " (js-defvar-helper var1 init1)))
    ((_ (var1 init1) (rest-var rest-init) ...)
     (js-statement "var" " "
                   (js-defvar-helper var1 init1)
                   (list "," (js-defvar-helper rest-var rest-init)) ...))
    ))

(define-syntax js-join-with-comma
  (syntax-rules ()
    ((_) ())
    ((_ x) x)
    ((_ x rest ...) (list x (list "," rest) ...))
    ))

(define-syntax js-function
  (syntax-rules ()
    ((_ (var ...) body ...)
     (let ((var (string-append "$" (symbol->string (gensym)))) ...)
       (list "function" "(" (js-join-with-comma var ...) ")" "{"
             body ... "}")))
    ))

(define-syntax js-defun
  (syntax-rules ()
    ((_ name (var ...) body ...)
     (let ((var (string-append "$" (symbol->string (gensym)))) ...)
       (list "function" (if (null? name) () (list " " name)) "(" (js-join-with-comma var ...) ")" "{"
             body ... "}")))
    ))

(define-syntax js-for/defvar
  (syntax-rules ()
    ((_ ((var init) ...) condition succ body ...)
     (let ((var (string-append "$" (symbol->string (gensym)))) ...)
       (list "for" "("
             (js-multi-defver (var init) ...)
             condition
             succ ")" "{"
             body ... "}")
       )
     )
    ))

(define-syntax js-for/iter
  (syntax-rules (->)
    ((_ (x -> s) body ...)
     (let1 x (string-append "$" (symbol->string (gensym)))
       (list "for" "(" "var" " " x " " "in" " " s ")" "{" body ... "}")
     ))
    ))

(define (main args)
  (write-tree
   `(,(cgi-header :content-type "text/javascript")
     ,(map (lambda (x) (list x "\n"))
           `(,(js-statement
               "D = "
               (js-function
                (output update-file)
                (js-statement "this.state = {}")
                (js-statement "this.outtext = " (js-function (t) (js-statement output " (document.createTextNode (" t "))")))
                (js-statement "this.out = " output "")
                (js-statement "this.update_logfile = " update-file "")
                ))
             ,(js-statement
               ;(system (new-file ,newfile))
               "D.prototype.system="
               (js-function
                ()
                (js-statement "this.update_logfile(this.newfile)"))
               )
             ,(js-statement
               "D.prototype.new_file="
               (js-function
                (filename)
                (js-statement "this.newfile=" filename)))
             ,(js-statement
               "D.prototype.chat_entry = "
               (js-function
                ()
                (js-let
                 ((img "make_dom_element (\"img\")")
                  (p "make_dom_element (\"p\")")
                  (div "make_dom_element (\"div\")")
                  (br "make_dom_element (\"br\")")
                  (table "make_dom_element (\"table\")")
                  (td "make_dom_element (\"td\")")
                  (tr "make_dom_element (\"tr\")")
                  (span "make_dom_element (\"span\")")
                  (imgsrc "this.state.avatar_image")
                  (lines "this.state.content.split (/\\r*\\n/)")
                  (lines_with_br (list "[" lines "[0]]")))

                 (js-for/defvar
                  ((i "1"))
                  (js-statement i "<" lines ".length")
                  (js-statement* i "++")

                  (js-statement lines_with_br ".push (" br "())")
                  (js-statement lines_with_br ".push (" lines "[" i "])")
                  )

                 (js-statement
                  (js-let
                   ((e `("(" ,table "({style: \"width: 100%; max-width: 100ex\"},"
                         ,tr "({style: \"background-color: rgb(200, 200, 255)\"},"
                         ,td "({width: \"50\", height: \"40\", style: \"vertical-align: top\"},"
                         ,imgsrc "?" ,img "({src:" ,imgsrc "}) : null),"
                         ,td ".apply (this, [{style: \"vertical-align: top;\"},"
                         ,span "({style:\"font-weight: bold;\"}, this.state.nickname),"
			 ,span "({style:\"font-size:small;padding-left:3em\"}, this.state.date ? this.state.date.toLocaleString() : \"\"),"
                         ,br "()].concat (" ,lines_with_br "))"
                         "))) (document)")))
                   (js-statement "this.out (" e" )")))
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

                   (js-statement "return this[" func "].apply (this," args ")")
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
                 (tags "[\"h1\", \"h2\", \"ul\", \"li\", \"form\", \"input\", \"textarea\", \"div\", \"p\", \"br\", \"a\"]")
                 (env "{}"))

                (js-for/iter
                 (i -> tags)
                 (js-let ((t `(,tags "[" ,i "]")))
                         (js-statement env "[" t "] = make_dom_element (" t ")")
                         ))

                (js-with
                 env
                 (js-let ((head `("(h1 (\"Web chat\")) (" ,d ")")))
                         (js-statement b ".appendChild (" head ")")
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
                                         ))))

                  (js-let
                   ((form_elem) (nameinput) (mailinput) (inputtext))
                   (js-with
                    env
                    (js-statement nameinput " = input ({type: \"text\", size: \"20\"}) (" d ")")
                    (js-statement nameinput ".name = \"nameinput\"")
                    (js-statement mailinput " = input ({type: \"text\", size: \"50\"}) (" d ")")
                    (js-statement mailinput ".name = \"mailinput\"")
                    (js-statement inputtext " = textarea ({style: \"width:100%; max-width:100ex; height:10ex;\"}) (" d ")")
                    (js-statement form_elem " = (form (\"Nickname: \", ewrap (" nameinput "),"
                                  "\"Gravatar e-mail: \", ewrap (" mailinput "),"
                                  "a ({href: \"http://gravatar.com\"}, \"What's this?\"),"
                                  "br (), ewrap (" inputtext "),"
                                  "p (\"[TIPS] Press Shift+Enter to add a new line.  \","
                                  "a ({href: \"http://gravatar.com\"}, \"Get a Gravatar account to show your icon.\")),"
                                  "p (a ({href: \"http://github.com/torus/webchat\"}, \"Webchat project page.\"))"
                                  ")) (" d ")")

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
                          (js-if e (js-statement e ".value = unescape (" val ")"))
                          )))
                       ))
                     ))

                   (js-statement form_elem ".onsubmit = " (js-function () (js-statement "return false")))
                   (js-statement b ".appendChild (" form_elem ")")

                   (js-let
                    ((stat `(,d ".createElement (\"div\")"))
                     (statcont `(,d ".createElement (\"p\")"))
                     (stattext `(,d ".createTextNode (\"initiazelid.  waiting for data...\")")))
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
                        (js-let
                         ((text `(,inputtext ".value")))
                         (js-statement inputtext ".value = \"\"")
                         (js-statement "sendtext (" d ", " inputtext ", " ul ", " nameinput ".value, " mailinput ".value, " text ")")
                         (js-statement "return false")
                         )
                        )))

                     (js-let
                      ((initial "true")
                       (pos "0")
                       (file))
                      (js-defun
                       "get_log" ()
                       (js-let
                        ((client "new XMLHttpRequest()"))
                       (js-statement client
                                     ".open(\"GET\", \"./pull.cgi?p=\" + "
                                     pos "+ \"&q=\" + " file ", true)")
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
                             (js-statement updatestat " (\"new pos = \" + " pos
                                           " + \" file = \" + " file
                                           " + \" scrollY = \" + " scrollY
                                           " + \" threshold = \" + " threshold ")")
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
                ((chat_entry "make_dom_element (\"chat-entry\")")
                 (from "make_dom_element (\"from\")")
                 (user_by_nickname "make_dom_element (\"user-by-nickname\")")
                 (avatar_img "make_dom_element (\"avatar-image\")")
                 (string "make_dom_element (\"string\")")
                 (content "make_dom_element (\"content\")"))

                (js-if `("!(" ,name " && " ,name ".length > 0)")
                       (js-statement name " = \"Anonymous\""))

                (js-let
                 ((avatar_elem "null"))
                 (js-if `(,mail " && " ,mail ".length > 0")
                        (js-statement avatar_elem " = " avatar_img " (" string " (\"http://www.gravatar.com/avatar/\""
                                      "+ hex_md5 (" mail ".toLowerCase ()) + \"?s=40\"))"))

                 (js-let
                  ((doc "document.implementation.createDocument (\"\", \"\", null)")
                   (elem `("(" ,chat_entry " (" ,from " (" ,user_by_nickname " (" ,string " (" ,name ")),"
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
     ))
  )