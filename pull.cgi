#!/usr/local/bin/gosh
; -*- scheme -*-

(use sxml.serializer)
(use www.cgi)

(define (main args)
  (frontend read-from-log pull-filter))

(define (frontend reader filter)
  (cgi-main
   (lambda (params)
     (let ((last-pos (let1 p (cgi-get-parameter "p" params) (and p (string->number p)))))
       `(,(cgi-header :content-type "text/xml")
         ,(srl:sxml->xml-noindent
           (receive (exps pos) (reader last-pos)
             `(*TOP* (res (pos ,pos)
                          (content ,@(filter exps)))))))))))

(define (pull-filter x) x)

(define (read-from-log pos)
  (let ((pos (or pos 0)))
    (let ((port (open-input-file "data.log")))
      (let wait-loop ((count 0))
        (let ((end (port-seek port 0 SEEK_END)))
          (if (> end pos)
              (let loop ((pos pos)
                         (part ()))
                (if (> end pos)
                    (begin
                      (port-seek port pos)
                      (let ((exp (read port)))
                        (loop (port-tell port) (cons exp part))))
                    (values (reverse part) pos)))
              (if (> count 30)
                  (values () pos)
                  (begin
                    (sys-sleep 1)
                    (wait-loop (+ count 1))))))))))
