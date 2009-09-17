#!/usr/bin/env gosh
; -*- scheme -*-

(use sxml.serializer)
(use www.cgi)
(use file.util)
(use util.list)

(load "./file")

(define (main args)
  (frontend read-from-log archive-filter))	

(define (frontend reader filter)
  (cgi-main
   (lambda (params)
     (let ((log-file (cgi-get-parameter "q" params)))
       `(,(cgi-header :content-type "text/html;charset=utf-8")
         ,(srl:sxml->xml-noindent
           (receive (exps file pos) (reader log-file 0)
             `(*TOP* (html (head (title "log " ,file))
			   (body
			    (ul ,@(filter exps))))))))))))

(define (archive-filter exps)
  (map (lambda (x)
	 (guard (e (else (ref e 'message)))
		(eval x (interaction-environment))))
       exps))

;;;;;;;;;;;;;

; (chat-entry
;  (date (posix-time 1253048216))
;  (from (user-by-nickname (string "とおる。"))
;        (avatar-image (string "http://www.gravatar.com/avatar/5efc507a8db7167e2db7889a5597a3cd?s=40&default=identicon")))
;  (content (string "あれ、名前がない。")))

(define (chat-entry . params)
  (let ((data (fold (lambda (x p)
		      (if x (cons x p) p))
		    () params)))
    `(li ,(cdr (assoc 'name data)) ": " (br) ,@(cdr (assoc 'content data)))
  ))

(define (date x) #f)
(define (posix-time x) #f)
(define (from . params)
  (let loop ((params params))
    (if (car params)
	(cons 'name (car params))
	(loop (cdr params)))))
(define (user-by-nickname x) x)
(define (string x) x)
(define (avatar-image x) #f)
(define (content x) (cons 'content (intersperse '(br) (string-split x #\newline))))
