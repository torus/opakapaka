

;; function call
;; (func -> a b c) //  -> func (a, b, c);
;; 
;; (a = b) -> a = b
;; (a * b + c) -> a * b + c
;; (this .. state = {}) -> this.state = {}

;; for (var i in obj) { func (obj[i]); a ++; }
;; (for (var i in obj) (func -> obj <> i) // (a ++) //)

(define-module js
  (export js))
(select-module js)

(use util.match)

(define (join delim lst)
  (if (null? lst)
      ""
      (if (null? (cdr lst))
          (car lst)
          #`",(car lst),delim,(join delim (cdr lst))")))

(define (js code)
  (match code
         ('var "var ")
         ('in " in ")
         ('return "return ")
         ('// ";")
         ('.. ".")
         ((? symbol? sym) (symbol->string sym))
         ((? number? num) (number->string num))
         ((? string? str) #`"\",str\"")
         (`(,func -> ,args ...)
          #`",(js func)(,(join \",\" (map js args)))")
         ((() x ...)
          (js `(|(| ,x |)|)))
         (`(<> ,x ...)
          #`"[,(js x)]")
         (`(^^ ,pairs ...)
          (string-append "{"
                         (join "," (map (lambda (p)
                                          (js `(,(car p) |:| ,(cadr p)))
                                          ) pairs)) "}"))
         (`(if (,condition ...) ,body ...)
          #`"if,(js `((() ,condition) |{| ,body |}|))")
         (`(for (,stmt ...) ,body ...)
          #`"for,(js `((() ,stmt) |{| ,body |}|))")
         (`(while (,expr ...) ,body ...)
          #`"while,(js `((() ,expr) |{| ,body |}|))")
         (`(function ,(? symbol? name) (,args ...) ,body ...)
          #`"function ,name(,(join \",\" args)){,(js body)}")
         (`(function (,args ...) ,body ...)
          #`"function(,(join \",\" args)){,(js body)}")
         ((terms ...)
          (apply string-append (map js terms)))
         ))
