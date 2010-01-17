#!/usr/bin/env gosh
; -*- scheme -*-

(use gauche.fcntl)
(use file.util)
(use sxml.ssax)
(use www.cgi)
(use text.tree)
(use util.match)

(add-load-path ".")

(load "file")
(load "push-filter")
(load "config")

(load "opakapaka.conf.cgi")

(define (with-output-to-locked-port port thunk)
  (sys-fcntl port F_SETLKW (make <sys-flock> :type F_WRLCK))
  (with-output-to-port port thunk)
  (sys-fcntl port F_SETLK (make <sys-flock> :type F_UNLCK))
  )

(define (add-date doc)
  (match doc
	 (`(chat-entry . ,content)
	  `(chat-entry
	    (date (posix-time ,(sys-time)))
	    . ,content))))

(define (push-filter x)
  (let ((addr (or (cgi-get-metavariable "REMOTE_ADDR") "?")))
    (add-date ((eval x (find-module 'push-filter)) `((src-addr ,addr))))))

(define (cgi-writer outport . doc)
  (for-each (lambda (e)
	      (newline)              ; First, write a newline
	      (write e)) ; Then, add a item so that the file always ends with ")"
	    doc))

(define (get-output-file-from-post doc)
  (let1 attr (make-hash-table)
    (match doc
      (`(chat-entry (@ (,key ,val) ...) ,_ ...)
       (map (lambda (k v) (hash-table-put! attr k v)) key val)))
    (hash-table-get attr 'room)))

(define (frontend writer)
  (let* ((port (current-input-port))
         (doc (ssax:xml->sxml port ()))
         (curlink (get-output-file-from-post (cadr doc))))
    (parameterize ((current-link curlink))
      (let* ((file (get-or-prepare-log-file))
             (out (open-output-file file :if-exists :append)))
        (with-output-to-locked-port
         out
         (lambda ()
           (let ((pos (port-seek out 0 SEEK_END))
                 (doc (push-filter (cadr doc))))
             (if (> pos (max-file-size))
                 (let1 newfile (create-new-file)
		   (sys-unlink (current-link))
		   (sys-symlink newfile (current-link))
		   (writer out doc `(system (new-file (string ,newfile)))))
                 (writer out doc)
                 )))))))
  (write-tree
   `(,(cgi-header))))

(define (main args)
  (frontend cgi-writer))
