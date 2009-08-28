(define *link* "current")
(define *data-dir* "data")
(define *max-file-size* 200)

(define (create-new-file)
  (if (file-exists? *data-dir*)
      (if (file-is-directory? *data-dir*)
          (let1 path (build-path *data-dir*
                                 (string-append "data."
                                                (x->string (sys-time)) "."
                                                (x->string (sys-getpid))))
            (touch-file path)
            path)
          (error #`",*data-dir* is not a direcotry."))
      (begin (make-directory* *data-dir*)
             (create-new-file))))

(define (get-or-prepare-log-file)
  (if (file-exists? *link*)
      (if (file-is-symlink? *link*)
          (sys-readlink *link*)
          (error #`",*link* is not a symlink."))
      (let1 file (create-new-file)
        (sys-symlink file *link*)
        file)))
