(define-module config-module
  (define (title t) (cons 'title t))
  (define (max-file-size t) (cons 'max-file-size t))
  )

(define-macro opakapaka-config
  (lambda procs
    `(define *config-alist*
       (let1 mod (find-module 'config-module)
         (list
          ,@(map (lambda (p)
                   `(eval ',p mod)) procs))))))

(define (config-get key)
  (cdr (assoc key *config-alist*)))
