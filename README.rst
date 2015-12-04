shotwell2blog
=============

Export tagged photos from a Shotwell photo database to a target
filesystem or list them in different ways.

The files are always sorted by exposure_time.

Command-line options::

    usage: shotwell2blog.py [-h] [-t TARGET_ROOT] [-l SHOTWELL_LIB]
                            [-d SHOTWELL_DB] [-s] [-b BEFORE] [-a AFTER]
                            [tags [tags ...]]

    positional arguments:
      tags                  One ore more Shotwell tags. The listed pictures must
                            have *at least* one of them. (default: -)

    optional arguments:
      -h, --help            show this help message and exit
      -t TARGET_ROOT, --target_root TARGET_ROOT
                            Where to export tagged pictures and videos. (default:
                            -)
      -l SHOTWELL_LIB, --shotwell_lib SHOTWELL_LIB
                            Your Shotwell library directory (default:
                            u'/home/luc/Pictures/')
      -d SHOTWELL_DB, --shotwell_db SHOTWELL_DB
                            Your Shotwell database file (default:
                            u'/home/luc/.local/share/shotwell/data/photo.db')
      -s, --sigal_image     Output as sigal_image directives (default: False)
      -b BEFORE, --before BEFORE
                            Select photos taken before that time (default: -)
      -a AFTER, --after AFTER
                            Select photos taken after that time (default: -)


**Usage examples:**

List the file names of all photos tagged "foo"::

  $ shotwell2blog.py foo

Copy all photos marked "blog" to a directory `~/myblog/pictures`.
Maintain subdirectories.  Don't touch existing photos::

  $ shotwell2blog.py -t ~/myblog/pictures blog

Create a zip file with a copy of each photo tagged "Foo" (the `-j`
option is to *not* include directory names)::

  $ shotwell2blog.py Foo | xargs zip -j foo.zip

Create a zip file with all photos tagged Foo and taken after 2015-01-01::

  $ shotwell2blog.py -a 2015-01-01 Foo | grep -v AÜ | xargs zip Foo2015.zip

**TODO**

- Export also videos

