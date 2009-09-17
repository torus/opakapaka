(use srfi-1)
(use file.util)

(define *link* "current")
(define *data-dir* "data")
(define *max-file-size* 10000)

(define (log-files)
  (let ((lst (directory-list *data-dir* :add-path? #t)))
    (filter #/.log$/ lst)
  ))

(define (create-new-file)
  (if (file-exists? *data-dir*)
      (if (file-is-directory? *data-dir*)
          (let1 path (build-path *data-dir*
                                 (string-append "data."
                                                (x->string (sys-time)) "."
                                                (x->string (sys-getpid)) ".log"))
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

(define (read-from-log file pos)
  (let ((pos (or pos 0))
        (file (or file (get-or-prepare-log-file))))
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
