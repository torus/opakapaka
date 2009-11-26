

;; function call
;; (func -> a b c) //  -> func (a, b, c);
;; 
;; (a = b) -> a = b
;; (a * b + c) -> a * b + c
;; (this .. state = {}) -> this.state = {}

;; for (var i in obj) { func (obj[i]); a ++; }
;; (for (var i in obj) (func -> obj <> i) // (a ++) //)

(use util.match)

(define (join delim lst)
  (if (null? (cdr lst))
      (car lst)
      #`",(car lst),delim,(join delim (cdr lst))"))

(define (js code)
  (match code
         ('var "var ")
         ('in " in ")
         ('// ";")
         ((? symbol? sym) (symbol->string sym))
         ((? number? num) (number->string num))
         ((? string? str) #`"\",str\"")
         (`(,func -> ,args ...)
          #`",(js func)(,(join \",\" (map js args)))")
         ((() x ...)
          (js `(|(| ,x |)|)))
         (`(<> ,x ...)
          #`"[,(js x)]")
         (`(for (,stmt ...) ,body ...)
          #`"for,(js `((() ,stmt) |{| ,body |}|))")
         (`(while (,expr ...) ,body ...)
          #`"while,(js `((() ,expr) |{| ,body |}|))")
         ((terms ...)
          (apply string-append (map js terms)))
         ))


(use gauche.test)

(test* "join" "a,b,c" (join "," '(a b c)))
(test* "string" "\"hello\"" (js "hello"))
(test* "var" "var x" (js '(var x)))
(test* "var init" "var x=100;" (js '(var x = 100 //)))
(test* "unary" "a" (js 'a))
(test* "unary operator" "+a" (js '(+ a)))
(test* "binary operator" "a+b" (js '(a + b)))
(test* "paren" "(a)" (js '(() a)))
(test* "paren" "a*(b+c)" (js '(a * (() b + c))))
(test* "square bracket" "[x]" (js '(<> x)))
(test* "array access" "arr[i]" (js '(arr (<> i))))
(test* "array literal" "var x=[]" (js '(var x = (<>))))
(test* "funcall" "func(a,b,c)" (js '(func -> a b c)))
(test* "funcall statement" "func(a,b,c);" (js '((func -> a b c) //)))
(test* "for" "for(var i=0;i<5;i++){func(i);}" (js '(for (var i = 0 // i < 5 // i ++) (func -> i) //)))
(test* "for-in" "for(var i in obj){func(i);}" (js '(for (var i in obj) (func -> i) //)))
(test* "while" "while(x>10){func(x);}" (js '(while (x > 10) (func -> x) //)))
