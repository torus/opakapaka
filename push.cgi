#!/usr/bin/env gosh
; -*- scheme -*-

(use gauche.fcntl)
(use file.util)
(use sxml.ssax)
(use www.cgi)
(use text.tree)
(use util.match)

(load "./file")

(define (with-output-to-locked-port port thunk)
  (sys-fcntl port F_SETLKW (make <sys-flock> :type F_WRLCK))
  (with-output-to-port port thunk)
  (sys-fcntl port F_SETLK (make <sys-flock> :type F_UNLCK))
  )

(define (push-filter x)
  (match x
	 (`(chat-entry . ,content)
	  `(chat-entry
	    (date (posix-time ,(sys-time)))
	    . ,content))))

(define (cgi-writer outport . doc)
  (with-output-to-locked-port
   outport
   (lambda ()
     (for-each (lambda (e)
                 (newline)              ; First, write a newline
                 (write e)) ; Then, add a item so that the file always ends with ")"
               doc)
     ))
  )

(define (frontend writer)
  (let* ((port (current-input-port))
         (doc (ssax:xml->sxml port ()))
	 (file (get-or-prepare-log-file))
         (out (open-output-file file :if-exists :append))
	 (pos (port-seek out 0 SEEK_END)))
    (let ((doc (push-filter (cadr doc))))
      (if (> pos *max-file-size*)
	  (let1 newfile (create-new-file)
		(sys-unlink *link*)
		(sys-symlink newfile *link*)
		(writer out doc `(system (new-file (string ,newfile)))))
	  (writer out doc)
	  )))
  (write-tree
   `(,(cgi-header))))

(define (main args)
  (frontend cgi-writer))
