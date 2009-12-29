OPAKAPAKA
=========

A tiny Ajax and comet-based chat system implemented in Scheme.
Visit the [project page on github.com](http://github.com/torus/opakapaka).

REQUIREMENTS
------------

- Gauche 0.8.13 or later
- Apache or lighttpd with CGI support
- Git (for downloading)

DOWNLOAD
--------

 git clone git://github.com/torus/opakapaka.git

SETUP
-----

- chmod +x *.cgi
- Set permission of this directory so that the HTTP daemon can create
  a data directory and log files.
- Access index.html from web browser.

When you access index.html for the first time, a data diretory and a
new log file will be generated automatically.

CONFIGURATION
-------------

Edit opakapaka.conf.cgi.

LICENSE
-------

Same as Gauche (BSD license).

AUTHOR
------

Toru Hisai &lt;toru at torus dot jp&gt;

Enjoy!
