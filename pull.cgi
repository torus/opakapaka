#!/usr/bin/env gosh
; -*- scheme -*-

(use sxml.serializer)
(use www.cgi)
(use file.util)

(load "./file")

(define (main args)
  (frontend read-from-log pull-filter))

(define (frontend reader filter)
  (cgi-main
   (lambda (params)
     (let ((last-pos (let1 p (cgi-get-parameter "p" params)
                       (and p (string->number p))))
           (log-file (cgi-get-parameter "q" params)))
       `(,(cgi-header :content-type "text/xml")
         ,(srl:sxml->xml-noindent
           (receive (exps file pos) (reader log-file last-pos)
             `(*TOP* (res (pos ,pos)
                          (file ,file)
                          (content ,@(filter exps)))))))))))

(define (pull-filter x) x)
