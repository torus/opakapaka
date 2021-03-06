#!/usr/bin/env gosh
; -*- scheme -*-

(use sxml.serializer)
(use www.cgi)
(use file.util)
(use util.list)

(load "./file")

(define (main args)
  (frontend read-from-log-no-wait archive-filter))	

(define (frontend reader filter)
  (cgi-main
   (lambda (params)
     (let ((log-file (cgi-get-parameter "q" params)))
       `(,(cgi-header :content-type "text/html;charset=utf-8")
         ,(srl:sxml->xml-noindent
	   (if log-file
	       (receive (exps file pos) (reader log-file 0)
			`(*TOP* (html (head (title "log " ,file))
				      (script "function init (x) {if (n = location.href.match(/#(.+)$/)) {document.getElementById('e'+n[1]).style.backgroundColor='#ffcccc'}}")
				      (body
				       (@ (onload "init()"))
				       (ul ,@(filter exps))))))
	       `(*TOP* (html (head (title "log archive"))
			     (body (ul
				    ,@(map (lambda (f) `(li (a (@ (href ,#`"./archive.cgi?q=,f")) ,f))) (log-files))))))
	       )))))))

(define (archive-filter exps)
  (map (lambda (x)
	 (guard (e (else (ref e 'message)))
		(eval x (interaction-environment))))
       exps))

;;;;;;;;;;;;;

; (chat-entry
;  (link (file "data/data.1234567890.1234.log") (pos 123))
;  (date (posix-time 1253048216))
;  (from (user-by-nickname (string "とおる。"))
;        (avatar-image (string "http://www.gravatar.com/avatar/5efc507a8db7167e2db7889a5597a3cd?s=40&default=identicon")))
;  (content (string "あれ、名前がない。")))

(define (chat-entry . params)
  (let ((data (fold (lambda (x p)
		      (if x (cons x p) p))
		    () params)))
    `(li (@ (id ,(string-append "e" (cdr (assoc 'pos data)))))
	 (a (@ (name ,(cdr (assoc 'pos data))))
	    ,(cdr (assoc 'name data)))
	 (span (@ (style "padding-left: 10ex;font-size: small"))
	       (a (@ (href ,(string-append "#" (cdr (assoc 'pos data))))) ,(cdr (assoc 'date data))))
	 (br)
	 ,@(cdr (assoc 'content data)))
  ))
(define (link file p) (cons 'pos p))
(define (file x) x)
(define (pos p) (x->string p))
(define (date x) (cons 'date (sys-ctime x)))
(define (posix-time x) (x->number x))
(define (from . params)
  (let loop ((params params))
    (if (car params)
	(cons 'name (car params))
	(loop (cdr params)))))
(define (user-by-nickname x) x)
(define (string x) x)
(define (avatar-image x) #f)
(define (content x) (cons 'content (intersperse '(br) (string-split x #\newline))))
(define (system x) #f)
(define (new-file x) #f)
(define (room x) #f)
(define (|@| x) #f)
