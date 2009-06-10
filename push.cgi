#!/usr/local/bin/gosh
; -*- scheme -*-

(use gauche.fcntl)
(use file.util)
(use sxml.ssax)
(use www.cgi)
(use text.tree)

(define (with-output-to-locked-port port thunk)
  (sys-fcntl port F_SETLKW (make <sys-flock> :type F_WRLCK))
  (with-output-to-port port thunk)
  (sys-fcntl port F_SETLK (make <sys-flock> :type F_UNLCK))
  )

(define (push-filter x) x)

(define (cgi-writer outport doc)
  (with-output-to-locked-port
   outport
   (lambda ()
     (newline)                    ; First, write a newline
     (write doc) ; Then, add a item so that the file always end with ")"
     ))
  )

(define (frontend writer)
  (let* ((port (current-input-port))
         (doc (ssax:xml->sxml port ())))
    (let ((out (open-output-file "data.log" :if-exists :append))
          (doc (push-filter (cadr doc))))
      (writer out doc)))
  (write-tree
   `(,(cgi-header))))

(define (main args)
  (frontend cgi-writer))
