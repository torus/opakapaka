(with-input-from-file "script.js"
  (lambda ()
    (call/cc
     (lambda (last)
       (let loop ()
         (write (let1 line (read-line)
                  (if (eof-object? line)
                      (last)
                      line)))
         (newline)
         (loop)
         )
       ))))
