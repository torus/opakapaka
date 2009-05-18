#!/usr/local/bin/gosh
; -*- scheme -*-

(use sxml.serializer)
(use www.cgi)

(define (main args)
  (cgi-main
   (lambda (params)
     (let ((last-pos (string->number (or (cgi-get-parameter "p" params) "0"))))
       `(,(cgi-header :content-type "text/xml")
         ,(srl:sxml->xml-noindent
           (receive (exps pos) (read-from-log last-pos)
             `(*TOP* (res (pos ,pos)
                          (content ,@exps))))))))))

(define (read-from-log pos)
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
                  (ret (reverse part) pos)))
            (if (> count 30)
                (ret () pos)
                (begin
                  (sys-sleep 1)
                  (wait-loop (+ count 1)))))))))
