shotwell2blog
=============

Export tagged photos and videos from Shotwell photo database
to a target filesystem or list them in different ways.

The files are always sorted by exposure_time.

Usage examples:

List the file names of all photos tagged "foo"::

  $ shotwell2blog.py foo

Copy all photos marked "blog" to a directory `~/myblog/pictures`.
Maintain subdirectories.  Don't touch existing photos::

  $ shotwell2blog.py -t ~/myblog/pictures blog

Create a zip file with a copy of each photo tagged "Foo" (the `-j`
option is to *not* include directory names)::

  $ shotwell2blog.py Foo | xargs zip -j foo.zip

