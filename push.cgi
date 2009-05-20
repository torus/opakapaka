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

(define (main args)
  (let* ((port (current-input-port))
         (doc (ssax:xml->sxml port ())))
    (let ((out (open-output-file "data.log" :if-exists :append))
          (doc (push-filter (cadr doc))))
      (with-output-to-locked-port out
         (lambda ()
           (newline)                    ; First, write a newline
           (write doc) ; Then, add a item so that the file always end with ")"
           ))))
  (write-tree
   `(,(cgi-header))))
