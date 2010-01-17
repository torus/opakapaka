(define-module push-filter)
(select-module push-filter)

(use srfi-1)
(use util.digest)
(use rfc.md5)

(define (get-tags doc)
      (let ((tag (car doc))
            (cont (cdr doc)))
        (cons tag
              (let loop ((cont cont))
                (if (null? cont)
                    ()
                    (let ((h (car cont)))
                      (if (pair? h)
                          (append (get-tags h)
                                  (loop (cdr cont)))
                          (loop (cdr cont)))))))))

(define (eval-child params)
  (lambda (x)
    (if (procedure? x)
        (x params)
        x)))

(define-syntax null-tag
  (syntax-rules ()
    ((_ tag)
     (define (tag . args)
       (lambda (params) `(tag ,@(map (eval-child params) args)))))))

(define-syntax define-null-tags
  (syntax-rules ()
    ((_ x ...)
     (begin (null-tag x) ...))))

(define (identicon-url ip-addr)
  (string-append "http://www.gravatar.com/avatar/"
                 (digest-hexify (md5-digest-string ip-addr))
                 "?s=40&default=identicon")
  )

(define (from . args)
  (lambda (params)
    (let ((children (map (eval-child params) args)))
      (if (assoc 'avatar-image children)
          `(from ,@children)
          `(from ,@children (avatar-image (string ,(identicon-url (cadr (assoc 'src-addr params))))))))))

(define-null-tags chat-entry link file pos date posix-time |@| room
  avatar-image user-by-nickname content string)

;; test
(select-module user)
(define (main args)
  (define data
    '(chat-entry
      (link (file "data/data.1234567890.1234.log") (pos 123))
      (date (posix-time 1253048216))
      (from (user-by-nickname (string "とおる。"))
            )
      (content (string "あれ、名前がない。"))))

  (define data2
    '(chat-entry
      (link (file "data/data.1234567890.1234.log") (pos 123))
      (date (posix-time 1253048216))
      (from (user-by-nickname (string "とおる。"))
            (avatar-image (string "http://www.gravatar.com/avatar/5efc507a8db7167e2db7889a5597a3cd?s=40&default=identicon"))
            )
      (content (string "あれ、名前がない。"))))

  (write ((eval data (find-module 'push-filter)) '((src-addr "1.2.4.5")))) (newline)
  (write ((eval data2 (find-module 'push-filter)) '((src-addr "1.2.4.5")))) (newline)

  )
