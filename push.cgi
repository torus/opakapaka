#!/usr/bin/env gosh
; -*- scheme -*-

(use gauche.fcntl)
(use sxml.ssax)
(use www.cgi)

(define (lock port)
  (sys-fcntl port F_SETLKW (make <sys-flock> :type F_WRLCK))
  )

(define (unlock port)
  (sys-fcntl port F_SETLK (make <sys-flock> :type F_UNLCK))
  )


(define (main args)
  (cgi-main
   (lambda (params)
     (let* ((port (current-input-port))
	    (doc (ssax:xml->sxml (open-input-string (cgi-get-parameter "doc" params)) ())))
       (let ((out (open-output-file "data" :if-exists :append)))
	 (lock out)
	 (newline out)			; First, write a newline
	 (write (cadr doc) out) ; Then, add a item so that the file always end with ")"
	 (unlock out)
	 ))
     )))
