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

(define (read-from-log file pos)
  (let ((pos (or pos 0))
        (file (get-or-prepare-log-file)))
    (let ((port (open-input-file file)))
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
                    (values (reverse part) file pos)))
              (if (> count 30)
                  (values () file pos)
                  (begin
                    (sys-sleep 1)
                    (wait-loop (+ count 1))))))))))
