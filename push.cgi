#!/usr/local/bin/gosh
; -*- scheme -*-

(use gauche.fcntl)
(use file.util)
(use sxml.ssax)
(use www.cgi)
(use text.tree)

(define (lock port)
  (sys-fcntl port F_SETLKW (make <sys-flock> :type F_WRLCK))
  )

(define (unlock port)
  (sys-fcntl port F_SETLK (make <sys-flock> :type F_UNLCK))
  )


(define (main args)
  (let* ((port (current-input-port))
         (doc (ssax:xml->sxml port ())))
    (let ((out (open-output-file "data.log" :if-exists :append)))
      (lock out)
      (newline out)                  ; First, write a newline
      (write (cadr doc) out) ; Then, add a item so that the file always end with ")"
      (unlock out)
      ))
  (write-tree
   `(,(cgi-header))
   )
  )
