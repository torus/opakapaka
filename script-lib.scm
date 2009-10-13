(define (js-statement . x) (list x ";"))
(define (js-statement* . x) x)
(define (js-if condition . body) (list "if(" condition "){" body "}"))
(define (js-else-if condition . body) (list "else" " " (apply js-if condition body)))
(define (js-else . body) (list "else{" body "}"))
(define (js-with obj . body) (list "with(" obj "){" body "}"))

(define-syntax js-let
  (syntax-rules ()
    ((_ (vars ...) body ...)
     (js-let-helper () (vars ...) body ...)
     )))

(define-syntax js-let-helper
  (syntax-rules ()
    ((_ ((var init) ...) () body ...)
     (let ((var (string-append "$" (symbol->string (gensym)))) ...)
       (list (js-multi-defver (var init) ...)
             body ...)))
    ((_ (part ...) ((var init) rest ...) body ...)
     (js-let-helper (part ... (var init)) (rest ...) body ...))
    ((_ (part ...) ((var) rest ...) body ...)
     (js-let-helper (part ... (var ())) (rest ...) body ...))
    ))

(define-syntax js-defvar-helper
  (syntax-rules ()
    ((_ var ())
     var)
    ((_ var init ...)
     (list var "=" init ...))
    ))

(define-syntax js-multi-defver
  (syntax-rules ()
    ((_ (var1 init1))
     (js-statement "var" " " (js-defvar-helper var1 init1)))
    ((_ (var1 init1) (rest-var rest-init) ...)
     (js-statement "var" " "
                   (js-defvar-helper var1 init1)
                   (list "," (js-defvar-helper rest-var rest-init)) ...))
    ))

(define-syntax js-join-with-comma
  (syntax-rules ()
    ((_) ())
    ((_ x) x)
    ((_ x rest ...) (list x (list "," rest) ...))
    ))

(define-syntax js-function
  (syntax-rules ()
    ((_ (var ...) body ...)
     (let ((var (string-append "$" (symbol->string (gensym)))) ...)
       (list "function" "(" (js-join-with-comma var ...) ")" "{"
             body ... "}")))
    ))

(define-syntax js-defun
  (syntax-rules ()
    ((_ name (var ...) body ...)
     (let ((var (string-append "$" (symbol->string (gensym)))) ...)
       (list "function" (if (null? name) () (list " " name)) "(" (js-join-with-comma var ...) ")" "{"
             body ... "}")))
    ))

(define-syntax js-for/defvar
  (syntax-rules ()
    ((_ ((var init) ...) condition succ body ...)
     (let ((var (string-append "$" (symbol->string (gensym)))) ...)
       (list "for" "("
             (js-multi-defver (var init) ...)
             condition
             succ ")" "{"
             body ... "}")
       )
     )
    ))

(define-syntax js-for/iter
  (syntax-rules (->)
    ((_ (x -> s) body ...)
     (let1 x (string-append "$" (symbol->string (gensym)))
       (list "for" "(" "var" " " x " " "in" " " s ")" "{" body ... "}")
     ))
    ))

(define-syntax js-call
  (syntax-rules ()
    ((_ func args ...)
     (string-append (x->string func) "(" (x->string args) ... ")"))))

(define-syntax js-.
  (syntax-rules ()
    ((_ first rest ...)
     (fold (lambda (a b) (string-append b "." a))
           (symbol->string 'first)
           (list (symbol->string 'rest) ...)))))

(define-syntax define-tag
  (syntax-rules ()
    ((_ (name args ...) body ...)
     (js-statement
      "D.prototype." name "="
      (js-function (args ...) body ...)
      ))))
