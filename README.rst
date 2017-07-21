==================
The picsel project
==================

This currently consists of two Python scripts :file:`shotwell2blog.py`
and :file:`digikam2blog.py`.

Both scripts copy tagged photos from a Shotwell or DigiKam photo
database to a target filesystem. Alternatively they can also simply
list their filenames in different ways instead of copying the files.

I use to have all my photos in a single DigiKam photo database. When I
want to share a photo, then I tag it with a given name (e.g. "blog").
And after closing DigiKam, I run a `make` process which copies those
pictures to a cache directory and then uses rsync to publish them to
an internet server.


**Usage examples:**

(Replace xxx by shotwell or digipḱam.)

List the file names of all photos tagged "foo"::

  $ xxx2blog.py foo

Copy all photos marked "blog" to a directory `~/myblog/pictures`.
Maintain subdirectories.  Don't touch existing photos::

  $ xxx2blog.py -t ~/myblog/pictures blog

Create a zip file with a copy of each photo tagged "Foo" (the `-j`
option is to *not* include directory names)::

  $ xxx2blog.py Foo | xargs zip -j foo.zip

Create a zip file with all photos tagged Foo and taken after
2015-01-01, expect those with "AÜ" in their name::

  $ xxx2blog.py -a 2015-01-01 Foo | grep -v AÜ | xargs zip Foo2015.zip

**TODO**

- Export also videos

